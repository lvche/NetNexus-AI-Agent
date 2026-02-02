from typing import TypedDict, Annotated

class AgentState(TypedDict):
    query: str          # 用户原始问题
    final_answer: str   # 最终给用户的回复
    next_step: str      # 下一步去哪里 (TECH / BIZ / END)