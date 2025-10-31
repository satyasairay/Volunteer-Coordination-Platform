import json
from fastapi.testclient import TestClient
import main

c = TestClient(main.app)
for url in ['/api/map-settings','/api/villages/pins','/api/blocks']:
    r = c.get(url)
    print(url, r.status_code, len(r.content))
