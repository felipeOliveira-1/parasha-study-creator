"""
Biblioteca de prompts estruturados para o Parasha Study Creator.
Implementa templates para diferentes tipos de análise e geração de conteúdo.
"""

from typing import List, Dict

def get_parasha_summary_prompt(parasha_text: str) -> List[Dict]:
    """
    Template para geração de resumo da parashá.
    """
    return [
        {
            "role": "system",
            "content": "Você é um especialista em estudos judaicos com profundo conhecimento da Torá. "
                      "Sua tarefa é criar um resumo conciso e significativo da parashá em português."
        },
        {
            "role": "user",
            "content": f"""Por favor, crie um resumo da seguinte parashá seguindo estas diretrizes:
- Máximo de 150 palavras
- Destaque apenas os 2-3 eventos mais significativos
- Foque nos principais ensinamentos morais
- Use linguagem clara e acessível

Texto da parashá:
{parasha_text}"""
        }
    ]

def get_themes_extraction_prompt(summary: str) -> List[Dict]:
    """
    Template para extração de temas principais para busca de referências Mussar.
    """
    return [
        {
            "role": "system",
            "content": "Você é um especialista em Mussar (ética judaica). "
                      "Sua tarefa é identificar os principais temas morais e éticos do texto."
        },
        {
            "role": "user",
            "content": f"""Identifique 3 temas morais ou éticos principais do seguinte resumo:
- Cada tema deve ser uma frase curta e clara
- Foque em conceitos universais do Mussar (como humildade, verdade, bondade)
- Liste um tema por linha

Resumo:
{summary}"""
        }
    ]

def get_study_topics_prompt(summary: str, mussar_references: List[Dict] = None) -> List[Dict]:
    """
    Template para geração de tópicos de estudo com referências Mussar.
    """
    refs_text = ""
    if mussar_references:
        refs_text = "\n\nReferências Mussar:\n" + "\n".join([
            f"- {ref['source']}: {ref['citation']}"
            for ref in mussar_references
        ])

    return [
        {
            "role": "system",
            "content": "Você é um rabino especializado em estudos da Torá e Mussar. "
                      "Sua tarefa é criar tópicos de estudo aprofundados baseados na parashá."
        },
        {
            "role": "user",
            "content": f"""Crie EXATAMENTE 3 tópicos de estudo baseados no seguinte resumo, seguindo este formato para cada tópico:

1. Título do Tópico
2. Contexto narrativo (breve explicação do contexto na parashá)
3. Versículo relevante com referência
4. Análise baseada nos ensinamentos da Torá
5. Aplicação prática dos ensinamentos

Regras:
- Cada tópico deve ter no máximo 400 palavras no total
- Use linguagem clara e acessível
- Foque em lições práticas e relevantes

Resumo:
{summary}{refs_text}"""
        }
    ]

def get_mussar_prompt(topics_content: str, references: List[Dict] = None) -> List[Dict]:
    """
    Template para geração de análise Mussar adicional.
    """
    if not references:
        return [
            {
                "role": "system",
                "content": "Você é um mestre em Mussar com profundo conhecimento dos textos éticos judaicos."
            },
            {
                "role": "user",
                "content": f"""Crie uma análise Mussar dos seguintes tópicos:
1. Identifique as principais virtudes e desafios morais
2. Extraia lições práticas para o desenvolvimento pessoal
3. Sugira exercícios ou reflexões para trabalhar essas virtudes

Tópicos:
{topics_content}"""
            }
        ]

    refs_text = "\n".join([
        f"- {ref['source']}: {ref['citation']}"
        for ref in references
    ])

    return [
        {
            "role": "system",
            "content": "Você é um mestre em Mussar com profundo conhecimento dos textos éticos judaicos. "
                      "Sua tarefa é criar uma análise Mussar adicional baseada nos tópicos e referências fornecidos."
        },
        {
            "role": "user",
            "content": f"""Crie uma análise Mussar adicional que:
1. Conecte os tópicos com os ensinamentos das referências
2. Extraia lições práticas para o desenvolvimento pessoal
3. Sugira exercícios ou reflexões baseados no Mussar

Tópicos:
{topics_content}

Referências:
{refs_text}"""
        }
    ]
