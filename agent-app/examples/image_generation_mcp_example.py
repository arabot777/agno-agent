"""
使用Agno官方MCP方式的图像生成Agent示例

这个示例展示了如何按照Agno官方文档使用MCP工具进行图像生成。

运行前需要:
1. 确保已安装: uv pip install mcp wavespeed-mcp
2. 设置环境变量: export WAVESPEED_API_KEY=your_api_key_here
3. 确保数据库连接正常

使用方法:
python examples/image_generation_mcp_example.py
"""

import asyncio
import os
from agents.image_generator import get_image_generator


async def main():
    """运行MCP图像生成示例"""
    
    # 检查API key
    api_key = os.getenv("WAVESPEED_API_KEY")
    if not api_key:
        print("❌ 错误：请设置 WAVESPEED_API_KEY 环境变量")
        print("   export WAVESPEED_API_KEY=your_api_key_here")
        return
    
    print("🚀 使用Agno官方MCP方式进行图像生成")
    print("=" * 60)
    
    try:
        # 使用Agno官方推荐的MCP方式创建agent
        print("📡 正在连接WaveSpeed MCP服务器...")
        agent = await get_image_generator(
            model_id="qwen-max",
            user_id="mcp_example_user",
            session_id="mcp_example_session",
            debug_mode=True,
            wavespeed_api_key=api_key
        )
        
        print("✅ MCP连接成功！")
        print("=" * 60)
        
        # 示例对话
        prompts = [
            "请生成一张夕阳下的大海图片，要有温暖的色调",
            "创建一幅现代艺术风格的城市夜景",
            "画一只可爱的小猫在花园里玩耍，卡通风格",
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n🎨 示例 {i}: {prompt}")
            print("-" * 60)
            
            # 运行agent
            response = await agent.arun(prompt, stream=False)
            print(f"🤖 Agent回应:\n{response.content}")
            print("\n" + "=" * 60)
            
            # 等待一秒避免API限制
            await asyncio.sleep(1)
            
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n💡 解决方案:")
        print("1. 确保WAVESPEED_API_KEY环境变量已设置")
        print("2. 确保API密钥有效")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 确保已安装: uv pip install mcp wavespeed-mcp")
        print("2. 确保网络连接正常")
        print("3. 确保数据库连接正常")
        print("4. 确保wavespeed-mcp命令可用")


async def test_mcp_connection():
    """测试MCP连接"""
    print("🔍 测试MCP连接...")
    
    try:
        from agno.tools.mcp import MCPTools
        
        # 简单测试MCP工具是否可用
        async with MCPTools(command="wavespeed-mcp --help", timeout_seconds=30) as mcp_tools:
            print("✅ MCP工具连接成功")
            print(f"   工具实例: {type(mcp_tools).__name__}")
            return True
            
    except Exception as e:
        print(f"❌ MCP连接失败: {e}")
        return False


if __name__ == "__main__":
    print("🧪 图像生成Agent MCP示例")
    print("=" * 60)
    
    # 先测试MCP连接
    if asyncio.run(test_mcp_connection()):
        print("\n🎯 开始图像生成示例...")
        asyncio.run(main())
    else:
        print("\n❌ MCP连接测试失败，请检查环境配置") 