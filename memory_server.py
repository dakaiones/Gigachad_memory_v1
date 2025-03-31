from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
import requests
from datetime import datetime

app = FastAPI()
memory_file = "memory.json"

class Memory(BaseModel):
    user_id: str
    message: str

@app.post("/memory")
def save_memory(item: Memory):
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        db = {}

    if item.user_id not in db:
        db[item.user_id] = []

    db[item.user_id].append({
        "time": datetime.now().isoformat(),
        "message": item.message
    })

    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    return {"status": "saved"}

@app.get("/memory")
def get_memory(user_id: str):
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            db = json.load(f)
        return {"memory": db.get(user_id, [])}
    except:
        return {"memory": []}

@app.get("/get_memory_endpoint")
def get_memory_endpoint():
    try:
        # 여기에 본인의 Gist RAW 주소를 입력하세요
        gist_url = "https://gist.githubusercontent.com/dakaiones/e8d05fdf06b54c84af3ce888de092fb8/raw/memory_endpoint.json"
        response = requests.get(gist_url, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": "Failed to fetch endpoint", "detail": str(e)}