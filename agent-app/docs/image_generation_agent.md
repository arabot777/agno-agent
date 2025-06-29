# 图像生成Agent使用指南

## 概述

图像生成Agent是一个集成了WaveSpeed MCP (Model Context Protocol) 的智能代理，能够根据文本描述生成高质量的图像。该Agent结合了强大的自然语言理解能力和先进的图像生成技术。

## 功能特性

- 🎨 **文本到图像生成**: 根据详细的文本描述创建高质量图像
- 🖼️ **图像到图像转换**: 基于现有图像进行风格转换和增强
- 🎭 **多种艺术风格**: 支持写实、抽象、动漫等多种艺术风格
- ⚙️ **自定义参数**: 支持尺寸、质量、风格等详细配置
- 🔄 **迭代优化**: 支持基于反馈的图像精修和变体生成

## 安装和配置

### 1. 安装依赖

确保已安装wavespeed-mcp包：

```bash
pip install wavespeed-mcp
```

或者更新项目依赖：

```bash
cd agent-app
pip install -r requirements.txt
```

### 2. 配置API密钥

获取WaveSpeed API密钥并设置环境变量：

```bash
export WAVESPEED_API_KEY=your_api_key_here
```

### 3. 数据库配置

确保PostgreSQL数据库正常运行，Agent将创建 `image_generator_sessions` 表来存储会话历史。

## 使用方法

### API调用

通过REST API使用图像生成Agent：

```bash
curl -X POST "http://localhost:8000/agents/image_generator/runs" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "请生成一张夕阳下的大海图片，要有温暖的色调",
       "model": "qwen-max",
       "user_id": "user123",
       "session_id": "session456"
     }'
```

### 编程接口

```python
import asyncio
from agents.image_generator import get_image_generator_async

async def generate_image():
    # 创建agent实例
    agent = await get_image_generator_async(
        model_id="qwen-max",
        user_id="user123",
        session_id="session456",
        wavespeed_api_key="your_api_key"
    )
    
    # 生成图像
    response = await agent.arun("画一只可爱的小猫在花园里玩耍")
    print(response.content)

asyncio.run(generate_image())
```

### 示例脚本

运行提供的示例脚本：

```bash
cd agent-app
python examples/image_generation_example.py
```

## 提示词优化建议

为了获得最佳效果，建议使用详细的描述：

### ✅ 好的提示词示例

```
请生成一张高质量的数字艺术作品：一只橙色的小猫坐在开满鲜花的花园里，
阳光透过树叶洒下斑驳的光影，背景是柔和的绿色植物，整体风格温馨治愈，
细节丰富，8K分辨率，电影级光照
```

### ❌ 避免的提示词

```
画一只猫
```

### 提示词要素

1. **主体描述**: 清楚描述要画的主要对象
2. **风格指定**: 指明艺术风格（写实、卡通、油画等）
3. **环境背景**: 描述场景和环境
4. **光影效果**: 指定光照条件
5. **技术参数**: 分辨率、质量要求
6. **情感氛围**: 希望传达的情感

## Agent工作流程

1. **理解请求**: 分析用户的图像描述需求
2. **提示词优化**: 将自然语言转换为专业的生成提示词
3. **参数配置**: 选择合适的生成参数和设置
4. **图像生成**: 调用WaveSpeed API进行图像生成
5. **结果展示**: 展示生成的图像并提供说明
6. **迭代改进**: 根据用户反馈进行调整

## 配置选项

可以通过环境变量配置：

```bash
# WaveSpeed API配置
export WAVESPEED_API_KEY=your_api_key
export WAVESPEED_API_HOST=https://api.wavespeed.ai
export WAVESPEED_API_RESOURCE_MODE=url  # url, base64, local

# 日志配置
export WAVESPEED_LOG_LEVEL=INFO

# 输出路径配置
export WAVESPEED_MCP_BASE_PATH=~/Desktop
```

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: WAVESPEED_API_KEY is required for image generation
   ```
   解决方案: 确保正确设置了环境变量 `WAVESPEED_API_KEY`

2. **MCP服务器连接失败**
   ```
   错误: Failed to connect to MCP server
   ```
   解决方案: 确保已安装 `wavespeed-mcp` 包

3. **数据库连接错误**
   ```
   错误: could not connect to server
   ```
   解决方案: 检查PostgreSQL数据库连接配置

### 调试模式

启用调试模式获取更多日志信息：

```python
agent = await get_image_generator_async(debug_mode=True)
```

## 性能优化

- 使用会话管理减少重复初始化
- 批量处理多个图像生成请求
- 合理设置图像分辨率平衡质量和速度
- 使用连接池优化数据库访问

## 安全注意事项

- 妥善保管API密钥，不要在代码中硬编码
- 注意生成内容的合规性，避免违规内容
- 限制用户输入长度防止滥用
- 定期轮换API密钥

## 更新日志

- v1.0.0: 初始版本，支持基本的文本到图像生成
- 集成WaveSpeed MCP工具
- 支持千问模型作为对话引擎
- 支持PostgreSQL会话存储 