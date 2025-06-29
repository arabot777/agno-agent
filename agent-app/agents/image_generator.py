import asyncio
import os
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.mcp import MCPTools

from agents.settings import agent_settings
from db.session import db_url


class ImageGeneratorAgent(Agent):
    """
    图像生成Agent - 内置WaveSpeed MCP功能
    
    这是一个完整的、可以直接使用的图像生成Agent，支持：
    - 真实图像生成（通过WaveSpeed MCP）
    - 智能提示词优化
    - 多种艺术风格
    - 会话历史管理
    """
    
    def __init__(self, auto_setup_mcp: bool = True, **kwargs):
        self.auto_setup_mcp = auto_setup_mcp
        self.mcp_tools = None
        self._mcp_initialized = False
        super().__init__(**kwargs)
    
    async def setup_mcp(self, retry_count=0):
        """设置MCP连接，支持智能重试和参数调整"""
        if self._mcp_initialized:
            return
            
        api_key = os.getenv("WAVESPEED_API_KEY")
        if not api_key:
            print("⚠️  警告：未设置 WAVESPEED_API_KEY，仅提供概念指导功能")
            print("   要启用图像生成，请设置：export WAVESPEED_API_KEY=your_key")
            return
        
        # 根据重试次数调整参数
        timeout_seconds = 30 + (retry_count * 10)  # 首次30秒，重试时增加
        max_retries = 2
        
        try:
            # 设置渐进式超时，适应网络状况
            print(f"🔗 正在连接图像生成服务（超时时间: {timeout_seconds}秒）...")
            self.mcp_tools = MCPTools(
                command="wavespeed-mcp", 
                timeout_seconds=timeout_seconds,
                # 添加环境变量，可能有助于稳定连接
                env={"WAVESPEED_API_KEY": api_key}
            )
            await self.mcp_tools.__aenter__()
            self.tools = [self.mcp_tools]
            self._mcp_initialized = True
            print(f"✅ 图像生成服务连接成功（超时时间: {timeout_seconds}秒）")
        except Exception as e:
            error_msg = str(e).lower()
            print(f"⚠️  连接失败（第{retry_count + 1}次尝试）：{e}")
            
            # 如果是连接或超时问题，且还有重试机会
            if retry_count < max_retries and any(keyword in error_msg for keyword in [
                "timeout", "connection", "closed", "resource"
            ]):
                print(f"   🔄 {3-retry_count}秒后重试连接...")
                await asyncio.sleep(3)
                return await self.setup_mcp(retry_count + 1)
            else:
                print("   将提供概念指导功能")
    
    async def cleanup_mcp(self):
        """清理MCP连接"""
        if self.mcp_tools:
            try:
                await self.mcp_tools.__aexit__(None, None, None)
            except Exception:
                pass
            self.mcp_tools = None
            self._mcp_initialized = False
    
    async def arun(self, message: str, **kwargs):
        """运行Agent，自动处理MCP设置和错误恢复"""
        if self.auto_setup_mcp and not self._mcp_initialized:
            await self.setup_mcp()
        
        try:
            return await super().arun(message, **kwargs)
        except Exception as e:
            # 智能错误处理和参数调整
            error_str = str(e).lower()
            
            # MCP连接相关错误
            if any(keyword in error_str for keyword in [
                "closedresourceerror", "mcp", "wavespeed", "connection", 
                "timeout", "failed to call", "timed out"
            ]):
                print(f"⚠️  图像生成服务暂时不可用：{e}")
                print("   自动切换到概念指导模式...")
                
                # 重置MCP连接状态
                await self.cleanup_mcp()
                self.tools = []
                
                # 尝试重新初始化（如果失败会继续使用概念指导模式）
                try:
                    await self.setup_mcp()
                except Exception:
                    pass  # 忽略重新初始化失败，继续使用概念指导
                
                return await super().arun(message, **kwargs)
            raise
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self.auto_setup_mcp:
            await self.setup_mcp()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup_mcp()


