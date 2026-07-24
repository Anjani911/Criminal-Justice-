import urllib.request, json
base='http://127.0.0.1:8000'
for path in ['/api/v1/health','/api/v1/version','/api/v1/openapi.json']:
    url=base+path
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            body=r.read().decode('utf-8')
            print(path, r.status)
            data=json.loads(body)
            if path.endswith('openapi.json'):
                print('openapi title:', data.get('info',{}).get('title'))
            else:
                print('keys:', list(data.keys()))
    except Exception as e:
        print(path, 'ERROR', e)
