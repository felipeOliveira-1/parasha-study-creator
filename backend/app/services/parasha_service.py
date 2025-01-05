import logging
import requests
from typing import Dict, Optional, List
from functools import lru_cache

logger = logging.getLogger(__name__)

# Mapeamento de parashiot para suas referências no Sefaria
PARASHA_REFERENCES = {
    "Bereshit": "Genesis.1.1-6.8",
    "Noach": "Genesis.6.9-11.32",
    "Lech Lecha": "Genesis.12.1-17.27",
    "Vayera": "Genesis.18.1-22.24",
    "Chayei Sarah": "Genesis.23.1-25.18",
    "Toldot": "Genesis.25.19-28.9",
    "Vayetzei": "Genesis.28.10-32.3",
    "Vayishlach": "Genesis.32.4-36.43",
    "Vayeshev": "Genesis.37.1-40.23",
    "Miketz": "Genesis.41.1-44.17",
    "Vayigash": "Genesis.44.18-47.27",
    "Vayechi": "Genesis.47.28-50.26",
    "Shemot": "Exodus.1.1-6.1",
    "Vaera": "Exodus.6.2-9.35",
    "Bo": "Exodus.10.1-13.16",
    "Beshalach": "Exodus.13.17-17.16",
    "Yitro": "Exodus.18.1-20.23",
    "Mishpatim": "Exodus.21.1-24.18",
    "Terumah": "Exodus.25.1-27.19",
    "Tetzaveh": "Exodus.27.20-30.10",
    "Ki Tisa": "Exodus.30.11-34.35",
    "Vayakhel": "Exodus.35.1-38.20",
    "Pekudei": "Exodus.38.21-40.38",
    "Vayikra": "Leviticus.1.1-5.26",
    "Tzav": "Leviticus.6.1-8.36",
    "Shemini": "Leviticus.9.1-11.47",
    "Tazria": "Leviticus.12.1-13.59",
    "Metzora": "Leviticus.14.1-15.33",
    "Achrei Mot": "Leviticus.16.1-18.30",
    "Kedoshim": "Leviticus.19.1-20.27",
    "Emor": "Leviticus.21.1-24.23",
    "Behar": "Leviticus.25.1-26.2",
    "Bechukotai": "Leviticus.26.3-27.34",
    "Bamidbar": "Numbers.1.1-4.20",
    "Naso": "Numbers.4.21-7.89",
    "Beha'alotekha": "Numbers.8.1-12.16",
    "Shelach": "Numbers.13.1-15.41",
    "Korach": "Numbers.16.1-18.32",
    "Chukat": "Numbers.19.1-22.1",
    "Balak": "Numbers.22.2-25.9",
    "Pinchas": "Numbers.25.10-30.1",
    "Matot": "Numbers.30.2-32.42",
    "Masei": "Numbers.33.1-36.13",
    "Devarim": "Deuteronomy.1.1-3.22",
    "Vaetchanan": "Deuteronomy.3.23-7.11",
    "Eikev": "Deuteronomy.7.12-11.25",
    "Re'eh": "Deuteronomy.11.26-16.17",
    "Shoftim": "Deuteronomy.16.18-21.9",
    "Ki Teitzei": "Deuteronomy.21.10-25.19",
    "Ki Tavo": "Deuteronomy.26.1-29.8",
    "Nitzavim": "Deuteronomy.29.9-30.20",
    "Vayelech": "Deuteronomy.31.1-31.30",
    "Haazinu": "Deuteronomy.32.1-32.52",
    "V'Zot HaBerachah": "Deuteronomy.33.1-34.12"
}

def get_parasha(name: str) -> Optional[Dict]:
    """
    Recupera uma parashá específica da API do Sefaria
    """
    try:
        logger.info(f"Getting parasha {name} from Sefaria")
        reference = get_parasha_reference(name)
        if not reference:
            logger.error(f"No Sefaria reference found for parasha: {name}")
            return None
            
        logger.info(f"Found reference {reference} for parasha {name}")
        text = get_parasha_from_sefaria(name)
        if not text:
            logger.error(f"Failed to get text from Sefaria for parasha: {name}")
            return None
            
        return {
            'name': name,
            'reference': reference,
            'text': text,
            'book': reference.split('.')[0]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving parasha {name}: {str(e)}")
        return None

@lru_cache(maxsize=100)
def get_parasha_from_sefaria(parasha_name: str) -> Optional[str]:
    """
    Obtém o texto da parashá da API do Sefaria.
    """
    try:
        reference = get_parasha_reference(parasha_name)
        if not reference:
            return None
            
        url = f"https://www.sefaria.org/api/texts/{reference}?context=0"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Processamento mais eficiente do texto
        text = "\n\n".join(
            " ".join(verse for verse in chapter if verse) if isinstance(chapter, list)
            else chapter
            for chapter in data.get('text', [])
        )
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error fetching text for parasha {parasha_name}: {str(e)}")
        return None

def get_parasha_reference(parasha_name: str) -> Optional[str]:
    """
    Obtém a referência correta da parashá no formato do Sefaria.
    """
    return PARASHA_REFERENCES.get(parasha_name)

def list_parashot() -> List[Dict]:
    """
    Lista todas as parashiot disponíveis
    """
    try:
        return [
            {
                'name': name,
                'reference': ref,
                'book': ref.split('.')[0]
            }
            for name, ref in PARASHA_REFERENCES.items()
        ]
    except Exception as e:
        logger.error(f"Error listing parashot: {str(e)}")
        return []
