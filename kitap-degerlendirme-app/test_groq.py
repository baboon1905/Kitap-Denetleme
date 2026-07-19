import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_key = os.getenv('GROQ_API_KEY')

print('🔍 Groq API Kontrol')
print(f'API Key: {groq_key[:10]}...' if groq_key else 'BOŞSA')

try:
    client = Groq(api_key=groq_key)
    print('✅ Groq client oluşturuldu')
    
    # Test
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": "Merhaba"}],
        max_tokens=20
    )
    
    print('✅ TEST BAŞARILI!')
    print(f'   Model: {response.model}')
    print(f'   Yanıt: {response.choices[0].message.content}')
    
except Exception as e:
    print(f'❌ Hata: {type(e).__name__}')
    print(f'   Mesaj: {str(e)[:200]}')
