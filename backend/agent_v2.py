import os
import re
from dotenv import load_dotenv, find_dotenv
# 强制加载环境变量
load_dotenv(find_dotenv(), override=True)

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from netmiko import ConnectHandler

# ==========================================
# 1. 配置
# ==========================================
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE")

llm = ChatOpenAI(
    model="qwen-max", 
    temperature=0,
    api_key=api_key,
    base_url=base_url
)

# ==========================================
# 2. 定义工具
# ==========================================
def run_cli_command(command: str):
    print(f"\n🔌 [系统执行命令]: {command}")
    device = {
        'device_type': 'cisco_ios',
        'host': '127.0.0.1',
        'port': 2222,
        'username': 'admin',
        'password': 'cisco',
        'fast_cli': False, 
    }
    try:
        with ConnectHandler(**device) as net_connect:
            return net_connect.send_command(command)
    except Exception as e:
        return f"Error: {e}"

# ==========================================
# 3. 核心逻辑 (V3 智能结束版)
# ==========================================
SYSTEM_PROMPT = """
你是一个网络运维专家。
【工具使用规则】
如果你需要执行命令，请严格按照以下格式输出：
Action: run_cli_command
Action Input: <命令>

【重要】
设备只支持简写命令，例如请用 'show ip int brief' 而不是全称。
如果不需要执行命令，请直接回答用户的问题即可。
"""

def run_agent(user_query):
    # ★ 看到这个 V3 就说明代码更新成功了
    print("🤖 Agent V3 (智能结束版) 启动...") 
    print(f"👤 用户: {user_query}")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_query)
    ]
    
    for i in range(5):
        print(f"\n🔄 [第 {i+1} 轮交互]...")
        
        # 1. AI 思考
        response = llm.invoke(messages)
        content = response.content
        print(f"🧠 AI 说: {content}")
        
        messages.append(AIMessage(content=content))
        
        # 2. 判断逻辑
        # 如果包含 Action，说明要干活
        if "Action: run_cli_command" in content:
            match = re.search(r"Action Input:\s*(.+)", content)
            if match:
                cmd = match.group(1).strip()
                tool_result = run_cli_command(cmd)
                print(f"📄 [结果]: {tool_result[:50]}...")
                
                # 把结果喂给 AI，让它继续下一轮思考
                messages.append(HumanMessage(content=f"Observation: {tool_result}"))
                continue
        
        # ★ 关键修改：如果 AI 没说要 Action，那它就是在回答用户，直接结束！
        print("\n✅ AI 已给出最终回复，任务结束。")
        return content

    return "❌ 超过最大循环次数"

if __name__ == "__main__":
    # 确保 mock_device.py 正在运行
    run_agent("请帮我检查一下接口状态，告诉我哪个接口是 UP 的？")