import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.state import AgentState
# ✅ 只保留 WebSocket 管理器，删除了 ssh_tool/local_cmd 的引用
from app.services.ws_manager import manager

llm = ChatOpenAI(
    model="qwen-max", 
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

SYSTEM_PROMPT = """
你是一个全能的 Windows 电脑管家。
你的职责是将用户的自然语言转换为 CMD 命令，通过远程连接下发给用户的电脑。

【常用指令映射】
1. 打开计算器 -> 执行 "calc"
2. 打开记事本 -> 执行 "notepad"
3. 查IP -> 执行 "ipconfig"
4. 浏览网页 -> 执行 "start https://www.baidu.com"
5. 创建文件夹 -> 执行 "mkdir <文件夹名>"

【安全准则】
1. 严禁执行 del, rd /s /q, format 等高危命令。
2. 如果用户请求危险操作，请直接拒绝。

【工具调用格式】
Action: run_remote_command
Action Input: <CMD命令>
"""

async def tech_node(state: AgentState):
    print("🔧 [Tech Node] 思考中...")
    query = state['query']
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)]
    
    final_res = ""
    # ReAct 循环
    for _ in range(3):
        # 异步调用 LLM
        resp = await llm.ainvoke(messages)
        content = resp.content
        messages.append(AIMessage(content=content))
        
        # 解析工具调用
        if "Action: run_remote_command" in content:
            match = re.search(r"Action Input:\s*(.+)", content)
            if match:
                cmd = match.group(1).strip()
                print(f"📡 准备下发指令: {cmd}")
                
                # ✅ 通过 WebSocket 发给家里的电脑，并等待结果
                res = await manager.send_command(cmd)
                
                messages.append(HumanMessage(content=f"Observation: {res}"))
                continue
        
        final_res = content
        break
    
    return {"final_answer": final_res}