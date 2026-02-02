import os
import sys

# ==========================================
# ★ 1. 最优先：加载环境变量 (解决报错的关键)
# ==========================================
from dotenv import load_dotenv, find_dotenv
# 强制寻找并加载 .env 文件
load_dotenv(find_dotenv(), override=True)

# ==========================================
# 2. 设置路径 (确保能导入 app 包)
# ==========================================
# 获取当前脚本所在目录 (backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

print("🚀 开始尝试生成 LangGraph 流程图...")

try:
    # ==========================================
    # 3. 导入你定义好的图
    # ==========================================
    # 环境变量加载后，这里导入就不会报错了
    from app.graph import app_graph
    print("✅ 成功加载 compiled graph (编译后的图)。")

    # ==========================================
    # 4. 执行绘图并保存
    # ==========================================
    output_filename = "netnexus_workflow.png"
    output_path = os.path.join(BASE_DIR, output_filename)

    print(f"🎨 正在渲染图像 (使用 Mermaid 引擎)...")
    
    # 获取图对象并绘制为 PNG
    png_data = app_graph.get_graph().draw_mermaid_png()

    with open(output_path, "wb") as f:
        f.write(png_data)

    print("-" * 30)
    print(f"🎉 成功！流程图已保存为: {output_filename}")
    print(f"📂 文件完整路径: {output_path}")
    print("-" * 30)

except ImportError as e:
    print("\n❌ 导入错误！")
    print(f"详情: {e}")

except Exception as e:
    print("\n❌ 生成图像失败！")
    print(f"详情: {e}")