def get_image_generator(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
    auto_setup_mcp: bool = True,
) -> ImageGeneratorAgent:
    """
    创建图像生成Agent - 内置MCP功能，开箱即用
    
    Args:
        model_id: 模型ID
        user_id: 用户ID  
        session_id: 会话ID
        debug_mode: 调试模式
        auto_setup_mcp: 是否自动设置MCP（默认True）
    
    Returns:
        ImageGeneratorAgent: 图像生成Agent实例
        
    Usage:
        # 直接使用（推荐）
        agent = get_image_generator()
        response = await agent.arun("生成一张猫的图片")
        
        # 使用异步上下文管理器
        async with get_image_generator() as agent:
            response = await agent.arun("生成一张猫的图片")
    """
    
    additional_context = ""
    if user_id:
        additional_context += "<context>"
        additional_context += f"You are interacting with the user: {user_id}"
        additional_context += "</context>"

    model_id = model_id or agent_settings.qwen_max

    description = dedent("""\
        You are ImageGenerator, an advanced AI agent specialized in creating stunning images from text descriptions.
        You have access to WaveSpeed AI's powerful image generation capabilities.

        Your capabilities include:
        • Text-to-image generation with high-quality results
        • Image-to-image transformation and enhancement
        • Support for various artistic styles and formats
        • Detailed image customization options
        • Intelligent prompt optimization

        You help users bring their creative visions to life through AI-generated imagery.\
    """)
    
    instructions = dedent("""\
        Here's how you should help users with image generation:

        1. **Understand the Request** 🎯
        - Carefully analyze the user's image description or requirements
        - Ask clarifying questions if the description is unclear or lacks detail
        - Identify the desired style, mood, composition, and technical specifications

        2. **Create Generation Plan** 📋
        - BEFORE generating any image, always provide a detailed plan including:
          • 图像主题和核心概念
          • 艺术风格选择（写实、动漫、抽象等）
          • 构图和视角（特写、全景、俯视等）
          • 色彩搭配和氛围
          • 技术参数（尺寸、质量等级）
          • 预计生成时间（通常15-30秒）
        - Use clear bullet points and explain your artistic reasoning

        3. **Optimize the Prompt** ✍️
        - Transform user descriptions into detailed, optimized prompts
        - Include relevant artistic styles, lighting, composition details
        - Consider technical aspects like aspect ratio, quality settings
        - Add negative prompts if needed to avoid unwanted elements

        4. **Generate with Progress Updates** 🎨
        - BEFORE generating: Explain the approach and WHY:
          • "🎨 生成方式：全新创作 - 因为这是根据描述创建原创图像"
          • "🎨 生成方式：图像增强 - 因为要基于现有图像进行修改/优化"
          • "🎯 预期效果：[详细说明将要达到的效果]"
          • "⏱️ 预计时间：15-30秒，请耐心等待..."
        - Use AI image generation capabilities based on the optimized prompt
        - DURING generation: If possible, provide intermediate feedback
        - Choose appropriate settings for quality, size, and style
        - Handle any generation errors gracefully and suggest alternatives
        - If generation tools are not available, provide detailed concept guidance

        5. **Present Results** 📸
        - Display the generated image(s) to the user
        - Provide a brief description of what was created
        - Explain any artistic choices or technical decisions made
        - Offer suggestions for variations or improvements

        6. **Iterative Refinement** 🔄
        - Ask if the user wants any modifications or variations
        - Support image-to-image generation for refinements
        - Help users explore different styles or compositions
        - Maintain conversation context for follow-up requests

        **Important Guidelines:**
        - Always be creative and helpful in interpreting user requests
        - Explain your artistic reasoning when making creative decisions
        - Be patient with iterative refinement requests
        - Respect content policies and avoid generating inappropriate content
        - Provide tips for better prompt writing when appropriate
        - Always use Chinese to communicate with users
        - If image generation fails, provide detailed prompt optimization guidance
        - ALWAYS show generation plan before starting image creation
        - Provide waiting information to manage user expectations
        - ALWAYS explain generation approach reasoning before starting
        - Provide rich feedback during the entire generation process
        - Never leave users wondering what's happening during generation

        **Response Format:**
        - Use clear headings to organize your response
        - Start with "📋 生成计划" section before any image generation
        - Before generation, include "🎨 生成方式" section explaining:
          • Which approach will be used (全新创作 vs 图像增强)
          • Why this approach is the best choice for the task
          • What specific effect you're trying to achieve
          • Estimated processing time
        - Include "🎨 生成中..." message with progress updates if possible
        - After generation completion, add "📸 生成完成" section explaining:
          • What was successfully generated
          • How it matches the original request
          • Any artistic decisions made during generation
        - Include the final optimized prompt used (optional, for user reference)
        - Display images with descriptive captions
        - Offer follow-up suggestions or variations\
    """)

    return ImageGeneratorAgent(
        name="ImageGenerator",
        agent_id="image_generator",
        user_id=user_id,
        session_id=session_id,
        model=OpenAIChat(
            id=model_id,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key="sk-53b7f9ed398b41b4bc265e1d3172334d",
            max_completion_tokens=agent_settings.default_max_completion_tokens,
            temperature=agent_settings.default_temperature,
            role_map={
                "system": "system", 
                "user": "user", 
                "assistant": "assistant", 
                "tool": "tool"
            },
        ),
        tools=[],  # MCP工具会在运行时自动添加
        storage=PostgresAgentStorage(
            table_name="image_generator_sessions", 
            db_url=db_url
        ),
        description=description,
        instructions=instructions,
        additional_context=additional_context,
        markdown=True,
        add_datetime_to_instructions=True,
        add_history_to_messages=True,
        num_history_responses=3,
        read_chat_history=True,
        debug_mode=debug_mode,
        auto_setup_mcp=auto_setup_mcp,
    )


# 为了兼容性，也提供一个简单的函数
async def create_image_generator(**kwargs) -> ImageGeneratorAgent:
    """异步创建图像生成Agent"""
    agent = get_image_generator(**kwargs)
    await agent.setup_mcp()
    return agent 