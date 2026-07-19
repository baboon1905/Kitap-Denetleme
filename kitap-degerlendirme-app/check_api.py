import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

print('API Key kontrol:')
print(f'  Uzunluk: {len(api_key) if api_key else 0}')
if api_key:
    print(f'  Başlangıç: {api_key[:10]}...')
    print(f'  Bitiş: ...{api_key[-10:]}')
else:
    print('  ❌ API KEY BOŞSA')

# OpenAI test
try:
    client = OpenAI(api_key=api_key)
    print('\n✅ OpenAI client oluşturuldu')
    
    # Basit bir istekle test et
    response = client.models.list()
    print(f'✅ OpenAI bağlantısı başarılı')
    print(f'  Mevcut modeller: {len(response.data)} adet')
    
except Exception as e:
    print(f'\n❌ Hata: {type(e).__name__}')
    print(f'  Detay: {str(e)[:200]}')
