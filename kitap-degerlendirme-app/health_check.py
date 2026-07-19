import requests
import sys
try:
    r = requests.get('http://127.0.0.1:5000/health', timeout=10)
    print('STATUS', r.status_code)
    print(r.text[:2000])
except Exception as e:
    print('ERR', repr(e))
    sys.exit(2)
