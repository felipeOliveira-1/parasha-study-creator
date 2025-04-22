import json
import os
import openai
import requests
import json
import re
import unicodedata
from difflib import get_close_matches
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

print("[DEBUG] MCP_SERVER.PY INICIADO")

load_dotenv()
load_dotenv(dotenv_path='.env', override=True)
load_dotenv(dotenv_path='.env.example', override=False)

# Garante que a pasta studies sempre será a da raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIES_DIR = os.path.join(BASE_DIR, "studies")
os.makedirs(STUDIES_DIR, exist_ok=True)

import unicodedata
from difflib import get_close_matches

SEFARIA_BOOKS_CACHE = None

def extract_titles_from_contents(contents):
    books = []
    for item in contents:
        if "title" in item:
            books.append(item["title"])
        if "titleVariants" in item:
            books.extend(item["titleVariants"])
        if "contents" in item and isinstance(item["contents"], list):
            books.extend(extract_titles_from_contents(item["contents"]))
    return books

def get_sefaria_books():
    global SEFARIA_BOOKS_CACHE
    if SEFARIA_BOOKS_CACHE is not None:
        return SEFARIA_BOOKS_CACHE
    url = "https://www.sefaria.org/api/index"
    try:
        response = requests.get(url)
        print(f"[DEBUG] Status code da API Sefaria: {response.status_code}")
        print(f"[DEBUG] Conteúdo bruto da resposta (primeiros 500 chars): {response.text[:500]}")
        if response.status_code == 200:
            data = response.json()
            books = extract_titles_from_contents(data)
            SEFARIA_BOOKS_CACHE = list(set(books))
            return SEFARIA_BOOKS_CACHE
        else:
            print("[DEBUG] Falha ao buscar lista de tratados do Sefaria.")
            return []
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar livros do Sefaria: {e}")
        return []

def normalize_str(s):
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace(' ', '').replace('.', '')
    return s

def match_sefaria_book(user_input):
    books = get_sefaria_books()
    print(f"[DEBUG] Primeiros 20 tratados retornados pelo Sefaria: {books[:20]}")
    norm_books = {normalize_str(b): b for b in books}
    user_norm = normalize_str(user_input)
    print(f"[DEBUG] user_input normalizado: {user_norm}")
    if user_norm in norm_books:
        print(f"[DEBUG] Match exato encontrado: {norm_books[user_norm]}")
        return norm_books[user_norm], None
    # Fuzzy match
    close = get_close_matches(user_norm, norm_books.keys(), n=10, cutoff=0.7)
    suggestions = [norm_books[c] for c in close]
    print(f"[DEBUG] Sugestões fuzzy para '{user_input}': {suggestions}")
    return None, suggestions

# Função para buscar texto da Sefaria

