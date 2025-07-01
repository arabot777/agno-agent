from os import getenv

from agno.playground import Playground

from agents.sage import get_sage
from agents.scholar import get_scholar
from agents.image_generator import get_image_generator
from teams.finance_researcher import get_finance_researcher_team
from teams.multi_language import get_multi_language_team
from workspace.dev_resources import dev_fastapi

# Router for the Playground Interface

# 创建所有Agent
sage_agent = get_sage(debug_mode=True)
scholar_agent = get_scholar(debug_mode=True)
image_generator_agent = get_image_generator(debug_mode=True)

# 创建团队
finance_researcher_team = get_finance_researcher_team(debug_mode=True)
multi_language_team = get_multi_language_team(debug_mode=True)

# 创建playground实例
playground = Playground(
    agents=[sage_agent, scholar_agent, image_generator_agent], 
    teams=[finance_researcher_team, multi_language_team]
)

# 注册服务端点
if getenv("RUNTIME_ENV") == "dev":
    playground.serve(f"http://localhost:{dev_fastapi.host_port}")

# 获取路由
playground_router = playground.get_async_router()

# 显示启动状态
print("🎉 Playground已启动")
print("🎨 图像生成Agent支持动态MCP初始化")
print("💡 首次使用时会自动检测并连接WaveSpeed服务")
print("🔗 设置 WAVESPEED_API_KEY 环境变量可启用真实图像生成功能")
