import sys
import os
import json
import argparse

VERSION = "1.0.0"
SUPER_JSON = "super.json"


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def load_super_json(path: str = ".") -> dict:
    config_path = os.path.join(path, SUPER_JSON)
    if not os.path.exists(config_path):
        print(f"[SSL] Erro: '{SUPER_JSON}' não encontrado em '{path}'")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_file(filepath: str, args: dict = {}):
    if not os.path.exists(filepath):
        print(f"[SSL] Erro: arquivo '{filepath}' não encontrado")
        sys.exit(1)

    if not filepath.endswith(".ssl"):
        print(f"[SSL] Aviso: '{filepath}' não tem extensão .ssl")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    from .interpreter import run
    run(code, args=args)


# ─────────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────────

def cmd_init(yes: bool = False):
    """runner init [-y]"""
    if os.path.exists(SUPER_JSON) and not yes:
        resp = input(f"[SSL] Arquivo (super.json) já existe, deseja subscrever? (s/n)")
        if resp.lower() != "s":
            print("Cancelado pelo usuário")
            return

    config = {
        "main": "main.ssl",
        "scripts": {},
        "packages": {},
        "type": "default"
    }

    with open(SUPER_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    # cria main.ssl se não existir
    if not os.path.exists("main.ssl"):
        pass

def cmd_run_dot(extra_args: dict = {}):
    """runner . → lê main do super.json e roda"""
    config = load_super_json()
    main_file = config.get("main", "main.ssl")
    print(f"[SSL] Rodando '{main_file}'...")
    run_file(main_file, args=extra_args)


def cmd_run_file(filepath: str, extra_args: dict = {}):
    """runner main.ssl → roda o arquivo direto"""
    print(f"[SSL] Rodando '{filepath}'...")
    run_file(filepath, args=extra_args)


def cmd_execute(script_name: str):
    """runner execute <script> → roda script do super.json"""
    config = load_super_json()
    scripts = config.get("scripts", {})

    if script_name not in scripts:
        print(f"[SSL] Erro: script '{script_name}' não encontrado em '{SUPER_JSON}'")
        print(f"[SSL] Scripts disponíveis: {list(scripts.keys()) or 'nenhum'}")
        sys.exit(1)

    script_file = scripts[script_name]
    print(f"[SSL] Executando script '{script_name}' → '{script_file}'...")
    run_file(script_file)


def cmd_version():
    """runner version"""
    print(f"SuperStaticLanguage Runner v{VERSION}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        print("SuperStaticLanguage Runner")
        print(f"  v{VERSION}\n")
        print("Uso:")
        print("  runner init [-y]          Cria super.json")
        print("  runner .                  Roda o main do super.json")
        print("  runner <arquivo.ssl>      Roda um arquivo .ssl")
        print("  runner execute <script>   Executa um script do super.json")
        print("  runner version            Mostra a versão")
        return

    # extrai flags extras --key=value (para uso futuro)
    extra_args = {}
    clean_args = []
    for arg in args:
        if arg.startswith("--") and "=" in arg:
            key, val = arg[2:].split("=", 1)
            extra_args[key] = val
        else:
            clean_args.append(arg)

    cmd = clean_args[0] if clean_args else ""

    if cmd == "init":
        yes = "-y" in clean_args
        cmd_init(yes=yes)

    elif cmd == ".":
        cmd_run_dot(extra_args=extra_args)

    elif cmd == "version":
        cmd_version()

    elif cmd == "execute":
        if len(clean_args) < 2:
            print("[SSL] Uso: runner execute <script>")
            sys.exit(1)
        cmd_execute(clean_args[1])

    elif cmd.endswith(".ssl"):
        cmd_run_file(cmd, extra_args=extra_args)

    else:
        print(f"[SSL] Comando desconhecido: '{cmd}'")
        print("[SSL] Use 'runner' sem argumentos para ver os comandos.")
        sys.exit(1)
