"""
图像生成Agent Playground服务 - 按照Agno官方MCP最佳实践

这个示例按照官方文档创建一个Web UI界面，用户可以通过浏览器与图像生成Agent交互。

参考：https://docs.agno.com/tools/mcp/mcp

运行前需要:
1. 确保已安装: uv pip install mcp wavespeed-mcp
2. 设置环境变量: export WAVESPEED_API_KEY=your_api_key_here
3. 确保数据库连接正常

使用方法:
python examples/image_generation_playground.py

然后访问: http://localhost:7007
"""

import asyncio
import os

import nest_asyncio
from agno.playground import Playground
from agno.tools.mcp import MCPTools

from agents.image_generator import get_image_generator

# 允许嵌套事件循环
nest_asyncio.apply()

agent_storage_file: str = "tmp/image_agents.db"


async def run_server() -> None:
    """运行图像生成Agent Playground服务器 - 官方最佳实践"""
    
    # 检查API密钥
    api_key = os.getenv("WAVESPEED_API_KEY")
    if not api_key:
        print("❌ 错误：请设置 WAVESPEED_API_KEY 环境变量")
        print("   export WAVESPEED_API_KEY=your_api_key_here")
        return

    print("🚀 启动图像生成Agent Playground服务（官方最佳实践）")
    print("=" * 60)
    print("📡 连接WaveSpeed MCP服务器...")
    
    try:
        # ✅ 按照官方文档：在服务器运行期间保持MCP连接
        async with MCPTools(command="wavespeed-mcp", timeout_seconds=30) as mcp_tools:
            print("✅ MCP连接成功！")
            
            # 创建图像生成Agent（不包含MCP工具）
            agent = get_image_generator(
                user_id="playground_user",
                session_id="playground_session",
                enable_mcp=True,  # 启用MCP功能描述
                debug_mode=True
            )
            
            # ✅ 按照官方最佳实践：在应用层添加MCP工具
            agent.tools = [mcp_tools]
            agent.name = "🎨 图像生成专家"

            print(f"🤖 Agent创建成功：{agent.name}")
            print(f"🛠️  可用工具：{[tool.name for tool in agent.tools]}")
            
            # 创建Playground
            playground = Playground(agents=[agent])
            app = playground.get_app()

            print("🌐 启动Web服务器...")
            print("📱 访问地址：http://localhost:7007")
            print("=" * 60)
            print("🎨 现在可以通过浏览器与图像生成Agent交互了！")
            print("💡 提示：尝试说 '帮我画一张夕阳下的大海'")
            print("=" * 60)

            # ✅ 在MCP上下文中运行服务器（保持连接活跃）
            playground.serve(app, host="0.0.0.0", port=7007)

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n💡 解决方案:")
        print("1. 确保WAVESPEED_API_KEY环境变量已设置")
        print("2. 确保API密钥有效")
        
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 确保已安装: uv pip install mcp wavespeed-mcp")
        print("2. 确保网络连接正常")
        print("3. 确保数据库连接正常")
        print("4. 确保端口7007未被占用")


if __name__ == "__main__":
    print("🎨 图像生成Agent Playground")
    print("📚 使用Agno官方MCP最佳实践")
    print("=" * 60)
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败：{e}") 