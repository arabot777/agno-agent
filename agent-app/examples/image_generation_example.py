"""
图像生成Agent使用示例

这个示例展示了如何使用集成WaveSpeed MCP的图像生成agent。

运行前需要:
1. 安装wavespeed-mcp: pip install wavespeed-mcp
2. 设置环境变量: export WAVESPEED_API_KEY=your_api_key_here
3. 确保数据库连接正常

使用方法:
python examples/image_generation_example.py
"""

import asyncio
import os
from agents.image_generator import get_image_generator_async


async def main():
    """运行图像生成示例"""
    
    # 检查API key
    api_key = os.getenv("WAVESPEED_API_KEY")
    if not api_key:
        print("错误：请设置 WAVESPEED_API_KEY 环境变量")
        return
    
    try:
        # 创建图像生成agent（异步版本）
        agent = await get_image_generator_async(
            model_id="qwen-max",
            user_id="example_user",
            session_id="example_session",
            debug_mode=True,
            wavespeed_api_key=api_key
        )
        
        # 示例对话
        prompts = [
            "请生成一张夕阳下的大海图片，要有温暖的色调",
            "创建一幅现代艺术风格的城市夜景",
            "画一只可爱的小猫在花园里玩耍",
        ]
        
        for prompt in prompts:
            print(f"\n🎨 用户提示: {prompt}")
            print("=" * 50)
            
            # 运行agent
            response = await agent.arun(prompt, stream=False)
            print(f"🤖 Agent回应:\n{response.content}")
            print("\n" + "=" * 50)
            
            # 等待一秒避免API限制
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"错误: {e}")
        print("\n可能的解决方案:")
        print("1. 确保WAVESPEED_API_KEY环境变量已设置")
        print("2. 确保wavespeed-mcp已安装: pip install wavespeed-mcp")
        print("3. 确保数据库连接正常")


if __name__ == "__main__":
    print("🚀 图像生成Agent示例")
    print("=" * 50)
    asyncio.run(main()) 