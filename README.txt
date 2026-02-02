# 🛡️ NetNexus - 智能网络运维与诊断平台

> 基于 LLM (Qwen-Max) + ReAct 架构的自动化网络运维助手，实现 "自然语言 -> 交换机 CLI" 的端到端排查。

## 📖 项目简介
针对传统网络运维 CLI 门槛高、排查效率低的问题，本项目构建了一个智能运维 Agent。
- **用户**：可以通过自然语言（如"检查接口状态"）下达指令。
- **AI**：自动拆解需求，通过 SSH 连接设备，执行 CLI 命令并分析回显。
- **架构**：采用 ReAct (Reasoning + Acting) 范式，确保操作的逻辑性与准确性。

## 🛠️ 技术栈
- **大模型层**: LangChain, Qwen-Max (通义千问), ReAct Agent
- **后端**: Python, FastAPI, Netmiko (SSH), Pydantic
- **前端**: Vue 3, Vite, Axios
- **工具**: Python-dotenv (安全配置), Mock Server (设备仿真)

## 🚀 快速开始

### 1. 后端启动
```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 配置 .env 文件 (填入 OPENAI_API_KEY)
# 启动 API 服务
python main.py
# (可选) 启动模拟设备
python mock_device.py


### 2. 前端启动
cd frontend
npm install
npm run dev