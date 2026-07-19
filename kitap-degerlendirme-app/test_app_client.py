from app import app

with app.test_client() as c:
    r = c.get('/health')
    print('STATUS', r.status_code)
    print(r.get_data(as_text=True)[:2000])
