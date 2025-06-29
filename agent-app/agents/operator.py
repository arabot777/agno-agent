from enum import Enum
from typing import List, Optional

from agents.sage import get_sage
from agents.scholar import get_scholar
from agents.image_generator import get_image_generator


class AgentType(Enum):
    SAGE = "sage"
    SCHOLAR = "scholar"
    IMAGE_GENERATOR = "image_generator"


def get_available_agents() -> List[str]:
    """Returns a list of all available agent IDs."""
    return [agent.value for agent in AgentType]


def get_agent(
    model_id: str = "gpt-4o",
    agent_id: Optional[AgentType] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
):
    """
    创建Agent实例
    
    现在IMAGE_GENERATOR提供真正的图像生成功能！
    - 内置WaveSpeed MCP集成
    - 自动处理API密钥和连接
    - 支持真实图像生成和概念指导
    
    如果设置了WAVESPEED_API_KEY环境变量，将提供完整的图像生成功能。
    如果未设置，将提供专业的概念指导和提示词优化。
    """
    if agent_id == AgentType.SAGE:
        return get_sage(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.IMAGE_GENERATOR:
        return get_image_generator(
            model_id=model_id, 
            user_id=user_id, 
            session_id=session_id, 
            debug_mode=debug_mode,
            auto_setup_mcp=True  # 启用内置MCP功能
        )
    else:
        return get_scholar(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
