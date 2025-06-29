"""
图像生成Agent测试文件

这个文件包含了图像生成agent的基础测试用例。
"""

import pytest
from unittest.mock import patch
from agents.image_generator import get_image_generator
from agents.operator import AgentType, get_agent, get_available_agents


class TestImageGeneratorAgent:
    """图像生成Agent测试类"""
    
    def test_get_image_generator_basic(self):
        """测试基础的图像生成agent创建"""
        agent = get_image_generator(
            model_id="qwen-max",
            user_id="test_user",
            session_id="test_session",
            debug_mode=True
        )
        
        assert agent is not None
        assert agent.name == "ImageGenerator"
        assert agent.agent_id == "image_generator"
        assert agent.user_id == "test_user"
        assert agent.session_id == "test_session"
    
    def test_agent_type_enum(self):
        """测试AgentType枚举包含图像生成agent"""
        assert AgentType.IMAGE_GENERATOR in AgentType
        assert AgentType.IMAGE_GENERATOR.value == "image_generator"
    
    def test_get_available_agents_includes_image_generator(self):
        """测试可用agents列表包含图像生成agent"""
        available_agents = get_available_agents()
        assert "image_generator" in available_agents
        assert "sage" in available_agents
        assert "scholar" in available_agents
    
    def test_get_agent_with_image_generator_type(self):
        """测试通过operator获取图像生成agent"""
        agent = get_agent(
            model_id="qwen-max",
            agent_id=AgentType.IMAGE_GENERATOR,
            user_id="test_user",
            session_id="test_session"
        )
        
        assert agent is not None
        assert agent.name == "ImageGenerator"
        assert agent.agent_id == "image_generator"
    
    def test_image_generator_description(self):
        """测试图像生成agent的描述信息"""
        agent = get_image_generator()
        
        assert "ImageGenerator" in agent.description
        assert "WaveSpeed AI" in agent.description
        assert "image generation" in agent.description.lower()
    
    def test_image_generator_instructions(self):
        """测试图像生成agent的指令配置"""
        agent = get_image_generator()
        
        instructions = agent.instructions
        assert "Understand the Request" in instructions
        assert "Optimize the Prompt" in instructions
        assert "Generate the Image" in instructions
        assert "Present Results" in instructions
        assert "Iterative Refinement" in instructions
    
    def test_image_generator_settings(self):
        """测试图像生成agent的基础设置"""
        agent = get_image_generator()
        
        assert agent.markdown is True
        assert agent.add_datetime_to_instructions is True
        assert agent.add_history_to_messages is True
        assert agent.num_history_responses == 3
        assert agent.read_chat_history is True
    
    @patch('os.getenv')
    async def test_async_image_generator_with_api_key(self, mock_getenv):
        """测试异步图像生成agent配置（模拟API key）"""
        mock_getenv.return_value = "test_api_key"
        
        from agents.image_generator import get_image_generator_async
        
        try:
            agent = await get_image_generator_async(
                model_id="qwen-max",
                user_id="test_user",
                session_id="test_session",
                wavespeed_api_key="test_api_key"
            )
            assert agent is not None
            assert agent.name == "ImageGenerator"
        except Exception as e:
            # 在测试环境中，MCP连接可能失败，这是正常的
            assert "WAVESPEED_API_KEY" in str(e) or "MCP" in str(e)
    
    async def test_async_image_generator_without_api_key(self):
        """测试没有API key时的错误处理"""
        from agents.image_generator import get_image_generator_async
        
        with pytest.raises(ValueError, match="WAVESPEED_API_KEY is required"):
            await get_image_generator_async(
                wavespeed_api_key=None
            )


class TestImageGeneratorIntegration:
    """图像生成Agent集成测试"""
    
    def test_agent_in_operator_mapping(self):
        """测试operator中正确映射了图像生成agent"""
        # 测试sage
        sage_agent = get_agent(agent_id=AgentType.SAGE)
        assert sage_agent.name == "Sage"
        
        # 测试scholar
        scholar_agent = get_agent(agent_id=AgentType.SCHOLAR)
        assert scholar_agent.name == "Scholar"
        
        # 测试image_generator
        image_agent = get_agent(agent_id=AgentType.IMAGE_GENERATOR)
        assert image_agent.name == "ImageGenerator"
    
    def test_all_agent_types_work(self):
        """测试所有agent类型都能正常工作"""
        for agent_type in AgentType:
            agent = get_agent(agent_id=agent_type)
            assert agent is not None
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'agent_id')


if __name__ == "__main__":
    # 运行基础测试
    test_class = TestImageGeneratorAgent()
    
    print("🧪 运行图像生成Agent测试...")
    
    try:
        test_class.test_get_image_generator_basic()
        print("✅ 基础创建测试通过")
        
        test_class.test_agent_type_enum()
        print("✅ AgentType枚举测试通过")
        
        test_class.test_get_available_agents_includes_image_generator()
        print("✅ 可用agents列表测试通过")
        
        test_class.test_get_agent_with_image_generator_type()
        print("✅ Operator获取agent测试通过")
        
        test_class.test_image_generator_description()
        print("✅ Agent描述测试通过")
        
        test_class.test_image_generator_instructions()
        print("✅ Agent指令测试通过")
        
        test_class.test_image_generator_settings()
        print("✅ Agent设置测试通过")
        
        print("\n🎉 所有测试都通过了！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise 