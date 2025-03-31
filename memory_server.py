from fastapi import FastAPI
from pydantic import BaseModel
import json
import requests
from datetime import datetime

app = FastAPI()
memory_file = "memory.json"
gist_url = "https://gist.githubusercontent.com/dakaiones/e8d05fdf06b54c84af3ce888de092fb8/raw/memory_endpoint.json"
fallback_url = "https://dakaiones1.serveo.net"

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
        res = requests.get(gist_url, timeout=3)
        return res.json()
    except Exception as e:
        return {"error": "Failed to fetch endpoint", "detail": str(e)}

@app.post("/memory_proxy")
def memory_proxy(item: Memory):
    try:
        # 1. Gist에서 주소 가져오기
        endpoint_res = requests.get(gist_url, timeout=3)
        endpoint = endpoint_res.json().get("endpoint")

        if not endpoint:
            raise Exception("Gist returned no endpoint.")

        # 2. 로컬 주소 우선 요청 시도
        try:
            res = requests.post(f"{endpoint}/memory", json=item.dict(), timeout=3)
            return res.json()
        except:
            # 3. 실패 시 serveo 주소로 fallback
            fallback = f"{fallback_url}/memory"
            res = requests.post(fallback, json=item.dict(), timeout=5)
            return res.json()

    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/memory_proxy")
def memory_proxy_get(user_id: str):
    try:
        endpoint_res = requests.get(gist_url, timeout=3)
        endpoint = endpoint_res.json().get("endpoint")

        if not endpoint:
            raise Exception("Gist returned no endpoint.")

        try:
            res = requests.get(f"{endpoint}/memory", params={"user_id": user_id}, timeout=3)
            return res.json()
        except:
            fallback = f"{fallback_url}/memory"
            res = requests.get(fallback, params={"user_id": user_id}, timeout=5)
            return res.json()

    except Exception as e:
        return {"status": "error", "detail": str(e)}