#!/usr/bin/env python3
"""
图像生成Playground - 按照Agno官方MCP最佳实践

这个示例严格按照官方文档创建，展示如何正确使用MCP工具。
参考：https://docs.agno.com/tools/mcp/mcp
"""

import asyncio
from os import getenv
from textwrap import dedent

import nest_asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.mcp import MCPTools

# Allow nested event loops
nest_asyncio.apply()

agent_storage_file: str = "tmp/image_agents.db"


async def run_server() -> None:
    """运行图像生成Agent服务器 - 按照官方最佳实践"""
    
    # 检查API密钥
    wavespeed_api_key = getenv("WAVESPEED_API_KEY")
    if not wavespeed_api_key:
        print("❌ 错误：需要设置 WAVESPEED_API_KEY 环境变量")
        print("   请运行：export WAVESPEED_API_KEY=your_api_key")
        print("   然后重新运行这个脚本")
        return

    print("🔗 正在连接 WaveSpeed MCP 服务...")
    
    # 按照官方文档：使用MCP异步上下文管理器包围整个应用
    async with MCPTools(
        command="wavespeed-mcp",
        env={"WAVESPEED_API_KEY": wavespeed_api_key}
    ) as mcp_tools:
        print("✅ MCP连接建立成功")
        
        # 创建图像生成Agent
        agent = Agent(
            name="图像生成Agent",
            agent_id="image_generator_mcp", 
            tools=[mcp_tools],  # 在应用层添加MCP工具
            instructions=dedent("""\
                你是一个专业的图像生成助手，可以根据用户的描述创建高质量的图像。

                你的能力包括：
                • 文本到图像生成
                • 图像到图像转换  
                • 多种艺术风格支持
                • 智能提示词优化

                请用中文与用户交流，并提供专业的图像生成服务。
            """),
            model=OpenAIChat(
                id="qwen-max",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="sk-53b7f9ed398b41b4bc265e1d3172334d",
                role_map={
                    "system": "system", 
                    "user": "user", 
                    "assistant": "assistant", 
                    "tool": "tool"
                },
            ),
            storage=SqliteAgentStorage(
                table_name="image_generator_sessions",
                db_file=agent_storage_file,
                auto_upgrade_schema=True,
            ),
            add_history_to_messages=True,
            num_history_responses=3,
            add_datetime_to_instructions=True,
            markdown=True,
        )

        print("📝 图像生成Agent已配置MCP工具")
        print(f"🔧 可用工具: {[tool.name for tool in agent.tools if hasattr(tool, 'name')]}")
        
        # 创建Playground
        playground = Playground(agents=[agent])
        app = playground.get_app()

        print("🎉 图像生成Playground已启动")
        print("📱 访问 http://localhost:7007 来使用Web界面")
        print("💡 或者在终端中直接测试...")
        
        # 可选：在启动时进行简单测试
        try:
            print("\n🧪 正在进行连接测试...")
            response = await agent.arun("简单介绍一下你的图像生成能力", stream=False)
            print(f"✅ 测试成功：{response.content[:100]}...")
        except Exception as e:
            print(f"⚠️  测试时出现问题：{e}")
        
        print("\n🚀 启动Web服务器...")
        
        # 保持MCP连接活跃的情况下运行服务器
        playground.serve(app)


if __name__ == "__main__":
    print("🎨 WaveSpeed MCP 图像生成Playground")
    print("=" * 50)
    print("📖 按照 Agno 官方MCP最佳实践实现")
    print("🔗 参考：https://docs.agno.com/tools/mcp/mcp")
    print("=" * 50)
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        print("💡 请检查环境配置和API密钥设置") 