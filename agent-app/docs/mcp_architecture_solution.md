# MCP架构问题和解决方案

## 问题分析

### 当前问题
在使用Agno的MCP工具时遇到的主要问题：

1. **连接生命周期管理**：`async with MCPTools(...)`上下文管理器在函数返回后会自动关闭连接
2. **异步上下文限制**：Agent在稍后调用工具时，MCP会话已经关闭
3. **架构不匹配**：试图在Agent工厂函数中管理MCP连接，但Agent的使用是在函数外部

### 错误示例
```python
async def get_image_generator(...):
    async with MCPTools(command="wavespeed-mcp") as mcp_tools:
        return Agent(tools=[mcp_tools])  # 连接在函数返回后关闭！
```

## 解决方案

### 方案1：在应用层管理MCP连接
```python
# 在应用主函数中管理MCP连接
async def main():
    async with MCPTools(command="wavespeed-mcp") as mcp_tools:
        agent = Agent(tools=[mcp_tools])
        # 在这个上下文中使用agent
        response = await agent.arun("生成图片")
```

### 方案2：创建长生命周期的MCP服务
```python
class ImageGeneratorService:
    def __init__(self):
        self.mcp_tools = None
        
    async def __aenter__(self):
        self.mcp_tools = MCPTools(command="wavespeed-mcp")
        await self.mcp_tools.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.mcp_tools:
            await self.mcp_tools.__aexit__(exc_type, exc_val, exc_tb)
            
    def get_agent(self, **kwargs):
        return Agent(tools=[self.mcp_tools], **kwargs)
```

### 方案3：使用Agno Playground（推荐）
按照官方文档，最佳实践是在Playground中使用MCP：

```python
async def run_server():
    async with MCPTools("wavespeed-mcp") as mcp_tools:
        agent = Agent(tools=[mcp_tools])
        playground = Playground(agents=[agent])
        playground.serve(playground.get_app())
```

## 最佳实践建议

1. **对于演示和开发**：使用Playground方式
2. **对于API服务**：创建长生命周期的MCP服务管理器
3. **对于一次性脚本**：在主函数中管理MCP连接

## 环境问题总结

之前遇到的环境问题已经解决：
- ✅ MCP包安装正确
- ✅ Agno MCP工具可用
- ✅ WaveSpeed MCP服务器可连接
- ❌ 连接生命周期管理不当

现在需要修正架构设计。 