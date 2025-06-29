"""
简单的MCP图像生成测试脚本 - 按照Agno官方最佳实践

这个脚本演示了按照官方文档的正确MCP使用方式：在应用层管理MCP连接。

参考：https://docs.agno.com/tools/mcp/mcp

使用方法:
export WAVESPEED_API_KEY=your_api_key_here
python examples/simple_mcp_test.py
"""

import asyncio
import os

from agno.tools.mcp import MCPTools

from agents.image_generator import get_image_generator
from agents.settings import agent_settings


async def test_image_generation():
    """测试图像生成功能 - 按照官方最佳实践"""
    
    # 检查API密钥
    api_key = os.getenv("WAVESPEED_API_KEY")
    if not api_key:
        print("❌ 错误：请设置 WAVESPEED_API_KEY 环境变量")
        print("   export WAVESPEED_API_KEY=your_api_key_here")
        return

    print("🧪 开始MCP图像生成测试（官方最佳实践）")
    print("=" * 50)
    
    try:
        # ✅ 正确的MCP使用方式：按照官方文档在应用层管理连接
        async with MCPTools(command="wavespeed-mcp", timeout_seconds=30) as mcp_tools:
            print("✅ MCP连接成功")
            
            # 创建Agent（不包含MCP工具）
            agent = get_image_generator(
                model_id=agent_settings.qwen_max,
                user_id="test_user",
                session_id="test_session",
                debug_mode=True
            )
            
            # ✅ 按照官方最佳实践：在应用层添加MCP工具
            agent.tools = [mcp_tools]
            
            print("🤖 Agent创建成功")
            print(f"🛠️  可用工具：{len(agent.tools)}个")
            
            # 测试提示词
            test_prompts = [
                "请生成一张夕阳的图片",
                "画一只可爱的小猫",
            ]
            
            for i, prompt in enumerate(test_prompts, 1):
                print(f"\n🎨 测试 {i}: {prompt}")
                print("-" * 40)
                
                try:
                    # 在MCP连接的上下文中执行
                    response = await agent.arun(prompt, stream=False)
                    print(f"✅ 响应：{response.content[:200]}...")
                    
                except Exception as e:
                    print(f"❌ 测试失败：{e}")
                
                # 短暂休息
                await asyncio.sleep(2)
            
            print("\n🎉 测试完成！")
            
    except Exception as e:
        print(f"❌ MCP连接失败：{e}")
        print("\n💡 可能的解决方案：")
        print("1. 检查wavespeed-mcp是否正确安装")
        print("2. 检查API密钥是否有效")
        print("3. 检查网络连接")


async def test_without_mcp():
    """测试不使用MCP的概念指导模式"""
    print("\n🧪 测试概念指导模式（无MCP）")
    print("=" * 50)
    
    # 创建不使用MCP的Agent
    agent = get_image_generator(
        model_id=agent_settings.qwen_max,
        user_id="test_user_no_mcp",
        session_id="test_session_no_mcp",
        auto_setup_mcp=False,  # 不自动设置MCP
        debug_mode=True
    )
    
    print("🤖 Agent创建成功（概念指导模式）")
    print(f"🛠️  工具数量：{len(agent.tools)}个（预期为0）")
    
    try:
        response = await agent.arun("帮我优化一个画猫的提示词", stream=False)
        print(f"✅ 概念指导响应：{response.content[:200]}...")
    except Exception as e:
        print(f"❌ 概念指导测试失败：{e}")


if __name__ == "__main__":
    asyncio.run(test_image_generation())
    asyncio.run(test_without_mcp()) 