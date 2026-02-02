import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

# 获取 backend 根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "network_info.txt")
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

def get_retriever():
    """获取检索器单例"""
    embeddings = DashScopeEmbeddings(model="text-embedding-v1", dashscope_api_key=os.getenv("OPENAI_API_KEY"))
    
    if os.path.exists(DB_PATH):
        db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    else:
        # 初始化建库
        loader = TextLoader(DATA_PATH, encoding="utf-8")
        docs = CharacterTextSplitter(chunk_size=500, chunk_overlap=0).split_documents(loader.load())
        db = Chroma.from_documents(docs, embeddings, persist_directory=DB_PATH)
        
    return db.as_retriever(search_kwargs={"k": 1})

# 如果直接运行此文件，则初始化数据库
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    get_retriever()
    print("✅ 知识库初始化完成")