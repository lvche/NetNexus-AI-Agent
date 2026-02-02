from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.nodes.supervisor import supervisor_node
from app.nodes.tech_node import tech_node
from app.nodes.biz_node import biz_node

# 1. 初始化图
workflow = StateGraph(AgentState)

# 2. 添加节点
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("tech", tech_node)
workflow.add_node("biz", biz_node)

# 3. 设置起点
workflow.set_entry_point("supervisor")

# 4. 设置条件边 (路由逻辑)
def route_logic(state):
    if state["next_step"] == "TECH":
        return "tech"
    else:
        return "biz"

workflow.add_conditional_edges(
    "supervisor",
    route_logic,
    {
        "tech": "tech",
        "biz": "biz"
    }
)

# 5. 设置终点 (做完直接结束)
workflow.add_edge("tech", END)
workflow.add_edge("biz", END)

# 6. 编译图
app_graph = workflow.compile()