import logging
import requests
from typing import Dict, Optional

# Mapeamento de parashiot para suas referências no Sefaria
PARASHA_REFERENCES = {
    "Bereshit": "Genesis 1:1-6:8",
    "Noach": "Genesis 6:9-11:32",
    "Lech Lecha": "Genesis 12:1-17:27",
    "Vayera": "Genesis 18:1-22:24",
    "Chayei Sarah": "Genesis 23:1-25:18",
    "Toldot": "Genesis 25:19-28:9",
    "Vayetzei": "Genesis 28:10-32:3",
    "Vayishlach": "Genesis 32:4-36:43",
    "Vayeshev": "Genesis 37:1-40:23",
    "Miketz": "Genesis 41:1-44:17",
    "Vayigash": "Genesis 44:18-47:27",
    "Vayechi": "Genesis 47:28-50:26",
    "Shemot": "Exodus 1:1-6:1",
    "Vaera": "Exodus 6:2-9:35",
    "Bo": "Exodus 10:1-13:16",
    "Beshalach": "Exodus 13:17-17:16",
    "Yitro": "Exodus 18:1-20:23",
    "Mishpatim": "Exodus 21:1-24:18",
    "Terumah": "Exodus 25:1-27:19",
    "Tetzaveh": "Exodus 27:20-30:10",
    "Ki Tisa": "Exodus 30:11-34:35",
    "Vayakhel": "Exodus 35:1-38:20",
    "Pekudei": "Exodus 38:21-40:38",
    "Vayikra": "Leviticus 1:1-5:26",
    "Tzav": "Leviticus 6:1-8:36",
    "Shemini": "Leviticus 9:1-11:47",
    "Tazria": "Leviticus 12:1-13:59",
    "Metzora": "Leviticus 14:1-15:33",
    "Achrei Mot": "Leviticus 16:1-18:30",
    "Kedoshim": "Leviticus 19:1-20:27",
    "Emor": "Leviticus 21:1-24:23",
    "Behar": "Leviticus 25:1-26:2",
    "Bechukotai": "Leviticus 26:3-27:34",
    "Bamidbar": "Numbers 1:1-4:20",
    "Naso": "Numbers 4:21-7:89",
    "Beha'alotekha": "Numbers 8:1-12:16",
    "Shelach": "Numbers 13:1-15:41",
    "Korach": "Numbers 16:1-18:32",
    "Chukat": "Numbers 19:1-22:1",
    "Balak": "Numbers 22:2-25:9",
    "Pinchas": "Numbers 25:10-30:1",
    "Matot": "Numbers 30:2-32:42",
    "Masei": "Numbers 33:1-36:13",
    "Devarim": "Deuteronomy 1:1-3:22",
    "Vaetchanan": "Deuteronomy 3:23-7:11",
    "Eikev": "Deuteronomy 7:12-11:25",
    "Re'eh": "Deuteronomy 11:26-16:17",
    "Shoftim": "Deuteronomy 16:18-21:9",
    "Ki Teitzei": "Deuteronomy 21:10-25:19",
    "Ki Tavo": "Deuteronomy 26:1-29:8",
    "Nitzavim": "Deuteronomy 29:9-30:20",
    "Vayeilech": "Deuteronomy 31:1-31:30",
    "Ha'azinu": "Deuteronomy 32:1-32:52",
    "VeZot HaBerakhah": "Deuteronomy 33:1-34:12"
}

class ParashaManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_parasha_reference(self, parasha_name: str) -> str:
        """
        Obtém a referência correta da parashá no formato do Sefaria.
        
        Args:
            parasha_name: Nome da parashá (ex: "Bereshit", "Noach")
            
        Returns:
            str: Referência no formato do Sefaria (ex: "Genesis 1:1-6:8")
        """
        if parasha_name not in PARASHA_REFERENCES:
            raise ValueError(f"Parashá '{parasha_name}' não encontrada. Verifique o nome e tente novamente.")
        return PARASHA_REFERENCES[parasha_name]

    def get_parasha_text(self, parasha_name: str) -> str:
        """
        Obtém o texto da parashá da API do Sefaria.
        
        Args:
            parasha_name: Nome da parashá
            
        Returns:
            str: Texto completo da parashá
        """
        try:
            reference = self.get_parasha_reference(parasha_name)
            book, verses = reference.split(" ", 1)
            
            base_url = "https://www.sefaria.org/api/texts/"
            url = f"{base_url}{book}.{verses}?context=0&pad=0&commentary=0&language=en"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if 'text' not in data:
                raise ValueError("Resposta da API não contém campo 'text'")
                
            text = self._flatten_text(data['text'])
            
            if not text.strip():
                raise ValueError("Texto da parashá está vazio após processamento")
                
            return text
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao fazer requisição para a API do Sefaria: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao obter texto da parashá: {e}")
            raise

    def _flatten_text(self, text_data) -> str:
        """
        Função auxiliar para achatar estruturas de texto aninhadas.
        
        Args:
            text_data: Texto ou estrutura de dados contendo texto
            
        Returns:
            str: Texto achatado em uma única string
        """
        if isinstance(text_data, str):
            return text_data
        elif isinstance(text_data, list):
            return " ".join(self._flatten_text(item) for item in text_data if item)
        else:
            return ""

    def list_available_parashot(self) -> list:
        """
        Lista todas as parashot disponíveis.
        
        Returns:
            list: Lista de nomes das parashot
        """
        return sorted(PARASHA_REFERENCES.keys())
