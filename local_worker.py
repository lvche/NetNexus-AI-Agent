import asyncio
import websockets
import subprocess
import platform

# ★★★ 连接地址 ★★★
# 如果你现在还在本地测试，就用 ws://127.0.0.1:8000/ws/agent
# 等你要面试时，改成 ws://<你的云服务器IP>:8000/ws/agent
SERVER_URL = "ws://127.0.0.1:8000/ws/agent"

async def run_cmd(cmd):
    """在本地执行 CMD 命令"""
    print(f"⚙️ 执行: {cmd}")
    
    # 简单的安全过滤
    if any(x in cmd.lower() for x in ["del", "rm", "format", "shutdown"]):
        return "❌ 危险指令已拦截"

    try:
        # 异步执行子进程
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        # Windows 中文乱码处理 (GBK 转 UTF8)
        encoding = 'gbk' if platform.system() == "Windows" else 'utf-8'
        
        if stdout:
            return stdout.decode(encoding, errors='ignore').strip()
        if stderr:
            return f"Error: {stderr.decode(encoding, errors='ignore').strip()}"
        return "执行成功"
    except Exception as e:
        return f"系统错误: {e}"

async def main():
    print(f"🚀 正在连接云端: {SERVER_URL} ...")
    while True:
        try:
            async with websockets.connect(SERVER_URL) as ws:
                print("✅ 已连接！等待指令...")
                while True:
                    # 1. 收指令
                    cmd = await ws.recv()
                    print(f"📩 收到: {cmd}")
                    
                    # 2. 干活
                    result = await run_cmd(cmd)
                    
                    # 3. 回传
                    await ws.send(result)
                    print("📤 结果已回传")
        except Exception as e:
            print(f"⚠️ 连接断开，3秒后重连... {e}")
            await asyncio.sleep(3)

if __name__ == "__main__":
    # 需要先 pip install websockets
    asyncio.run(main())