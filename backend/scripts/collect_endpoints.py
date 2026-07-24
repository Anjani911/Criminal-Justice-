import re
import pathlib
from typing import Dict, List

api_dir = pathlib.Path(__file__).resolve().parents[1] / 'app' / 'api'
files = list(api_dir.glob('*.py'))
endpoints = []

router_prefix = {}
# find router prefix per file
for f in files:
    text = f.read_text(encoding='utf-8')
    m = re.search(r"router\s*=\s*APIRouter\([^)]*prefix\s*=\s*(?P<prefix>[^,\)]+)", text)
    if m:
        prefix = m.group('prefix').strip()
        router_prefix[f.name] = prefix
    else:
        router_prefix[f.name] = None

pattern = re.compile(r"@router\.(get|post|put|delete|patch)\((?P<args>[^)]*)\)")
for f in files:
    text = f.read_text(encoding='utf-8')
    for match in pattern.finditer(text):
        method = match.group(1).upper()
        args = match.group('args')
        # extract first string literal as path if present
        path_m = re.search(r"r?\"([^\"]*)\"|r?\'([^\']*)\'", args)
        path = path_m.group(1) if path_m and path_m.group(1) else (path_m.group(2) if path_m and path_m.group(2) else '')
        prefix = router_prefix.get(f.name) or ''
        full_path = (prefix + path).replace('"', '')
        endpoints.append({'file': f.name, 'method': method, 'path': full_path, 'decorator_args': args.strip()})

print(f"Discovered {len(endpoints)} endpoints via static scan:\n")
for e in endpoints:
    print(f"{e['method']:6} {e['path']:50} | defined_in={e['file']:20} | args={e['decorator_args']}")
