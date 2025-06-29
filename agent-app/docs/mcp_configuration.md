# MCP配置指南

## 概述

WaveSpeed MCP需要API密钥才能正常工作。本文档说明了在不同环境下如何配置MCP。

## 配置方式

### 1. 环境变量配置（推荐）

这是**当前项目使用的主要方式**：

```bash
# 设置API密钥
export WAVESPEED_API_KEY="your_wavespeed_api_key_here"

# 可选：设置API主机
export WAVESPEED_API_HOST="https://api.wavespeed.ai"

# 可选：设置资源模式
export WAVESPEED_API_RESOURCE_MODE="url"
```

#### 在项目中使用

1. **复制环境变量模板**：
   ```bash
   cp example.env .env
   ```

2. **编辑 `.env` 文件**，取消注释并设置真实值：
   ```env
   WAVESPEED_API_KEY=your_actual_api_key_here
   WAVESPEED_API_HOST=https://api.wavespeed.ai
   WAVESPEED_API_RESOURCE_MODE=url
   ```

3. **加载环境变量**：
   ```bash
   source .env
   ```

### 2. YAML配置文件

用于Docker容器或Kubernetes部署：

```yaml
# workspace/secrets/dev_app_secrets.yml
WAVESPEED_API_KEY: "your_wavespeed_api_key_here"
WAVESPEED_API_HOST: "https://api.wavespeed.ai"
WAVESPEED_API_RESOURCE_MODE: "url"
```

### 3. MCP服务器配置文件

如果使用Claude Desktop或其他MCP客户端，可以使用 `mcp_config.json`：

```json
{
  "mcpServers": {
    "Wavespeed": {
      "command": "wavespeed-mcp",
      "env": {
        "WAVESPEED_API_KEY": "your_wavespeed_api_key_here"
      }
    }
  }
}
```

## 配置位置

### 开发环境

1. **环境变量**：
   - 文件：`agent-app/.env`
   - 设置：`WAVESPEED_API_KEY=your_key`

2. **应用密钥**：
   - 文件：`workspace/secrets/dev_app_secrets.yml`
   - 格式：YAML

3. **MCP客户端**：
   - 文件：`agent-app/mcp_config.json`
   - 格式：JSON

### 生产环境

1. **容器环境变量**：
   ```bash
   docker run -e WAVESPEED_API_KEY=your_key ...
   ```

2. **Kubernetes Secret**：
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: wavespeed-secret
   data:
     WAVESPEED_API_KEY: <base64-encoded-key>
   ```

## 验证配置

### 检查环境变量

```bash
echo $WAVESPEED_API_KEY
```

### 测试MCP连接

```bash
cd agent-app
PYTHONPATH=. python examples/simple_mcp_test.py
```

### 运行完整测试

```bash
cd agent-app
export WAVESPEED_API_KEY=your_key
python examples/image_generation_example.py
```

## 故障排除

### 常见问题

1. **API密钥未设置**：
   ```
   ❌ 错误：请设置 WAVESPEED_API_KEY 环境变量
   ```
   
   **解决方案**：
   ```bash
   export WAVESPEED_API_KEY=your_actual_key
   ```

2. **MCP服务器连接失败**：
   ```
   ❌ MCP连接失败: Failed to connect to MCP server
   ```
   
   **解决方案**：
   ```bash
   # 确保wavespeed-mcp已安装
   pip install wavespeed-mcp
   
   # 检查命令是否可用
   wavespeed-mcp --help
   ```

3. **API认证失败**：
   ```
   ❌ API status error: 403 - Access denied
   ```
   
   **解决方案**：
   - 检查API密钥是否有效
   - 确认API密钥格式正确
   - 联系WaveSpeed获取有效密钥

### 调试模式

启用调试模式获取更多信息：

```python
agent = get_image_generator(debug_mode=True)
```

## 安全注意事项

1. **不要在代码中硬编码API密钥**
2. **将 `.env` 文件添加到 `.gitignore`**
3. **定期轮换API密钥**
4. **在生产环境使用密钥管理服务**

## 配置示例

### 完整的 `.env` 文件

```env
# Agno配置
AGNO_API_KEY=your_agno_key
AGNO_MONITOR=True

# OpenAI配置
OPENAI_API_KEY=sk-your_openai_key

# WaveSpeed MCP配置
WAVESPEED_API_KEY=your_wavespeed_key
WAVESPEED_API_HOST=https://api.wavespeed.ai
WAVESPEED_API_RESOURCE_MODE=url

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=ai
DB_PASS=ai
DB_DATABASE=ai
```

### Claude Desktop配置

如果在Claude Desktop中使用，将此配置添加到Claude配置文件：

```json
{
  "mcpServers": {
    "Wavespeed": {
      "command": "wavespeed-mcp",
      "env": {
        "WAVESPEED_API_KEY": "your_wavespeed_api_key_here"
      }
    }
  }
}
```

配置文件位置：
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json` 