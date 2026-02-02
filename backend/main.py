from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # ★ 新增
from pydantic import BaseModel
from agent_v2 import run_agent

app = FastAPI(title="NetNexus AI API")

# ★ 新增：配置跨域，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境要改具体域名，开发环境用 * 偷懒
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"📩 收到 API 请求: {request.query}")
    try:
        result = run_agent(request.query)
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)