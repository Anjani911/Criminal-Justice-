import requests, json
BASE='http://127.0.0.1:8000'
results=[]

def try_post(path, data, token=None):
    headers={'Content-Type':'application/json'}
    if token: headers['Authorization']=f'Bearer {token}'
    r = requests.post(BASE+path, json=data, headers=headers, timeout=10)
    return r

def try_get(path, token=None):
    headers={}
    if token: headers['Authorization']=f'Bearer {token}'
    r = requests.get(BASE+path, headers=headers, timeout=10)
    return r

print('Login valid')
r=try_post('/api/v1/auth/login', {'username':'admin','password':'password123'})
print(r.status_code)
try:
    data=r.json()
    token=data.get('access_token')
    print('got token:', bool(token))
except Exception as e:
    print('login parse error', e)
    token=None

print('\nLogin invalid')
r2=try_post('/api/v1/auth/login', {'username':'nope','password':'wrong'})
print(r2.status_code, r2.text[:200])

print('\n/me with token')
r3=try_get('/api/v1/auth/me', token=token)
print(r3.status_code)
print(r3.json() if r3.status_code==200 else r3.text[:200])

paths = [
    '/api/v1/cases',
    '/api/v1/analytics/dashboard',
    '/api/v1/analytics/crime-trends',
    '/api/v1/analytics/hotspots',
    '/api/v1/predictions/trends',
    '/api/v1/predictions/hotspots',
    '/api/v1/predictions/station-risk',
    '/api/v1/predictions/warnings',
    '/api/v1/network',
    '/api/v1/network/metrics',
    '/api/v1/reports/dashboard',
    '/api/v1/audit',
]

for p in paths:
    try:
        r=try_get(p, token=token)
        text = ''
        try:
            j=r.json()
            if isinstance(j, dict):
                text = str(list(j.keys()))
            else:
                text = str(type(j))
        except Exception:
            text = r.text[:200]
        print(p, r.status_code, text)
    except Exception as e:
        print(p, 'ERROR', e)

# predictions specifics
print('\nPredictions detail calls')
for p in ['/api/v1/predictions/trends','/api/v1/predictions/hotspots','/api/v1/predictions/station-risk','/api/v1/predictions/warnings']:
    try:
        r=try_get(p, token=token)
        print(p, r.status_code)
        try:
            print('status field:', r.json().get('status'))
        except Exception:
            print('no json')
    except Exception as e:
        print(p, 'ERROR', e)

print('\nDone')
