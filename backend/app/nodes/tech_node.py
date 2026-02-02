import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.state import AgentState
# 引入 WebSocket 管理器
from app.services.ws_manager import manager

llm = ChatOpenAI(
    model="qwen-max", 
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# ★★★ 把人设改成电脑管家 ★★★
SYSTEM_PROMPT = """
你是一个全能的 Windows 电脑管家。
你可以通过远程指令直接操控用户的电脑。

【常用指令映射】
1. 打开计算器 -> 执行 "calc"
2. 打开记事本 -> 执行 "notepad"
3. 查IP -> 执行 "ipconfig"
4. 关机/重启 -> 拒绝执行，回复太危险。
5. 创建文件/文件夹 -> 使用 "echo" 或 "mkdir"

【行为准则】
1. 直接转换自然语言为 CMD 命令。
2. 严禁执行 del, rd, format 等破坏性命令。

【工具格式】
Action: run_remote_command
Action Input: <CMD命令>
"""

# 注意：这里改成 async def
async def tech_node(state: AgentState):
    print("🔧 [Tech Node] 准备远程控制...")
    query = state['query']
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)]
    
    final_res = ""
    for _ in range(3):
        resp = await llm.ainvoke(messages) # 使用异步调用
        content = resp.content
        messages.append(AIMessage(content=content))
        
        if "Action: run_remote_command" in content:
            match = re.search(r"Action Input:\s*(.+)", content)
            if match:
                cmd = match.group(1).strip()
                
                # ★★★ 通过 WebSocket 下发给家里电脑 ★★★
                res = await manager.send_command(cmd)
                
                messages.append(HumanMessage(content=f"Observation: {res}"))
                continue
        
        final_res = content
        break
    
    return {"final_answer": final_res}