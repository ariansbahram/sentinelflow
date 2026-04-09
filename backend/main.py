from fastapi import FastAPI, HTTPException
from sample_alerts import alerts
from agent import triage_alert
from storage import get_memory

app = FastAPI(title="SentinelFlow API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SentinelFlow backend is running."}

@app.get("/alerts")
def get_alerts():
    return alerts

@app.post("/triage/{alert_id}")
def triage(alert_id: int):
    alert = next((a for a in alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return triage_alert(alert)

@app.get("/memory")
def memory():
    return get_memory()
