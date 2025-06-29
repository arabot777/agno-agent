"""
简化版图像生成Agent测试文件

这个文件测试不依赖MCP工具的基础图像生成agent功能。
"""

from agents.image_generator_simple import get_image_generator_simple


class TestSimpleImageGeneratorAgent:
    """简化版图像生成Agent测试类"""
    
    def test_get_simple_image_generator_basic(self):
        """测试基础的简化图像生成agent创建"""
        agent = get_image_generator_simple(
            model_id="qwen-max",
            user_id="test_user",
            session_id="test_session",
            debug_mode=True
        )
        
        assert agent is not None
        assert agent.name == "ImageGeneratorSimple"
        assert agent.agent_id == "image_generator_simple"
        assert agent.user_id == "test_user"
        assert agent.session_id == "test_session"
    
    def test_simple_image_generator_description(self):
        """测试简化版图像生成agent的描述信息"""
        agent = get_image_generator_simple()
        
        assert "ImageGeneratorSimple" in agent.description
        assert "simplified version" in agent.description.lower()
        assert "image generation" in agent.description.lower()
        assert "concepts" in agent.description.lower()
    
    def test_simple_image_generator_instructions(self):
        """测试简化版图像生成agent的指令配置"""
        agent = get_image_generator_simple()
        
        instructions = agent.instructions
        assert "Understand the Request" in instructions
        assert "Optimize the Prompt" in instructions
        assert "Provide Guidance" in instructions
        assert "Educational Response" in instructions
        assert "Note Limitations" in instructions
    
    def test_simple_image_generator_settings(self):
        """测试简化版图像生成agent的基础设置"""
        agent = get_image_generator_simple()
        
        assert agent.markdown is True
        assert agent.add_datetime_to_instructions is True
        assert agent.add_history_to_messages is True
        assert agent.num_history_responses == 3
        assert agent.read_chat_history is True
    
    def test_simple_image_generator_tools(self):
        """测试简化版图像生成agent工具配置"""
        agent = get_image_generator_simple()
        
        # 简化版本不应该有任何工具
        assert agent.tools == []


if __name__ == "__main__":
    # 运行基础测试
    test_class = TestSimpleImageGeneratorAgent()
    
    print("🧪 运行简化版图像生成Agent测试...")
    
    try:
        test_class.test_get_simple_image_generator_basic()
        print("✅ 基础创建测试通过")
        
        test_class.test_simple_image_generator_description()
        print("✅ Agent描述测试通过")
        
        test_class.test_simple_image_generator_instructions()
        print("✅ Agent指令测试通过")
        
        test_class.test_simple_image_generator_settings()
        print("✅ Agent设置测试通过")
        
        test_class.test_simple_image_generator_tools()
        print("✅ Agent工具配置测试通过")
        
        print("\n🎉 所有简化版测试都通过了！")
        print("📝 注意：这是简化版本，不包含实际的图像生成功能")
        print("🔧 要使用完整功能，需要正确配置MCP工具和WaveSpeed API")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise 