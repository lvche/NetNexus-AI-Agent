import sys
import os
from dotenv import load_dotenv, find_dotenv

# 1. 路径与环境变量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
load_dotenv(find_dotenv(), override=True)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import app_graph
# 引入刚才写的 manager
from app.services.ws_manager import manager 

app = FastAPI(title="NetNexus Remote Control")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket 接口 (让家里电脑连这个) ---
@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 这里的死循环是用来接收电脑回传的“执行结果”
            data = await websocket.receive_text()
            print(f"📩 [Cloud] 收到回传: {data[:50]}...")
            manager.resolve_response(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- HTTP 聊天接口 (给手机App用的) ---
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"📱 [App] 收到请求: {request.query}")
    try:
        inputs = {"query": request.query}
        # invoke 是同步的，但我们的 manager 是 async 的
        # LangGraph 会自动处理 async node，或者我们需要用 ainvoke
        result = await app_graph.ainvoke(inputs)
        return ChatResponse(response=result["final_answer"])
    except Exception as e:
        print(f"❌ 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 注意：Host 设为 0.0.0.0 才能让局域网或公网访问
    uvicorn.run(app, host="0.0.0.0", port=8000)