
from __future__ import annotations

from acto_server.app import create_app
from mangum import Mangum

# FastAPI 
app = create_app()

# Mangum adapter 
handler = Mangum(app, lifespan="off")

