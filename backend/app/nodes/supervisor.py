import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.state import AgentState

llm = ChatOpenAI(
    model="qwen-max", 
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

def supervisor_node(state: AgentState):
    """
    路由节点：分析用户意图，决定下一步。
    """
    print(f"🧭 [Supervisor] 分析意图: {state['query']}")
    
    prompt = ChatPromptTemplate.from_template("""
    你是一个任务路由助手。
    用户问题: "{query}"
    
    请判断该问题属于哪类：
    1. TECH: 涉及设备操作、接口状态、版本查询、Ping测试等。
    2. BIZ: 涉及公司静态信息、WiFi密码、IP规划、SOP流程、联系人。
    
    只输出 'TECH' 或 'BIZ'。
    """)
    
    chain = prompt | llm
    result = chain.invoke({"query": state['query']})
    intent = result.content.strip().upper()
    
    if "TECH" in intent:
        return {"next_step": "TECH"}
    else:
        return {"next_step": "BIZ"}