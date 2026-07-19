import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
org_id = os.getenv('OPENAI_ORG_ID')

print('🔍 OpenAI Configurasyon Kontrolü')
print(f'API Key: {api_key[:20]}...' if api_key else 'BOŞSA')
print(f'Organization ID: {org_id if org_id else "AYARLANMAMIŞSA"}')

try:
    # Client oluştur
    if org_id:
        client = OpenAI(api_key=api_key, organization=org_id)
    else:
        client = OpenAI(api_key=api_key)
    
    print('\n✅ Client oluşturuldu')
    
    # Models listele
    models = client.models.list()
    print(f'✅ Modeller erişilebilir: {len(models.data)} adet')
    
    # Rate limits bilgisi
    print('\n📊 Çok basit bir test...')
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print(f'✅ TEST BAŞARILI!')
    print(f'   Model: {response.model}')
    print(f'   Yanıt: {response.choices[0].message.content}')
    
except Exception as e:
    print(f'\n❌ Hata: {type(e).__name__}')
    print(f'   Mesaj: {str(e)[:300]}')
