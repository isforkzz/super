import asyncio
import re


class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

class SSLError(Exception): pass


class SSLClass:
    def __init__(self, name, members, parent=None):
        self.name    = name
        self.members = members
        self.parent  = parent

class SSLInstance:
    def __init__(self, cls: SSLClass, props: dict, interpreter):
        self.cls         = cls
        self.props       = props
        self._interp     = interpreter
        self._decorators = {}
        # registra decorators definidos na classe
        for m in cls.members:
            if isinstance(m, dict) and m.get("node") == "DecoratorDef":
                self._decorators[m["name"]] = m

    def get(self, key, default=None):
        if isinstance(key, str) and key in self.props:
            val = self.props[key]
            if isinstance(default, dict) and isinstance(val, dict):
                return SSLInstance.__wrap(val, self._interp)
            return val
        return default

    def __repr__(self):
        return f"<{self.cls.name} {self.props}>"


class Interpreter:
    def __init__(self, extra=None):
        self.env     = {"console": {"__console__": True, "log": None, "warn": None, "error": None, "info": None}}          # variáveis globais
        self.globals = {}          # global const/function
        self.types   = {}          # interfaces / type aliases / enums
        self.exports = {}          # exports do arquivo
        self.page    = None        # export page as "..."
        self.extra   = extra or {} # args CLI --key=val

    # ── RUN ──────────────────────────────────

    def run(self, nodes: list, env=None):
        scope = env if env is not None else self.env
        for node in nodes:
            self.exec(node, scope)

    # ── EXEC ─────────────────────────────────

    def exec(self, node, scope):
        if not isinstance(node, dict):
            return
        kind = node.get("node")

        if kind == "VarDecl":     return self.exec_var(node, scope)
        if kind == "FuncDecl":    return self.exec_func_decl(node, scope)
        if kind == "ClassDecl":   return self.exec_class(node, scope)
        if kind == "Interface":   return self.exec_interface(node)
        if kind == "Enum":        return self.exec_enum(node, scope)
        if kind == "TypeAlias":   return self.exec_type_alias(node)
        if kind == "Return":      raise ReturnSignal(self.eval(node["value"], scope))
        if kind == "Break":       raise BreakSignal()
        if kind == "Continue":    raise ContinueSignal()
        if kind == "If":          return self.exec_if(node, scope)
        if kind == "For":         return self.exec_for(node, scope)
        if kind == "While":       return self.exec_while(node, scope)
        if kind == "Match":       return self.exec_match(node, scope)
        if kind == "Try":         return self.exec_try(node, scope)
        if kind == "Throw":       raise SSLError(self.eval(node["value"], scope))
        if kind == "Delete":      return self.exec_delete(node, scope)
        if kind == "IIFE":        return self.exec_iife(node, scope)
        if kind == "Decorated":   return self.exec_decorated(node, scope)
        if kind == "ExportPage":  self.page = node["alias"]; return
        if kind == "Import":      return self.exec_import(node, scope)
        if kind == "ExprStmt":    return self.eval(node["expr"], scope)
        if kind == "AugAssign":   return self.exec_aug_assign(node, scope)

    # ── VAR ──────────────────────────────────

    def exec_var(self, node, scope):
        value = self.eval(node["value"], scope)
        tipo  = node.get("type")
        if tipo and tipo != "void":
            value = self.cast(value, tipo, node["name"])
        target = self.globals if node.get("global") else scope
        target[node["name"]] = value
        if node.get("export"):
            self.exports[node["name"]] = value

    # ── FUNCTION ─────────────────────────────

    def exec_func_decl(self, node, scope):
        target = self.globals if node.get("global") else scope
        target[node["name"]] = node
        if node.get("export"):
            self.exports[node["name"]] = node

    # ── CLASS ────────────────────────────────

    def exec_class(self, node, scope):
        parent = scope.get(node["parent"]) if node["parent"] else None
        cls = SSLClass(node["name"], node["members"], parent)
        scope[node["name"]] = cls

    # ── INTERFACE ────────────────────────────

    def exec_interface(self, node):
        self.types[node["name"]] = {"kind": "interface", "fields": node["fields"]}

    # ── ENUM ─────────────────────────────────

    def exec_enum(self, node, scope):
        enum_obj = {v: v for v in node["values"]}
        scope[node["name"]] = enum_obj

    # ── TYPE ALIAS ───────────────────────────

    def exec_type_alias(self, node):
        self.types[node["name"]] = {"kind": "type", "values": node["values"]}

    # ── IF ───────────────────────────────────

    def exec_if(self, node, scope):
        if self.eval(node["condition"], scope):
            self.run(node["body"], scope)
        elif node["else"]:
            self.run(node["else"], scope)

    # ── FOR ──────────────────────────────────

    def exec_for(self, node, scope):
        iterable = self.eval(node["iterable"], scope)
        for item in iterable:
            local = {**scope, node["var"]: item}
            try:
                self.run(node["body"], local)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    # ── WHILE ────────────────────────────────

    def exec_while(self, node, scope):
        while self.eval(node["condition"], scope):
            try:
                self.run(node["body"], scope)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    # ── MATCH ────────────────────────────────

    def exec_match(self, node, scope):
        value = self.eval(node["value"], scope)
        for case in node["cases"]:
            if self.eval(case["value"], scope) == value:
                self.run(case["body"], scope)
                return
        if node["default"]:
            self.run(node["default"], scope)

    # ── TRY/EXCEPT ───────────────────────────

    def exec_try(self, node, scope):
        try:
            self.run(node["body"], scope)
        except Exception as e:
            for exc in node["excepts"]:
                err_name = exc["error"]
                local = {**scope, err_name: str(e)}
                self.run(exc["body"], local)
                return

    # ── DELETE ───────────────────────────────

    def exec_delete(self, node, scope):
        target = node["target"]
        if isinstance(target, dict) and target.get("node") == "PropAccess":
            obj = self.eval(target["target"], scope)
            if isinstance(obj, dict):
                obj.pop(target["prop"], None)
            elif isinstance(obj, SSLInstance):
                obj.props.pop(target["prop"], None)

    # ── AUG ASSIGN ───────────────────────────

    def exec_aug_assign(self, node, scope):
        name  = node["target"].get("ref")
        left  = self.eval(node["target"], scope)
        right = self.eval(node["value"], scope)
        ops   = {"+": lambda a,b: a+b, "-": lambda a,b: a-b,
                 "*": lambda a,b: a*b, "/": lambda a,b: a/b,
                 "%": lambda a,b: a%b, "**": lambda a,b: a**b}
        result = ops[node["op"]](left, right)
        if name:
            scope[name] = result
        return result

    # ── IIFE ─────────────────────────────────

    def exec_iife(self, node, scope):
        func = node["func"]
        args = [self.eval(a, scope) for a in node["args"]]
        return self.call_func(func, args, scope)

    # ── DECORATED ────────────────────────────

    def exec_decorated(self, node, scope):
        chain = node["chain"]
        args  = [self.eval(a, scope) for a in node["args"]]
        # resolve o decorator
        obj = scope.get(chain[0]) or self.globals.get(chain[0])
        for part in chain[1:]:
            if isinstance(obj, dict):
                obj = obj.get(part)
            elif isinstance(obj, SSLInstance):
                obj = obj.props.get(part) or obj._decorators.get(part)
        # registra a função decorada
        target = node["target"]
        self.exec(target, scope)
        if target.get("node") == "FuncDecl":
            func = scope.get(target["name"])
            if callable(obj):
                obj(func, *args)
        return

    # ── IMPORT ───────────────────────────────

    def exec_import(self, node, scope):
        import os
        path = node["path"]
        # resolve page alias
        if not path.endswith(".ssl"):
            path = path.replace(".", "/") + ".ssl"
        if not os.path.exists(path):
            print(f"[SSL] Aviso: import '{node['path']}' não encontrado")
            return
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        from .lexer import tokenize
        from .parser import Parser
        tokens  = tokenize(code)
        ast     = Parser(tokens).parse()
        sub     = Interpreter()
        sub.run(ast)
        if node["kind"] == "all":
            scope.update(sub.exports)
        else:
            for name in node["names"]:
                if name in sub.exports:
                    scope[name] = sub.exports[name]
                else:
                    print(f"[SSL] Aviso: '{name}' não exportado em '{node['path']}'")

    # ── EVAL ─────────────────────────────────

    def eval(self, node, scope):
        if node is None:
            return None
        if not isinstance(node, dict):
            return node

        kind = node.get("node")

        if "ref" in node:
            name = node["ref"]
            if name in scope:         return scope[name]
            if name in self.globals:  return self.globals[name]
            if name in self.env:      return self.env[name]
            raise NameError(f"[SSL] '{name}' não definido")

        if kind == "Undefined":   return None
        if kind == "Array":       return self.eval_array(node, scope)
        if kind == "Object":      return {k: self.eval(v, scope) for k, v in node["pairs"].items()}
        if kind == "Template":    return self.eval_template(node["raw"], scope)
        if kind == "BinOp":       return self.eval_binop(node, scope)
        if kind == "Unary":       return self.eval_unary(node, scope)
        if kind == "Is":          return self.eval_is(node, scope)
        if kind == "Nullish":     return self.eval_nullish(node, scope)
        if kind == "Ternary":     return self.eval(node["then"] if self.eval(node["condition"], scope) else node["else"], scope)
        if kind == "Await":       return self.eval_await(node, scope)
        if kind == "Call":        return self.eval_call(node, scope)
        if kind == "MethodCall":  return self.eval_method(node, scope)
        if kind == "PropAccess":  return self.eval_prop(node, scope)
        if kind == "OptionalChain": return self.eval_optional(node, scope)
        if kind == "New":         return self.eval_new(node, scope)
        if kind == "This":        return scope.get("__this__")
        if kind == "Typeof":      return self.eval_typeof(node, scope)
        if kind == "Exists":      return self.eval_exists(node, scope)
        if kind == "Spread":      return self.eval(node["value"], scope)
        if kind in ("ArrowFunc", "FuncDecl"): return node

        return node

    def eval_array(self, node, scope):
        result = []
        for e in node["elements"]:
            val = self.eval(e, scope)
            if isinstance(e, dict) and e.get("node") == "Spread":
                if isinstance(val, list):
                    result.extend(val)
                continue
            result.append(val)
        return result

    def eval_template(self, raw: str, scope):
        def replacer(m):
            expr = m.group(1)
            from .lexer import tokenize
            from .parser import Parser
            tokens = tokenize(expr)
            ast    = Parser(tokens).parse_expr()
            return str(self.eval(ast, scope))
        return re.sub(r'\$\{([^}]+)\}', replacer, raw)

    def eval_binop(self, node, scope):
        l = self.eval(node["left"], scope)
        r = self.eval(node["right"], scope)
        op = node["op"]
        if op == "+":   return l + r
        if op == "-":   return l - r
        if op == "*":   return l * r
        if op == "/":   return l / r
        if op == "%":   return l % r
        if op == "**":  return l ** r
        if op == "==":  return l == r
        if op == "!=":  return l != r
        if op == ">":   return l > r
        if op == "<":   return l < r
        if op == ">=":  return l >= r
        if op == "<=":  return l <= r
        if op == "and": return l and r
        if op == "or":  return l or r
        raise ValueError(f"[SSL] Operador desconhecido: {op}")

    def eval_unary(self, node, scope):
        v = self.eval(node["value"], scope)
        if node["op"] == "!":  return not v
        if node["op"] == "-":  return -v

    def eval_is(self, node, scope):
        l = self.eval(node["left"], scope)
        r = node["right"]
        # is tipo
        if isinstance(r, dict) and r.get("node") == "VARTYPE":
            tipo = r["value"]
        elif isinstance(r, dict) and "ref" in r:
            tipo = r["ref"]
        else:
            tipo = self.eval(r, scope)

        type_map = {"str": str, "string": str, "int": int, "number": int,
                    "float": float, "bool": bool, "boolean": bool, "array": list}
        if tipo in type_map:
            result = isinstance(l, type_map[tipo])
        else:
            result = l == tipo

        return not result if node["negate"] else result

    def eval_nullish(self, node, scope):
        l = self.eval(node["left"], scope)
        return l if l is not None else self.eval(node["right"], scope)

    def eval_await(self, node, scope):
        val = self.eval(node["value"], scope)
        if asyncio.iscoroutine(val):
            return asyncio.get_event_loop().run_until_complete(val)
        return val

    def eval_call(self, node, scope):
        name = node["name"]
        args = [self.eval(a, scope) for a in node["args"]]

        # builtins
        if name == "print":
            print(*args)
            return
        if name == "range":
            return list(range(*[int(a) for a in args]))
        if name == "exists":
            return args[0] is not None

        # console
        if name == "console":
            return

        func = scope.get(name) or self.globals.get(name)
        if not func:
            raise NameError(f"[SSL] Função '{name}' não definida")
        return self.call_func(func, args, scope)

    def eval_method(self, node, scope):
        target = self.eval(node["target"], scope)
        method = node["method"]
        args   = [self.eval(a, scope) for a in node["args"]]

        # console.log/warn/error/info
        if isinstance(target, dict) and "__console__" in target:
            print(*args)
            return

        # string
        if isinstance(target, str):
            if method == "length":    return len(target)
            if method == "toUpper":   return target.upper()
            if method == "toLower":   return target.lower()
            if method == "trim":      return target.strip()
            if method == "replace":   return target.replace(args[0], args[1])
            if method == "toString":  return str(target)
            if method == "parseInt":  return int(target)
            if method == "parseFloat": return float(target)
            if method == "includes":  return args[0] in target
            if method == "slice":     return target[args[0]:args[1]]
            raise AttributeError(f"[SSL] string.{method} não existe")

        # number
        if isinstance(target, (int, float)):
            if method == "toString":   return str(target)
            if method == "toFixed":    return round(float(target), args[0] if args else 2)
            if method == "parseInt":   return int(target)
            if method == "parseFloat": return float(target)
            raise AttributeError(f"[SSL] number.{method} não existe")

        # array
        if isinstance(target, list):
            if method == "length":   return len(target)
            if method == "push":     target.append(args[0]); return target
            if method == "pop":      return target.pop()
            if method == "includes": return args[0] in target
            if method == "slice":    return target[args[0]:args[1]]
            if method == "get":
                idx = args[0]
                return target[idx] if isinstance(idx, int) and 0 <= idx < len(target) else (args[1] if len(args) > 1 else None)
            if method in ("map", "filter", "find"):
                lam  = node["args"][0]
                results = []
                for item in target:
                    local = {**scope}
                    if isinstance(lam, dict) and lam.get("node") == "ArrowFunc":
                        param = lam["params"][0]["name"] if lam["params"] else "_"
                        local[param] = item
                        try:
                            self.run(lam["body"], local)
                        except ReturnSignal as r:
                            results.append((item, r.value))
                            continue
                        results.append((item, None))
                    elif isinstance(lam, dict) and lam.get("node") == "Lambda":
                        local[lam["param"]] = item
                        results.append((item, self.eval(lam["body"], local)))
                if method == "map":    return [r for _, r in results]
                if method == "filter": return [i for i, r in results if r]
                if method == "find":
                    for i, r in results:
                        if r: return i
                    return None
            raise AttributeError(f"[SSL] array.{method} não existe")

        # dict/object
        if isinstance(target, dict):
            if method == "get":
                key = args[0]
                default = args[1] if len(args) > 1 else None
                return target.get(key, default)

        # SSLInstance
        if isinstance(target, SSLInstance):
            if method in target.props:
                val = target.props[method]
                if isinstance(val, dict) and val.get("node") in ("FuncDecl", "ArrowFunc"):
                    return self.call_func(val, args, {**scope, "__this__": target})
                return val
            if method == "get":
                return target.get(args[0], args[1] if len(args) > 1 else None)
            raise AttributeError(f"[SSL] {target.cls.name}.{method} não existe")

        raise TypeError(f"[SSL] Tipo '{type(target).__name__}' não suporta métodos")

    def eval_prop(self, node, scope):
        target = self.eval(node["target"], scope)
        prop   = node["prop"]

        if isinstance(target, dict):
            # console object
            if prop in ("log", "warn", "error", "info"):
                return {"__console__": True}
            return target.get(prop)
        if isinstance(target, list):
            if prop == "length": return len(target)
        if isinstance(target, SSLInstance):
            if prop in target.props:
                return target.props[prop]
            for m in target.cls.members:
                if isinstance(m, dict) and m.get("name") == prop:
                    if m.get("node") == "FuncDecl":
                        return m
            return None
        if isinstance(target, SSLClass):
            # acesso a decorator da classe
            for m in target.members:
                if isinstance(m, dict) and m.get("name") == prop:
                    return m
        return None

    def eval_optional(self, node, scope):
        target = self.eval(node["target"], scope)
        if target is None:
            return None
        prop = node["prop"]
        if isinstance(target, dict):
            return target.get(prop)
        if isinstance(target, SSLInstance):
            return target.props.get(prop)
        return None

    def eval_new(self, node, scope):
        cls_val = scope.get(node["class"]) or self.globals.get(node["class"])
        if not isinstance(cls_val, SSLClass):
            raise TypeError(f"[SSL] '{node['class']}' não é uma classe")
        args  = [self.eval(a, scope) for a in node["args"]]
        props = {}
        # propriedades da classe
        for m in cls_val.members:
            if isinstance(m, dict) and m.get("node") == "Property":
                props[m["name"]] = None
        instance = SSLInstance(cls_val, props, self)
        # chama constructor
        for m in cls_val.members:
            if isinstance(m, dict) and m.get("node") == "Constructor":
                local = {**scope, "__this__": instance}
                for i, p in enumerate(m["params"]):
                    local[p["name"]] = args[i] if i < len(args) else None
                try:
                    self.run(m["body"], local)
                except ReturnSignal:
                    pass
                break
        # registra métodos
        for m in cls_val.members:
            if isinstance(m, dict) and m.get("node") == "FuncDecl":
                instance.props[m["name"]] = m
        return instance

    def eval_typeof(self, node, scope):
        val = self.eval(node["value"], scope)
        if isinstance(val, bool):    return "bool"
        if isinstance(val, int):     return "int"
        if isinstance(val, float):   return "float"
        if isinstance(val, str):     return "string"
        if isinstance(val, list):    return "array"
        if isinstance(val, dict):    return "object"
        if isinstance(val, SSLInstance): return val.cls.name
        return "undefined"

    def eval_exists(self, node, scope):
        try:
            val = self.eval(node["value"], scope)
            return val is not None
        except NameError:
            return False

    def eval_typeof(self, node, scope):
        val = self.eval(node["value"], scope)
        if isinstance(val, bool):        return "bool"
        if isinstance(val, int):         return "int"
        if isinstance(val, float):       return "float"
        if isinstance(val, str):         return "string"
        if isinstance(val, list):        return "array"
        if isinstance(val, SSLInstance): return val.cls.name
        if isinstance(val, dict):        return "object"
        return "undefined"

    # ── CALL FUNC ────────────────────────────

    def call_func(self, func, args, scope):
        if not isinstance(func, dict):
            raise TypeError(f"[SSL] Não é uma função: {func}")
        params = func.get("params", [])
        body   = func.get("body", [])
        local  = {**scope}
        for i, p in enumerate(params):
            local[p["name"]] = args[i] if i < len(args) else None
        try:
            self.run(body, local)
        except ReturnSignal as r:
            return r.value
        return None

    # ── CAST ─────────────────────────────────

    def cast(self, value, tipo, name):
        tipo_real = type(value).__name__
        aceitos = {
            "int":   (int,),
            "float": (float, int),
            "str":   (str,),
            "bool":  (bool,),
            "array": (list,),
        }
        if not isinstance(value, aceitos.get(tipo, (object,))):
            raise TypeError(f"[SSL] Erro de tipo: '{name}' esperava {tipo}, recebeu {tipo_real}")
        if tipo == "float" and isinstance(value, int):
            return float(value)
        return value