def generate_daf_yomi_summary(daf_yomi):
    print("[DEBUG] Entrou na função generate_daf_yomi_summary")
    try:
        # === INÍCIO DO CÓDIGO ORIGINAL ===
        match = re.match(r"([A-Za-záéíóúãõâêôçÁÉÍÓÚÃÕÂÊÔÇ ]+)\s*(\d+)", daf_yomi)
        if not match:
            print("[DEBUG] Regex não bateu no daf_yomi:", daf_yomi)
            return {"error": "Formato do Daf inválido. Use, por exemplo, 'Makkot 13'"}
        tratado_user = match.group(1).strip()
        daf_num = match.group(2).strip()
        print(f"[DEBUG] Tratado digitado: {tratado_user} | Daf: {daf_num}")
        tratado_ok, sugestoes = match_sefaria_book(tratado_user)
        print(f"[DEBUG] Tratado validado: {tratado_ok} | Sugestões: {sugestoes}")
        if not tratado_ok:
            msg = f"Tratado '{tratado_user}' não encontrado no Sefaria."
            if sugestoes:
                msg += f"\nSugestões: {', '.join(sugestoes)}"
            print("[DEBUG] Falha ao encontrar tratado. Mensagem:", msg)
            return {"error": msg}
        tratado = tratado_ok
        ref_a = f"{tratado}.{daf_num}a"
        ref_b = f"{tratado}.{daf_num}b"
        print(f"[DEBUG] Referências buscadas: {ref_a}, {ref_b}")
        textos = []
        referencias_usadas = []
        for ref in [ref_a, ref_b]:
            text = None
            # Busca preferencialmente em inglês
            for lang in ["en", "he"]:
                print(f"[DEBUG] Buscando {ref} em {lang}")
                result = search_sefaria(ref, lang=lang)
                print(f"[DEBUG] Resultado bruto: {result}")
                def norm_ref(s):
                    return s.replace(" ", "").replace(".", "").lower() if s else ""
                if result.get("found") and result.get("text") and (result.get("reference") or result.get("ref")):
                    ref_result = result.get("reference") or result.get("ref")
                    print(f"[DEBUG] Comparando {norm_ref(ref_result)} com {norm_ref(ref)}")
                    if norm_ref(ref_result) == norm_ref(ref):
                        text = result["text"]
                        referencias_usadas.append(ref_result)
                        print(f"[DEBUG] Aceito: {ref_result}")
                        break
                    else:
                        print(f"[DEBUG] Rejeitado: referência retornada não bate exatamente com a buscada")
                else:
                    print(f"[DEBUG] Rejeitado: resultado não tem texto ou referência")
            if text:
                # Se vier como lista, converte para string
                if isinstance(text, list):
                    text = "\n".join(str(l) for l in text)
                textos.append(f"[{ref}]:\n{text}\n")
            else:
                print(f"[DEBUG] Nenhum texto encontrado para {ref}")
                return {"error": f"Não foi possível encontrar o texto do Daf Yomi '{daf_yomi}' (frente e verso) no Sefaria."}
        if not textos:
            return {"error": f"Não foi possível encontrar o texto do Daf Yomi '{daf_yomi}' (frente e verso) no Sefaria."}
        texto_completo = "\n".join(textos)
        aviso = (
            "⚠️ IMPORTANT: On Sefaria, the first daf is always 2a (there is no 1a). "
            "The text returned matches exactly the real references fetched: "
            f"{', '.join(referencias_usadas) if referencias_usadas else 'None found'}\n"
            "Always check the actual reference on Sefaria's website to ensure it matches your daf.\n"
            f"You requested '{daf_yomi}'. The text fetched was for '{tratado} {daf_num}a' and '{tratado} {daf_num}b'.\n"
        )
        # Prompt em português para o resumo
        prompt = f"""
Você é um(a) grande estudioso(a) e educador(a) do Talmud. Sua tarefa é criar um resumo detalhado, didático e organizado por tópicos, em PORTUGUÊS (pt-br), do Daf Yomi abaixo. Siga exatamente a estrutura e estilo do exemplo:

---
[Insira aqui um exemplo de estrutura de resumo, se desejar]
---

{aviso}

Texto do Daf Yomi a ser resumido (frente e verso):
{texto_completo}

Instruções:
- Escreva SOMENTE o resumo em português, com introdução, tópicos numerados e destacados, e uma conclusão/reflexão.
- Seja claro, didático e fiel ao conteúdo do daf.
- NÃO inclua o texto bruto do daf no resultado.
- O resultado deve ser adequado para um arquivo Markdown (.md).
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
                temperature=0.15,
                max_tokens=4000
            )
            content = response.choices[0].message.content
            # Salva automaticamente o resumo em português
            filename = os.path.join(STUDIES_DIR, f"{tratado}_{daf_num}_pt.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "study_md": content, "file": filename}
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return {"error": str(e), "traceback": tb}
        # === FIM DO CÓDIGO ORIGINAL ===
    except Exception as e:
        print(f"[DEBUG] Exceção capturada: {e}")
        raise
    # Lê o modelo de EXEMPLO_DAF_YOMI.md
    try:
        with open("EXEMPLO_DAF_YOMI.md", "r", encoding="utf-8") as f:
            exemplo_daf = f.read()
    except Exception:
        exemplo_daf = ""  # fallback: sem modelo
    prompt = f"""
Você é um mestre em Talmud, com vasta experiência didática. Seu objetivo é criar um resumo didático, detalhado e organizado do Daf Yomi solicitado, seguindo exatamente o modelo abaixo:

---
{exemplo_daf}
---

{aviso}
{referencias_md}
Siga a estrutura, linguagem, divisão em tópicos e tom do exemplo. O resumo deve conter:
- Introdução
- Tópicos numerados e destacados
- Conclusão/reflexão
- Linguagem clara, didática e fiel ao texto do daf

Texto do Daf Yomi para resumir (frente e verso):
{texto_completo}

