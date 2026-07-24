from app.main import app
from fastapi.routing import APIRoute

routes = [r for r in app.routes if isinstance(r, APIRoute)]
print(f"Found {len(routes)} routes:\n")
for r in routes:
    methods = ",".join(sorted([m for m in r.methods if m not in ("HEAD","OPTIONS")]))
    deps = []
    try:
        for d in r.dependant.dependencies:
            deps.append(str(d))
    except Exception:
        deps = [str(r.dependant)]
    print(f"{methods:6} {r.path:40} | name={r.name:30} | include_in_schema={r.include_in_schema} | deps={deps}")
