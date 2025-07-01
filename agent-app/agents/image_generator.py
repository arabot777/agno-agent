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
    图像生成Agent - 支持运行时动态MCP初始化
    
    这个Agent会在首次使用时自动检测和初始化MCP连接，
    完美解决了Web框架中的MCP生命周期管理问题。
    """
    
    def __init__(self, **kwargs):
        self._mcp_tools = None
        self._mcp_initialized = False
        super().__init__(**kwargs)
    
    async def _ensure_mcp_ready(self):
        """确保MCP连接就绪 - 动态初始化"""
        if self._mcp_initialized:
            return
            
        api_key = os.getenv("WAVESPEED_API_KEY")
        if not api_key:
            print("💡 提示：设置 WAVESPEED_API_KEY 可启用真实图像生成功能")
            self._mcp_initialized = True  # 标记为已检查，避免重复提示
            return
            
        try:
            print("🔗 正在初始化图像生成服务...")
            self._mcp_tools = MCPTools(
                command="wavespeed-mcp",
                timeout_seconds=30,
                env={"WAVESPEED_API_KEY": api_key}
            )
            await self._mcp_tools.__aenter__()
            
            # 动态添加MCP工具到agent
            if self._mcp_tools not in self.tools:
                self.tools.append(self._mcp_tools)
            
            self._mcp_initialized = True
            print("✅ 图像生成服务已就绪，支持真实图像生成")
            
        except Exception as e:
            print(f"⚠️  图像生成服务初始化失败：{e}")
            print("   将提供概念指导和提示词优化服务")
            self._mcp_initialized = True  # 标记为已尝试
    
    async def arun(self, message: str, **kwargs):
        """运行Agent，首次使用时自动初始化MCP"""
        # 动态初始化MCP（如果需要且尚未初始化）
        if not self._mcp_initialized:
            await self._ensure_mcp_ready()
        
        try:
            return await super().arun(message, **kwargs)
        except Exception as e:
            # 处理MCP连接相关错误
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in [
                "closedresourceerror", "mcp", "wavespeed", "connection", 
                "timeout", "failed to call", "closed", "resource"
            ]):
                print("🔄 图像生成服务连接中断，重新建立连接中...")
                
                # 重置状态并重新初始化
                self._mcp_initialized = False
                if self._mcp_tools in self.tools:
                    self.tools.remove(self._mcp_tools)
                self._mcp_tools = None
                
                # 重新尝试初始化
                await self._ensure_mcp_ready()
                
                # 重新运行请求
                if self._mcp_initialized and self._mcp_tools:
                    return await super().arun(message, **kwargs)
                else:
                    print("   切换到概念指导模式继续服务...")
                    return await super().arun(message, **kwargs)
            
            raise


def get_image_generator(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> ImageGeneratorAgent:
    """
    创建图像生成Agent - 按照Agno官方最佳实践
    
    注意：按照官方文档建议，MCP工具应在应用层管理，而不是在Agent内部。
    
    Args:
        model_id: 模型ID
        user_id: 用户ID  
        session_id: 会话ID
        debug_mode: 调试模式
    
    Returns:
        ImageGeneratorAgent: 图像生成Agent实例
        
    Usage:
        # 在应用层使用MCP（推荐的官方方式）
        async with MCPTools(command="wavespeed-mcp") as mcp_tools:
            agent = get_image_generator()
            agent.tools = [mcp_tools]  # 在应用层添加MCP工具
            response = await agent.arun("生成一张猫的图片")
        
        # 或在Playground中使用（官方推荐）
        async def run_server():
            async with MCPTools(command="wavespeed-mcp") as mcp_tools:
                agent = get_image_generator()
                agent.tools = [mcp_tools]
                playground = Playground(agents=[agent])
                playground.serve(app)
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
    )

