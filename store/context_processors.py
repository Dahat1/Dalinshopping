# store/context_processors.py
from .translations import get_translations

def language_processor(request):
    # URL'den dili al (settings.py'deki ayar sayesinde otomatik gelir)
    current_lang = request.LANGUAGE_CODE 
    
    # 'en-us' gelirse 'en' yapalım
    if 'en' in current_lang:
        current_lang = 'en'

    # Sözlüğü çek
    texts = get_translations(current_lang)

    return {
        't': texts,       # HTML'de {{ t.home }} diye kullanacağız
        'CURRENT_LANG': current_lang # Şu anki dil kodu
    }