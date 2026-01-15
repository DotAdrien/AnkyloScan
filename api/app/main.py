from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="AnkyloScan API 🦖", port=8001)

class ScanResult(BaseModel):
    ip: str
    hostname: str = "Inconnu"
    status: str
    open_ports: List[int]

db_mock = []

@app.get("/")
def home():
    return {"message": "AnkyloScan API tournant sur le port 8001 ! 🦖🔥"}

@app.post("/results")
def receive_results(result: ScanResult):
    db_mock.append(result.dict())
    return {"status": "success", "data": result}

@app.get("/results")
def get_results():
    return db_mock