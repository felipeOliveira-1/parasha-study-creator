"""
Biblioteca de prompts estruturados para o Parasha Study Creator.
Implementa templates XML para diferentes tipos de análise e geração de conteúdo.
"""

import os
from typing import List, Dict

class PromptLibrary:
    @staticmethod
    def get_parasha_summary_prompt(parasha_text: str) -> dict:
        """
        Template para geração de resumo da parashá.
        """
        return {
            "role": "system",
            "content": """
<prompt>
    <purpose>Criar um resumo conciso e significativo da parashá</purpose>
    <instructions>
        <instruction>Resuma o texto em português em no máximo 150 palavras</instruction>
        <instruction>Destaque apenas os 2-3 eventos mais significativos</instruction>
        <instruction>Foque nos principais ensinamentos morais</instruction>
        <instruction>Use linguagem clara e acessível</instruction>
    </instructions>
    <context>
        <text>{text}</text>
    </context>
</prompt>
""".format(text=parasha_text)
        }

    @staticmethod
    def get_study_topics_prompt(summary: str) -> dict:
        """
        Template para geração de tópicos de estudo.
        """
        return {
            "role": "system",
            "content": """
<prompt>
    <purpose>Criar tópicos de estudo aprofundados baseados na parashá</purpose>
    <context>
        <summary>{summary}</summary>
    </context>
    <strict_rules>
        <rule>Gere EXATAMENTE 3 tópicos, nem mais nem menos</rule>
        <rule>Cada comentarista tem limite de 30 palavras</rule>
        <rule>Use exatamente 2 comentaristas por tópico</rule>
        <rule>Cada tópico deve ter no máximo 400 palavras no total</rule>
        <rule>Não repita comentaristas entre tópicos</rule>
        <rule>Cada elemento deve seguir exatamente o formato e limites especificados</rule>
    </strict_rules>
    <output_format>
        <topic>
            <title>[Máximo 6 palavras, focando no tema central]</title>
            <verse>
                <reference>[Livro capítulo:versículo]</reference>
                <text>[Máximo 20 palavras, apenas o versículo essencial]</text>
            </verse>
            <context>[Máximo 30 palavras explicando o contexto histórico específico]</context>
            <commentaries>
                <commentary>
                    <author>[Nome do comentarista]</author>
                    <insight>[Exatamente 30 palavras explicando o insight principal]</insight>
                    <hebrew>[1 termo hebraico relevante com transliteração e significado em 5 palavras]</hebrew>
                </commentary>
                [Exatamente 2 comentaristas]
            </commentaries>
            <mussar_analysis>
                <middah>[Nome do traço de caráter em hebraico e português]</middah>
                <definition>[Definição do traço em exatamente 10 palavras]</definition>
                <relevance>[Por que este traço é relevante hoje - 20 palavras]</relevance>
                <exercises>
                    <morning>[1 exercício específico para manhã - 15 palavras]</morning>
                    <evening>[1 reflexão específica para noite - 15 palavras]</evening>
                    <weekly>[1 prática semanal mensurável - 15 palavras]</weekly>
                </exercises>
            </mussar_analysis>
            <modern_application>
                <challenge>[1 desafio moderno específico - 10 palavras]</challenge>
                <solution>[1 solução prática e mensurável - 15 palavras]</solution>
                <measurement>[Como medir progresso - 10 palavras]</measurement>
            </modern_application>
            <discussion>[1 pergunta provocativa relacionada ao tema central - 15 palavras]</discussion>
        </topic>
    </output_format>
    <formatting_rules>
        - Mantenha cada elemento exatamente dentro do limite de palavras especificado
        - Use linguagem clara e direta
        - Foque em aplicações práticas e mensuráveis
        - Mantenha-se dentro do judaísmo ortodoxo
        - Garanta que cada tópico seja único e complementar aos outros
        - Evite repetir termos em hebraico entre os tópicos
    </formatting_rules>
</prompt>
""".format(summary=summary)
        }

    @staticmethod
    def get_mussar_prompt(topics_content: str, references: List[Dict]) -> Dict:
        """Retorna o prompt para gerar a análise Mussar."""
        references_text = ""
        if references:
            references_text = "\n\nReferências encontradas:\n"
            for ref in references:
                if ref['type'] == 'supabase':
                    references_text += f"- {ref['text']} (Fonte: {ref['source']})\n"
                else:  # sefaria
                    references_text += f"- {ref['text']} (Fonte: {ref['source']}, Referência: {ref['ref']})\n"

        return {
            "role": "system",
            "content": f"""Você é um especialista em Mussar (ética e desenvolvimento moral judaico) com profundo conhecimento dos textos clássicos e modernos. 
            Sua tarefa é criar uma análise Mussar profunda e significativa baseada nos tópicos fornecidos e nas referências disponíveis.

            TÓPICOS:
            {topics_content}

            REFERÊNCIAS:
            {references_text}

            Ao criar a análise Mussar:
            1. Cite explicitamente as referências fornecidas, incluindo:
               - Para referências modernas: "Rabi [Nome], em '[Nome da Obra]', ensina que..."
               - Para textos clássicos do Sefaria: "O [Nome da Obra] (capítulo X) nos ensina que..."
            2. Conecte as citações com o contexto da parashá
            3. Foque em lições práticas de desenvolvimento moral
            4. Use linguagem acessível mas profunda

            Estruture sua resposta assim:
            1. Introdução geral ao tema Mussar da parashá
            2. 2-3 pontos principais, cada um com:
               - Uma citação de uma referência (alternando entre fontes modernas e clássicas)
               - Explicação da relevância para a parashá
               - Aplicação prática para nossos dias
            3. Conclusão com chamado à ação

            Use markdown para formatação."""
        }