Gere apenas o resumo, sem comentários extras.
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
            temperature=0.15,
            max_tokens=4000
        )
        content = response.choices[0].message.content
        # Salva automaticamente o resumo
        filename = os.path.join(STUDIES_DIR, f"{tratado}_{daf_num}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(aviso)
            f.write(referencias_md)
            f.write("\n---\n")
            f.write(content)
        return {"success": True, "study_md": content, "file": filename}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return {"error": str(e), "traceback": tb}

def search_sefaria(reference, lang="he"):
    # Usa a nova API v3 do Sefaria
    url = f"https://www.sefaria.org/api/v3/texts/{reference}?lang={lang}"
    headers = {"accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers)
        print(f"[DEBUG] GET {url} -> Status {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # Tenta sempre retornar o texto disponível
            text = ""
            # 1. Tenta pegar texto principal
            if lang == "he":
                text = data.get("he") or data.get("text") or ""
            elif lang == "en":
                text = data.get("text") or data.get("he") or ""
            else:
                text = data.get("text") or data.get("he") or ""
            found = bool(text and any(line.strip() for line in text if isinstance(text, list))) if isinstance(text, list) else bool(text.strip())
            # 2. Se não encontrou, tenta nas versões alternativas
            if not found and "versions" in data:
                versions = data["versions"]
                # Prioridade: inglês, hebraico, qualquer
                version_text = ""
                # Procura inglês
                for v in versions:
                    if v.get("language", "").startswith("en") and v.get("text"):
                        version_text = v["text"]
                        print(f"[DEBUG] Texto encontrado em versão alternativa (en): {v.get('versionTitle')}")
                        break
                # Se não achou, procura hebraico
                if not version_text:
                    for v in versions:
                        if v.get("language", "").startswith("he") and v.get("text"):
                            version_text = v["text"]
                            print(f"[DEBUG] Texto encontrado em versão alternativa (he): {v.get('versionTitle')}")
                            break
                # Se ainda não achou, pega qualquer
                if not version_text:
                    for v in versions:
                        if v.get("text"):
                            version_text = v["text"]
                            print(f"[DEBUG] Texto encontrado em versão alternativa: {v.get('versionTitle')}")
                            break
                if version_text:
                    text = version_text
                    found = bool(text and any(line.strip() for line in text if isinstance(text, list))) if isinstance(text, list) else bool(text.strip())
            if not found and data.get("warnings"):
                print(f"[DEBUG] Aviso Sefaria: {data['warnings']}")
            return {
                "found": found,
                "text": text,
                "reference": data.get("ref", reference),
                "lang": lang,
                "raw": data
            }
        else:
            print(f"[DEBUG] Erro ao buscar referência {reference}: status {resp.status_code}")
            return {"found": False}
    except Exception as e:
        print(f"[DEBUG] Exceção ao buscar referência {reference}: {e}")
        return {"found": False}

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

ATENÇÃO: Mesmo que o tema seja o mesmo, traga sempre uma abordagem, exemplos, reflexões e estrutura diferentes a cada execução. Use criatividade, varie as fontes, os tópicos e as sugestões práticas. Nunca repita literalmente um estudo anterior.

Contexto:
Um Programa de estudos de Torá foi iniciado na escola Kabalah Online. Nesse programa será oferecido aos alunos ensinamentos da Cabala judaica, incluindo Zohar, guematria, mussar os comentários de Rashi, Tanya (Chabad), além da Halachá (Lei Judaica) segundo a tradição da Torá e do Shulchan Aruch.

Papel:
Você é um mestre cabalista e posek (autoridade haláchica), com amplo conhecimento da Lei Judaica e dos segredos da Torá. Suas respostas devem ser equilibradas, trazendo tanto a perspectiva haláchica (prática e normativa) quanto a perspectiva cabalística (esotérica e mística). Seu conhecimento cobre tanto os aspectos místicos e esotéricos da Torá quanto os aspectos práticos da Halachá. Você se baseia em fontes autênticas da tradição judaica, como o Talmud, Shulchan Aruch, Mishná Berurá, Rambam (Maimônides), Arizal, Zohar, Tanya e os escritos de grandes rabinos.

Você é capaz de orientar sobre:
    •    Guematria: A relação numérica e espiritual das palavras e sua interpretação à luz da Torá.
    •    Zohar e Cabala: Explicações esotéricas sobre a Torá e a alma.
    •    Mussar: Práticas espirituais validadas pela tradição rabínica.
    •    Halachá: Respostas práticas segundo o Shulchan Aruch, Rambam, Mishná Berurá e poskim modernos.
    •    Rashi, Tanya e Baal HaSulam: Conexões entre interpretação simples, Chassidut e Cabala.

Ação:
    1.    Analise a porção semanal '{parasha}' dentro do contexto da Torá, Cabala, Mussar e Halachá.
    2.    Se for uma questão haláchica, responda com base em fontes autênticas da Lei Judaica (Shulchan Aruch, Rambam, Mishná Berurá, Responsa rabínica).
    3.    Se for uma questão cabalística, explique à luz do Zohar, Arizal, Tanya e Baal HaSulam.
    4.    Se envolver guematria, calcule os valores numéricos e ofereça interpretações baseadas na Torá e na tradição mística.
    5.    Se envolver textos de Rashi, Tanya ou Baal HaSulam, conecte as interpretações peshat (simples), drash (midráshico), sod (esotérico) e sua aplicação prática.
    6.    It is extremely important and imperative that you always bring the appropriate references that you consulted to provide your answer.

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
            temperature=0.17,
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
        elif tool == "generate_daf_yomi_summary":
            daf = args.get("daf")
            if not daf:
                result = {"error": "Parâmetro 'daf' é obrigatório."}
            else:
                result = generate_daf_yomi_summary(daf)
        else:
            result = {"error": "Ferramenta desconhecida"}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

import os

def run(config_file=None):
    # Caminho robusto: sempre busca ../config/mcp_config.json relativo ao diretório do script
    if config_file is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(base_dir, '..', 'config', 'mcp_config.json')
    with open(config_file) as f:
        config = json.load(f)
    port = config.get("port", 8000)
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPHandler)
    print(f'Servidor MCP rodando na porta {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
