import logging
from typing import Dict, List, Optional
from openai import OpenAI

class StudyGenerator:
    def __init__(self, openai_client: OpenAI):
        """
        Inicializa o gerador de estudos.
        
        Args:
            openai_client: Cliente OpenAI configurado
        """
        self.client = openai_client
        self.logger = logging.getLogger(__name__)

    def generate_study_topics(self, parasha_text: str, references: List[Dict] = None, retries: int = 3) -> str:
        """
        Gera tópicos de estudo baseados no texto da parashá.
        
        Args:
            parasha_text: Texto da parashá
            references: Lista opcional de referências relevantes
            retries: Número de tentativas em caso de erro
            
        Returns:
            str: Conteúdo do estudo gerado
        """
        try:
            # Gera um resumo do texto da parashá
            completion = self.client.chat.completions.create(
                model="gpt-4",  # ou outro modelo configurado
                messages=[
                    {"role": "system", "content": "Você é um especialista em Torá."},
                    {
                        "role": "user",
                        "content": f"Resuma o seguinte texto da Torá em português, destacando os principais acontecimentos e ensinamentos (máximo 300 caracteres):\n\n{parasha_text}"
                    }
                ]
            )
            summary = completion.choices[0].message.content
            
            # Gera os tópicos de estudo
            study_messages = [
                {
                    "role": "system",
                    "content": """You are a Rabbi specializing in Jewish studies, with deep knowledge of Torah, Talmud, Mishnah, Midrash, Halakha, Kabbalah, and Jewish thought. Your task is to create study topics in PT-BR that help deepen the understanding of the Torah portion. Always keep the scope within Orthodox Judaism."""
                },
                {
                    "role": "user",
                    "content": f"""Based on this summary of the parasha: {summary}

                    Develop 3 study topics, each containing:
                    - Topic title
                    - Related Bible verse (reference and text)
                    - A deep reflection on the topic
                    - A question for discussion
                    - 3 practical tips for applying the learning

                    Format each topic like this:
                    ### [Topic Title]
                    **Bible Verse:** [Reference]
                    **The Verse:** "[Verse Text]"

                    **Reflection:** [Your Reflection]

                    **Discussion Question:** [Your Question]

                    **Practical Tips:**
                    - [Tip 1]
                    - [Tip 2]
                    - [Tip 3]"""
                }
            ]

            study_completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=study_messages
            )
            topics_content = study_completion.choices[0].message.content

            # Adiciona os tópicos ao template
            template = f"# Estudo da Parashá\n\n## Resumo\n{summary}\n\n## Tópicos de Estudo\n{topics_content}\n"

            # Gera o Mussar com as referências
            if references:
                mussar_content = self._generate_mussar_analysis(topics_content, references)
                template += f"\n## Mussar\n{mussar_content}\n"

            return template

        except Exception as e:
            self.logger.error(f"Erro ao gerar estudo: {str(e)}")
            if retries > 0:
                self.logger.info(f"Tentando novamente... ({retries} tentativas restantes)")
                return self.generate_study_topics(parasha_text, references, retries - 1)
            raise

    def _generate_mussar_analysis(self, topics_content: str, references: List[Dict]) -> str:
        """
        Gera análise Mussar para os tópicos de estudo.
        
        Args:
            topics_content: Conteúdo dos tópicos de estudo
            references: Lista de referências relevantes
            
        Returns:
            str: Análise Mussar gerada
        """
        try:
            mussar_messages = [
                {
                    "role": "system",
                    "content": """As a Rabbi, your task is to create a comprehensive Mussar analysis with practical tips for each topic. The Mussar analysis should include citations from available references, formatted as: "In [Book Name], we find: '[QUOTE]'. This teaching shows us that..." You should provide detailed explanations after each citation and demonstrate how it applies to modern life. Avoid repeating the same source twice, and ensure that your response is in pt-br."""
                },
                {
                    "role": "user",
                    "content": f"""Crie uma análise Mussar com citações das referências e dicas práticas para cada tópico:

                    Tópicos: {topics_content}

                    Referências Disponíveis:
                    {references}"""
                }
            ]

            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=mussar_messages
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar análise Mussar: {str(e)}")
            return ""
