import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.state import AgentState
from app.services.rag_service import get_retriever

llm = ChatOpenAI(
    model="qwen-max", 
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

def biz_node(state: AgentState):
    print("📚 [Biz Node] 开始查询业务文档...")
    query = state['query']
    retriever = get_retriever()
    
    # 检索
    docs = retriever.invoke(query)
    context = "\n".join([d.page_content for d in docs]) or "无相关记录"
    
    # 回答
    template = "基于以下文档回答问题：\n{context}\n\n问题：{question}"
    chain = ChatPromptTemplate.from_template(template) | llm | StrOutputParser()
    res = chain.invoke({"context": context, "question": query})
    
    return {"final_answer": res}