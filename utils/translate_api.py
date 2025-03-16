# utils/translate_api.py
import ssl
import certifi  # Bu qatorni qo'shing

import aiohttp
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class CambridgeDictionary:
    BASE_URL = 'https://dictionary.cambridge.org/dictionary/english/'

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def get_word_info(self, word):
        """So'zni Cambridge Dictionary saytidan izlash va ma'lumotlarni qaytarish"""
        url = self.BASE_URL + word.lower().strip()

        try:
            # Certifi bilan SSL kontekst yaratamiz
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            async with aiohttp.ClientSession() as session:
                # ssl_context parametrini qo'shamiz
                async with session.get(url, headers=self.headers, ssl=ssl_context) as response:
                    if response.status != 200:
                        logger.error(f"Cambridge Dictionary API xatosi: {response.status} - {url}")
                        return {
                            'success': False,
                            'error': f"Xatolik yuz berdi. Status kod: {response.status}"
                        }

                    html = await response.text()

            return self._parse_html(html, word)

        except Exception as e:
            logger.error(f"Cambridge Dictionary API xatosi: {str(e)}")
            return {
                'success': False,
                'error': f"So'rovda xatolik yuz berdi: {str(e)}"
            }


    def _parse_html(self, html, word):
        """HTML ma'lumotlarini parse qilish"""
        soup = BeautifulSoup(html, 'html.parser')

        # So'z topilmagan holatni tekshirish
        if not soup.find('div', class_='di-body'):
            return {
                'success': False,
                'error': f"'{word}' so'zi topilmadi. Imlosini tekshiring."
            }

        result = {
            'success': True,
            'word': word,
            'definitions': [],
            'pronunciations': {
                'uk': None,  # British talaffuz
                'us': None  # American talaffuz
            }
        }

        try:
            # Asosiy ma'nolar bloklarini topish
            definition_blocks = soup.find_all('div', class_='def-block')

            # Ma'nolarni olish
            for block in definition_blocks[:5]:  # Birinchi 5 ta ma'noni olish
                definition = block.find('div', class_='def')
                if definition:
                    result['definitions'].append(definition.text.strip())

            # Talaffuz audio fayllarini olish
            # UK (British) talaffuz


            uk_audio = soup.select_one('span.uk source[type="audio/mpeg"]')
            if uk_audio and uk_audio.get('src'):
                result['pronunciations']['uk'] = 'https://dictionary.cambridge.org' + uk_audio.get('src')




            # US (American) talaffuz
            us_audio = soup.select_one('span.us source[type="audio/mpeg"]')
            if us_audio and us_audio.get('src'):
                result['pronunciations']['us'] = 'https://dictionary.cambridge.org' + us_audio.get('src')

        except Exception as e:
            logger.error(f"HTML parsing xatosi: {str(e)}")
            result['success'] = False
            result['error'] = f"Ma'lumotlarni olishda xatolik: {str(e)}"

        return result