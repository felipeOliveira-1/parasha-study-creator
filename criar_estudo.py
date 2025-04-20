import requests
import json
import subprocess
import sys
import time

MCP_URL = "http://localhost:8000/"


def is_mcp_running():
    try:
        requests.get(MCP_URL, timeout=2)
        return True
    except Exception:
        return False

def start_mcp_server():
    print("Iniciando servidor MCP em background...")
    # Inicia o servidor MCP em background
    subprocess.Popen([sys.executable, "mcp_server.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Aguarda até o servidor estar disponível
    for _ in range(20):
        if is_mcp_running():
            return True
        time.sleep(0.5)
    return False

def main():
    print("=== Gerador de Estudos de Parashot ===")
    parasha = input("Digite o nome da porção (ex: Shemini): ").strip()
    if not parasha:
        print("Porção não informada. Encerrando.")
        return
    if not is_mcp_running():
        if not start_mcp_server():
            print("❌ Não foi possível iniciar o servidor MCP.")
            return
    print(f"Gerando estudo para: {parasha} ...")
    body = {
        "tool": "generate_parasha_study_ptbr",
        "args": {"parasha": parasha}
    }
    try:
        resp = requests.post(MCP_URL, json=body, timeout=120)
        data = resp.json()
        if data.get("success"):
            print(f"✅ Estudo criado com sucesso: {data['file']}")
        else:
            print("❌ Erro ao criar estudo:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    main()
