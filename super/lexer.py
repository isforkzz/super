import re

TOKEN_SPEC = [
    # comentários
    ("COMMENT_ML", r"/\$[\s\S]*?\$/"),   # /$ ... $/
    ("COMMENT_SL", r"//[^\n]*"),          # // ...

    # keywords
    ("ASYNC",      r"\basync\b"),
    ("AWAIT",      r"\bawait\b"),
    ("GLOBAL",     r"\bglobal\b"),
    ("EXPORT",     r"\bexport\b"),
    ("IMPORT",     r"\bimport\b"),
    ("FROM",       r"\bfrom\b"),
    ("AS",         r"\bas\b"),
    ("PAGE",       r"\bpage\b"),
    ("CLASS",      r"\bclass\b"),
    ("EXTENDS",    r"\bextends\b"),
    ("SUPER",      r"\bsuper\b"),
    ("NEW",        r"\bnew\b"),
    ("THIS",       r"\bthis\b"),
    ("INTERFACE",  r"\binterface\b"),
    ("ENUM",       r"\benum\b"),
    ("TYPE",       r"\btype\b"),
    ("DECORATOR",  r"\bDecorator\b"),
    ("PUBLIC",     r"\bpublic\b"),
    ("PRIVATE",    r"\bprivate\b"),
    ("FUNCTION",   r"\bfunction\b"),
    ("RETURN",     r"\breturn\b"),
    ("IF",         r"\bif\b"),
    ("ELSE",       r"\belse\b"),
    ("FOR",        r"\bfor\b"),
    ("WHILE",      r"\bwhile\b"),
    ("BREAK",      r"\bbreak\b"),
    ("CONTINUE",   r"\bcontinue\b"),
    ("MATCH",      r"\bmatch\b"),
    ("CASE",       r"\bcase\b"),
    ("DEFAULT",    r"\bdefault\b"),
    ("TRY",        r"\btry\b"),
    ("EXCEPT",     r"\bexcept\b"),
    ("THROW",      r"\bthrow\b"),
    ("DELETE",     r"\bdelete\b"),
    ("TYPEOF",     r"\btypeof\b"),
    ("EXISTS",     r"\bexists\b"),
    ("IN",         r"\bin\b"),
    ("OF",         r"\bof\b"),
    ("IS",         r"\bis\b"),
    ("NOT",        r"\bnot\b"),
    ("AND",        r"\band\b"),
    ("OR",         r"\bor\b"),
    ("NULL",       r"\bnull\b"),
    ("UNDEFINED",  r"\bundefined\b"),
    ("BOOL_LIT",   r"\b(true|false)\b"),
    ("VARTYPE",    r"\b(int|float|str|string|bool|boolean|number|array|void)\b"),
    ("KEYWORD",    r"\b(const|var|let)\b"),

    # literais
    ("TEMPLATE",   r'f"[^"]*"'),
    ("NUMBER",     r"\d+(\.\d+)?"),
    ("STRING",     r'"[^"]*"|\'[^\']*\''),
    ("ID",         r"[a-zA-Z_][a-zA-Z0-9_]*"),

    # operadores
    ("NULLISH",    r"\?\?"),
    ("OPTIONAL",   r"\?\."),
    ("ARROW",      r"=>"),
    ("SPREAD",     r"\.\.\."),
    ("POW_EQ",     r"\*\*="),
    ("MUL_EQ",     r"\*="),
    ("DIV_EQ",     r"/="),
    ("MOD_EQ",     r"%="),
    ("ADD_EQ",     r"\+="),
    ("SUB_EQ",     r"-="),
    ("POW",        r"\*\*"),
    ("GTE",        r">="),
    ("LTE",        r"<="),
    ("EQ",         r"=="),
    ("NEQ",        r"!="),
    ("GT",         r">"),
    ("LT",         r"<"),
    ("TERNARY",    r"\?"),
    ("PIPE",       r"\|"),
    ("AT",         r"@"),
    ("PLUS",       r"\+"),
    ("MINUS",      r"-"),
    ("STAR",       r"\*"),
    ("SLASH",      r"/"),
    ("PERCENT",    r"%"),
    ("EQUALS",     r"="),
    ("BANG",       r"!"),

    # delimitadores
    ("LBRACE",     r"\{"),
    ("RBRACE",     r"\}"),
    ("LBRACKET",   r"\["),
    ("RBRACKET",   r"\]"),
    ("LPAREN",     r"\("),
    ("RPAREN",     r"\)"),
    ("SEMICOL",    r";"),
    ("COMMA",      r","),
    ("COLON",      r":"),
    ("DOT",        r"\."),

    ("SKIP",       r"[ \t]+"),
    ("NEWLINE",    r"\n"),
    ("MISMATCH",   r"."),
]

VARTYPE_ALIASES = {
    "str": "str", "string": "str",
    "int": "int", "number": "int",
    "float": "float",
    "bool": "bool", "boolean": "bool",
    "array": "array",
    "void": "void",
}

TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


def tokenize(code: str) -> list:
    tokens = []
    for m in TOKEN_RE.finditer(code):
        kind  = m.lastgroup
        value = m.group()
        if kind in ("SKIP", "NEWLINE", "SEMICOL", "COMMENT_SL", "COMMENT_ML"):
            continue
        if kind == "MISMATCH":
            raise SyntaxError(f"[SSL] Caractere inesperado: '{value}'")
        tokens.append((kind, value))
    return tokens
