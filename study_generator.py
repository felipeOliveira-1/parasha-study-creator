import json
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from prompt_library import PromptLibrary

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
                model="gpt-4o",  # ou outro modelo configurado
                messages=[
                    PromptLibrary.get_parasha_summary_prompt(parasha_text)
                ]
            )
            summary = completion.choices[0].message.content
            
            # Gera os tópicos de estudo
            study_messages = [
                PromptLibrary.get_study_topics_prompt(summary)
            ]

            study_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=study_messages
            )
            topics_content = study_completion.choices[0].message.content

            # Adiciona os tópicos ao template
            template = f"# Estudo da Parashá\n\n## Resumo\n{summary}\n\n## Tópicos de Estudo\n{topics_content}\n"

            # Gera o Mussar com as referências
            if references:
                mussar_messages = [
                    PromptLibrary.get_mussar_prompt(topics_content, references)
                ]

                completion = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=mussar_messages
                )
                
                mussar_content = completion.choices[0].message.content
                template += f"\n## Mussar\n{mussar_content}\n"

            return template

        except Exception as e:
            self.logger.error(f"Erro ao gerar estudo: {str(e)}")
            if retries > 0:
                self.logger.info(f"Tentando novamente... ({retries} tentativas restantes)")
                return self.generate_study_topics(parasha_text, references, retries - 1)
            raise

    def generate_mussar_analysis(self, topics_content: str) -> str:
        """
        Gera a análise Mussar baseada nos tópicos e referências.
        """
        try:
            # Busca referências do Supabase
            references = self.reference_manager.get_references()
            
            # Busca textos de Mussar do Sefaria
            sefaria_texts = get_mussar_texts(self.parasha_ref)
            
            # Combina as referências
            all_references = []
            
            # Adiciona referências do Supabase
            for ref in references:
                all_references.append({
                    'source': ref.get('title', ''),
                    'text': ref.get('content', ''),
                    'type': 'supabase'
                })
            
            # Adiciona textos do Sefaria
            for text in sefaria_texts:
                all_references.append({
                    'source': text['source'],
                    'text': text['text'],
                    'ref': text['ref'],
                    'type': 'sefaria'
                })
            
            # Gera a análise Mussar
            prompt = PromptLibrary.get_mussar_prompt(topics_content, all_references)
            messages = [prompt]
            
            mussar_content = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            ).choices[0].message.content

            return mussar_content

        except Exception as e:
            logging.error(f"Erro ao gerar análise Mussar: {str(e)}")
            return "Erro ao gerar análise Mussar. Por favor, tente novamente."

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
                PromptLibrary.get_mussar_prompt(topics_content, references)
            ]

            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=mussar_messages
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar análise Mussar: {str(e)}")
            return ""
