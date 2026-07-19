import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

try:
    client = OpenAI(api_key=api_key)
    
    print('🧪 Basit test isteniyor...')
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Merhaba, sen kimsin?"}
        ],
        temperature=0.3,
        max_tokens=50
    )
    
    print('✅ BAŞARILI!')
    print(f'Model: {response.model}')
    print(f'Yanıt: {response.choices[0].message.content}')
    
except Exception as e:
    print(f'❌ Hata: {type(e).__name__}')
    print(f'Mesaj: {str(e)[:300]}')
