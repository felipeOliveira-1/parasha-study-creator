"""
Biblioteca de prompts estruturados para o Parasha Study Creator.
Implementa templates XML para diferentes tipos de análise e geração de conteúdo.
"""

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
    def get_mussar_prompt(topics_content: str, references: list) -> dict:
        """
        Template para análise Mussar.
        """
        references_text = "\n".join([f"- {ref.get('title', 'Unknown')}" for ref in references])
        return {
            "role": "system",
            "content": """
<prompt>
    <purpose>Gerar análise Mussar focada em crescimento pessoal mensurável</purpose>
    <context>
        <topics>{topics}</topics>
        <available_references>
            {references}
        </available_references>
    </context>
    <strict_rules>
        <rule>Crie uma análise Mussar concisa por tópico (máximo 200 palavras)</rule>
        <rule>Use exatamente 1 citação relevante por tópico (máximo 20 palavras)</rule>
        <rule>Cada exercício deve ser específico e mensurável</rule>
        <rule>Foque em um único middah (traço de caráter) por tópico</rule>
    </strict_rules>
    <output_format>
        <mussar_analysis>
            <topic_analysis>
                <topic_title>[Título do Tópico]</topic_title>
                <middah>
                    <name>[Nome do traço em hebraico e português]</name>
                    <definition>[Definição em exatamente 10 palavras]</definition>
                    <importance>[Por que é importante hoje - 20 palavras]</importance>
                </middah>
                <citation>
                    <source>[Nome da fonte]</source>
                    <quote>[Citação - máximo 20 palavras]</quote>
                    <application>[Como aplicar - 20 palavras]</application>
                </citation>
                <daily_practice>
                    <morning>[1 exercício específico - 10 palavras]</morning>
                    <afternoon>[1 ponto de verificação - 10 palavras]</afternoon>
                    <evening>[1 reflexão guiada - 10 palavras]</evening>
                </daily_practice>
                <progress>
                    <metric>[Como medir sucesso - 10 palavras]</metric>
                    <milestone>[Meta para 30 dias - 10 palavras]</milestone>
                </progress>
            </topic_analysis>
        </mussar_analysis>
    </output_format>
    <formatting_rules>
        - Mantenha cada elemento exatamente no limite especificado
        - Use linguagem clara e acionável
        - Foque em práticas mensuráveis
        - Evite repetir middot entre os tópicos
        - Garanta que exercícios sejam específicos e realizáveis
    </formatting_rules>
</prompt>
""".format(topics=topics_content, references=references_text)
        }
