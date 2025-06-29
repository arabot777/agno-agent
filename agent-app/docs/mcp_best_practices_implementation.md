# 按照Agno官方最佳实践的MCP实现

## 🎯 官方文档参考

本实现严格按照 [Agno官方MCP文档](https://docs.agno.com/tools/mcp/mcp) 的最佳实践设计。

## ✅ 正确的架构设计

### 1. Agent设计（符合官方实践）

```python
# ✅ 正确：Agent不内部管理MCP连接
def get_image_generator() -> Agent:
    return Agent(
        name="ImageGenerator",
        tools=[],  # 空工具列表，MCP工具在应用层添加
        # ... 其他配置
    )
```

### 2. 应用层MCP管理（官方推荐）

```python
# ✅ 正确：在应用层管理MCP连接
async with MCPTools(command="wavespeed-mcp") as mcp_tools:
    agent = get_image_generator()
    agent.tools = [mcp_tools]  # 在应用层添加MCP工具
    response = await agent.arun("生成图片")
```

## 🏗️ 当前实现架构

### 1. 核心Agent (`agents/image_generator.py`)

- **标准Agent实现**：不包含内部MCP连接管理
- **双模式支持**：`enable_mcp` 参数控制功能描述
  - `enable_mcp=True`：描述包含MCP功能，假设工具会在应用层添加
  - `enable_mcp=False`：仅概念指导模式

### 2. API层 (`agents/operator.py`)

```python
# API返回仅概念指导的Agent
return get_image_generator(enable_mcp=False)
```

**原因**：API层直接管理MCP连接会增加复杂性，不符合官方最佳实践。

### 3. 应用层示例

#### Playground服务 (`examples/image_generation_playground.py`)

```python
# ✅ 正确：长生命周期MCP连接
async with MCPTools(command="wavespeed-mcp") as mcp_tools:
    agent = get_image_generator(enable_mcp=True)
    agent.tools = [mcp_tools]
    playground = Playground(agents=[agent])
    playground.serve(app)  # 在MCP上下文中运行服务
```

#### 脚本使用 (`examples/simple_mcp_test.py`)

```python
# ✅ 正确：脚本级MCP管理
async with MCPTools(command="wavespeed-mcp") as mcp_tools:
    agent = get_image_generator(enable_mcp=True)
    agent.tools = [mcp_tools]
    response = await agent.arun("生成图片")
```

## 📋 使用场景

### 1. 🎨 真实图像生成（需要MCP）

**使用Playground**：
```bash
export WAVESPEED_API_KEY=your_key
python examples/image_generation_playground.py
# 访问 http://localhost:7007
```

**使用脚本**：
```bash
export WAVESPEED_API_KEY=your_key
python examples/simple_mcp_test.py
```

### 2. 💡 概念指导（无需MCP）

**API调用**：
```bash
curl -X POST "http://localhost:8000/agents/image_generator/runs" \
     -H "Content-Type: application/json" \
     -d '{"message": "帮我优化一个画猫的提示词"}'
```

**直接使用**：
```python
agent = get_image_generator(enable_mcp=False)
response = await agent.arun("优化提示词")
```

## 🔧 配置管理

### 环境变量方式（推荐）

```bash
# 设置API密钥
export WAVESPEED_API_KEY=your_key

# 可选配置
export WAVESPEED_API_HOST=https://api.wavespeed.ai
export WAVESPEED_API_RESOURCE_MODE=url
```

### 配置文件

```json
// mcp_config.json - 用于Claude Desktop等客户端
{
  "mcpServers": {
    "Wavespeed": {
      "command": "wavespeed-mcp",
      "env": {
        "WAVESPEED_API_KEY": "your_key"
      }
    }
  }
}
```

## 🔍 验证工具

### 配置检查脚本

```bash
python scripts/check_mcp_config.py
```

输出示例：
```
🧪 WaveSpeed MCP配置检查
==================================================
🔍 检查环境变量配置...
  ✅ WAVESPEED_API_KEY: *** (WaveSpeed API密钥)
📁 检查配置文件...
  ✅ example.env: 存在
📦 检查MCP包安装...
  ✅ mcp: 已安装
  ✅ wavespeed-mcp: 命令可用
==================================================
🎉 配置检查通过！
```

## ❌ 避免的反模式

### 1. 在Agent内部管理MCP（错误）

```python
# ❌ 错误：不要在Agent内部管理MCP连接
class BadAgent(Agent):
    async def __aenter__(self):
        self.mcp_tools = MCPTools(command="wavespeed-mcp")
        await self.mcp_tools.__aenter__()  # 违反官方最佳实践
```

### 2. 在API中直接返回包含MCP的Agent（复杂）

```python
# ❌ 复杂：API层管理MCP会增加架构复杂性
def get_agent_with_mcp():  # 不推荐
    # 需要在API层管理异步上下文...
```

## 🎉 总结

当前实现**完全符合Agno官方MCP最佳实践**：

1. ✅ **Agent不内部管理MCP连接**
2. ✅ **在应用层管理MCP生命周期**
3. ✅ **使用异步上下文管理器**
4. ✅ **提供清晰的使用示例**
5. ✅ **支持多种使用场景**

这种设计确保了：
- **架构清晰**：职责分离明确
- **易于维护**：符合官方规范
- **灵活使用**：支持多种场景
- **资源安全**：正确的连接管理 