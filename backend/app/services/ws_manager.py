import asyncio
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # 存放活动的连接 (这里假设只有一个 worker，就是你家电脑)
        self.active_connection: WebSocket = None
        # 用来挂起请求，等待结果
        self.response_future: asyncio.Future = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection = websocket
        print("✅ [WS Manager] 本地电脑已连接！")

    def disconnect(self, websocket: WebSocket):
        self.active_connection = None
        if self.response_future and not self.response_future.done():
            self.response_future.cancel()
        print("❌ [WS Manager] 本地电脑断开连接")

    async def send_command(self, command: str):
        """发送命令并等待结果"""
        if not self.active_connection:
            return "⚠️ 错误：本地电脑未连接，无法执行命令。"

        # 1. 创建一个新的 Future 对象，相当于“空的收件箱”
        self.response_future = asyncio.Future()

        # 2. 发送指令
        print(f"☁️ [Cloud] 下发指令: {command}")
        await self.active_connection.send_text(command)

        # 3. 阻塞等待结果 (最多等 30 秒)
        try:
            result = await asyncio.wait_for(self.response_future, timeout=30.0)
            return result
        except asyncio.TimeoutError:
            return "❌ 执行超时：本地电脑没有在30秒内返回结果。"

    def resolve_response(self, response: str):
        """收到结果，填入收件箱"""
        if self.response_future and not self.response_future.done():
            self.response_future.set_result(response)

# 全局单例
manager = ConnectionManager()