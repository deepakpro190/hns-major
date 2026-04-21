from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

from services.scheduler import start_aggregation_loop

from api.ingest import router as ingest_router
from api.live_status import router as live_router
from api.prediction import router as prediction_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    threading.Thread(target=start_aggregation_loop, daemon=True).start()
from api.storage import router as storage_router

app.include_router(storage_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")
app.include_router(live_router, prefix="/api")
app.include_router(prediction_router, prefix="/api")
from api.transport import router as transport_router

app.include_router(transport_router, prefix="/api")

