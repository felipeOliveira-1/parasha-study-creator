import logging
import requests
from typing import Dict, Optional
from .supabase_service import get_supabase_client

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

logger = logging.getLogger(__name__)

def get_parasha(name: str) -> Optional[Dict]:
    """
    Recupera uma parashá específica do Supabase e da API do Sefaria
    """
    # Primeiro tenta buscar do Supabase
    supabase = get_supabase_client()
    response = supabase.table('parashot').select('*').eq('name', name).execute()
    parasha_data = response.data[0] if response.data else None

    # Se não encontrou no Supabase, busca da API do Sefaria
    if not parasha_data:
        parasha_data = get_parasha_from_sefaria(name)
        if parasha_data:
            # Salva no Supabase para cache
            supabase.table('parashot').insert(parasha_data).execute()

    return parasha_data

def get_parasha_from_sefaria(parasha_name: str) -> Optional[Dict]:
    """
    Obtém o texto da parashá da API do Sefaria.
    """
    try:
        reference = get_parasha_reference(parasha_name)
        book, verses = reference.split(" ", 1)
        
        base_url = "https://www.sefaria.org/api/texts/"
        url = f"{base_url}{book}.{verses}?context=0&pad=0&commentary=0&language=en"
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Formata o texto da parashá
        text = data.get('text', [])
        if isinstance(text, list):
            text = ' '.join([' '.join(chapter) if isinstance(chapter, list) else chapter for chapter in text])
        
        return {
            'name': parasha_name,
            'reference': reference,
            'text': text,
            'hebrew': data.get('he', ''),
            'book': book,
            'verses': verses
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter parashá do Sefaria: {str(e)}")
        return None

def get_parasha_reference(parasha_name: str) -> str:
    """
    Obtém a referência correta da parashá no formato do Sefaria.
    """
    if parasha_name not in PARASHA_REFERENCES:
        raise ValueError(f"Parashá '{parasha_name}' não encontrada. Verifique o nome e tente novamente.")
    return PARASHA_REFERENCES[parasha_name]

def list_parashot() -> list:
    """
    Lista todas as parashiot disponíveis
    """
    supabase = get_supabase_client()
    response = supabase.table('parashot').select('name, description').execute()
    
    # Se não houver dados no Supabase, retorna a lista de referências
    if not response.data:
        return [{'name': name, 'description': ref} for name, ref in PARASHA_REFERENCES.items()]
        
    return response.data
