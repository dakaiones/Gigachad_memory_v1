from fastapi import FastAPI
from pydantic import BaseModel
import json
import os

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
    db[item.user_id] = item.message
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    return {"status": "saved"}

@app.get("/memory")
def get_memory(user_id: str):
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            db = json.load(f)
        return {"memory": db.get(user_id, "기억 없음")}
    except:
        return {"memory": "기억 파일 없음"}