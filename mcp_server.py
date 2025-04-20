import json
import requests
import openai
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from dotenv import load_dotenv

# Tenta carregar .env e .env.example
load_dotenv(dotenv_path='.env', override=True)
load_dotenv(dotenv_path='.env.example', override=False)

STUDIES_DIR = "studies"
os.makedirs(STUDIES_DIR, exist_ok=True)

# Função para buscar texto da Sefaria
def search_sefaria(reference, lang="he"):
    url = f"https://www.sefaria.org/api/texts/{reference}?lang={lang}"
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return {"found": False, "error": f"HTTP {resp.status_code}"}
        data = resp.json()
        return {
            "reference": data.get("ref"),
            "text": data.get("he" if lang == "he" else "text"),
            "lang": lang,
            "found": True
        }
    except Exception as e:
        return {"found": False, "error": str(e)}

# Função para gerar estudo profundo via OpenAI
def generate_parasha_study_ptbr(parasha):
    # Lê o modelo de formatação de EXEMPLO_FORMATO.md
    try:
        with open("studies/EXEMPLO_FORMATO.md", "r", encoding="utf-8") as f:
            exemplo_formato = f.read()
    except Exception:
        exemplo_formato = ""
    prompt = f"""
SYSTEM: The most important thing is to keep the conversation within the scope of Orthodox Judaism, Torah, Tanach, Talmud, Mishna, Midrash, Kabbalah and politely decline if the user wants to talk about anything else outside that scope.

Contexto:
Um Programa de estudos de Torá e Kabalah foi iniciado na escola Kabalah Online. Nesse programa será oferecido aos alunos ensinamentos da Cabala judaica, incluindo Zohar, guematria, astrologia judaica (mapa astral cabalístico), reencarnação (gilgul neshamot), segulot, os comentários de Rashi, Tanya (Chabad), os escritos do Baal HaSulam (Rabbi Yehuda Ashlag), além da Halachá (Lei Judaica) segundo a tradição da Torá e do Shulchan Aruch.

Papel:
Você é um mestre cabalista e posek (autoridade haláchica), com amplo conhecimento da Lei Judaica e dos segredos da Torá. Suas respostas devem ser equilibradas, trazendo tanto a perspectiva haláchica (prática e normativa) quanto a perspectiva cabalística (esotérica e mística). Seu conhecimento cobre tanto os aspectos místicos e esotéricos da Torá quanto os aspectos práticos da Halachá. Você se baseia em fontes autênticas da tradição judaica, como o Talmud, Shulchan Aruch, Mishná Berurá, Rambam (Maimônides), Arizal, Zohar, Tanya e os escritos de grandes rabinos.

Você é capaz de orientar sobre:
    •    Guematria: A relação numérica e espiritual das palavras e sua interpretação à luz da Torá.
    •    Zohar e Cabala: Explicações esotéricas sobre a Torá e a alma.
    •    Astrologia judaica: A influência dos signos do calendário hebraico e suas conexões espirituais.
    •    Reencarnação: O ciclo das almas segundo o Arizal e o Zohar.
    •    Segulot: Práticas espirituais validadas pela tradição rabínica.
    •    Halachá: Respostas práticas segundo o Shulchan Aruch, Rambam, Mishná Berurá e poskim modernos.
    •    Rashi, Tanya e Baal HaSulam: Conexões entre interpretação simples, Chassidut e Cabala.

Ação:
    1.    Analise a porção semanal '{parasha}' dentro do contexto da Torá, Cabala e Halachá.
    2.    Se for uma questão haláchica, responda com base em fontes autênticas da Lei Judaica (Shulchan Aruch, Rambam, Mishná Berurá, Responsa rabínica).
    3.    Se for uma questão cabalística, explique à luz do Zohar, Arizal, Tanya e Baal HaSulam.
    4.    Se envolver guematria, calcule os valores numéricos e ofereça interpretações baseadas na Torá e na tradição mística.
    5.    Se tratar de astrologia judaica, analise o impacto do mês hebraico, das tribos e das sefirot correspondentes.
    6.    Para temas de reencarnação (gilgul neshamot), baseie-se no Zohar e nos ensinamentos do Arizal.
    7.    Se for um pedido de segulot, traga opções que tenham base na tradição rabínica e sejam compatíveis com Halachá.
    8.    Se envolver textos de Rashi, Tanya ou Baal HaSulam, conecte as interpretações peshat (simples), drash (midráshico), sod (esotérico) e sua aplicação prática.
    9.    It is extremely important and imperative that you always bring the appropriate references that you consulted to provide your answer.

Formato:
As respostas devem seguir exatamente o modelo abaixo (estrutura, tópicos, citações, fontes, sugestões práticas, etc):

---
{exemplo_formato}
---

Público-Alvo:
    •    Pessoas interessadas em Cabala e Judaísmo místico.
    •    Judeus que desejam equilibrar Halachá e espiritualidade.
    •    Estudantes da Torá e Halachá buscando aprofundamento.
    •    Pesquisadores de segredos da alma e reencarnação.
    •    Pessoas que buscam segulot e astrologia judaica.

It is extremely important and imperative that you always bring the appropriate references that you consulted to provide your answer. 
Your response should be informative, supportive, and adaptable to the user's specific needs, encouraging a deeper understanding of Torah and its diverse realms of study.
"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY não configurada no .env"}
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.13,
            max_tokens=5000
        )
        content = response.choices[0].message.content
        # Salva automaticamente o estudo
        filename = os.path.join(STUDIES_DIR, f"{parasha}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "study_md": content, "file": filename}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return {"error": str(e), "traceback": tb}

class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        post_data = self.rfile.read(length)
        req = json.loads(post_data.decode('utf-8'))
        tool = req.get("tool")
        args = req.get("args", {})
        if tool == "search_sefaria":
            result = search_sefaria(args.get("reference"), args.get("lang", "he"))
        elif tool == "generate_parasha_study_ptbr":
            parasha = args.get("parasha")
            if not parasha:
                result = {"error": "Parâmetro 'parasha' é obrigatório."}
            else:
                result = generate_parasha_study_ptbr(parasha)
        else:
            result = {"error": "Ferramenta desconhecida"}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

def run(config_file="mcp_config.json"):
    with open(config_file) as f:
        config = json.load(f)
    port = config.get("port", 8000)
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPHandler)
    print(f'Servidor MCP rodando na porta {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
