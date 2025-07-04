# SearXNG API 使用指南

## 🎯 功能概述

本项目已经适配Dify并新增了微信专搜功能，提供以下两个主要API接口：

## 1️⃣ Dify集成 - 通用搜索API

### 接口地址
```
GET/POST /search
```

### 支持的输出格式
- `html` - 网页格式（默认）
- `json` - JSON格式（Dify集成必需）

### 基本用法

#### JSON格式搜索（Dify调用）
```bash
# GET请求
curl "http://localhost:8888/search?q=人工智能&format=json"

# POST请求
curl -X POST "http://localhost:8888/search" \
  -d "q=人工智能&format=json"
```

#### 响应格式
```json
{
  "query": "人工智能",
  "number_of_results": 42,
  "results": [
    {
      "title": "文章标题",
      "url": "https://example.com",
      "content": "文章摘要内容",
      "engine": "搜索引擎名称",
      "score": 1.0
    }
  ],
  "suggestions": ["相关建议"],
  "answers": [],
  "infoboxes": []
}
```

### Dify配置

1. **安装SearXNG插件**
   - 在Dify marketplace中搜索并安装SearXNG插件

2. **配置Base URL**
   ```
   http://localhost:8888
   ```

3. **测试连接**
   ```bash
   curl "http://localhost:8888/search?q=test&format=json"
   ```

## 2️⃣ 微信专搜API

### 接口地址
```
GET/POST /wechat_search
```

### 特点
- 🎯 **专门搜索**：只使用微信相关搜索引擎
- 📱 **微信内容**：搜索微信公众号文章
- 📄 **JSON输出**：强制返回JSON格式

### 基本用法

```bash
# GET请求
curl "http://localhost:8888/wechat_search?q=ChatGPT"

# POST请求  
curl -X POST "http://localhost:8888/wechat_search" \
  -d "q=ChatGPT"
```

### 响应格式
```json
{
  "query": "ChatGPT",
  "number_of_results": 15,
  "results": [
    {
      "title": "微信文章标题",
      "url": "https://mp.weixin.qq.com/s/...",
      "content": "微信文章摘要",
      "engine": "wechat",
      "score": 1.0
    }
  ],
  "suggestions": [],
  "answers": [],
  "infoboxes": []
}
```

### 错误处理
```json
{
  "error": "No query provided",
  "message": "请提供搜索关键词"
}
```

## 🛠️ 技术实现

### 已启用的微信搜索引擎
1. **wechat** - 主要微信搜索引擎
2. **sogou wechat** - 搜狗微信搜索（备用）

### 配置修改点
1. **JSON格式支持**：`searx/settings.yml` 中添加 `json` 格式
2. **微信引擎启用**：启用 `sogou wechat` 引擎
3. **专用API**：新增 `/wechat_search` 路由

## 🔧 部署建议

### 生产环境配置
```yaml
# searx/settings.yml
search:
  formats:
    - html
    - json

server:
  limiter: true  # 生产环境建议启用限流
  secret_key: "your-secret-key"  # 使用随机生成的密钥
```

### 性能优化
```yaml
outgoing:
  request_timeout: 5.0
  pool_connections: 200
  pool_maxsize: 50
```

## 📝 使用示例

### Python调用示例
```python
import requests

# 通用搜索
response = requests.get('http://localhost:8888/search', {
    'q': '人工智能',
    'format': 'json'
})
data = response.json()

# 微信专搜
wechat_response = requests.get('http://localhost:8888/wechat_search', {
    'q': 'ChatGPT'
})
wechat_data = wechat_response.json()
```

### JavaScript调用示例
```javascript
// 通用搜索
const searchGeneral = async (query) => {
    const response = await fetch(`http://localhost:8888/search?q=${encodeURIComponent(query)}&format=json`);
    return await response.json();
};

// 微信专搜
const searchWechat = async (query) => {
    const response = await fetch(`http://localhost:8888/wechat_search?q=${encodeURIComponent(query)}`);
    return await response.json();
};
```

## 🚀 快速测试

```bash
# 测试通用搜索JSON接口
curl "http://localhost:8888/search?q=测试&format=json" | jq .

# 测试微信专搜接口
curl "http://localhost:8888/wechat_search?q=人工智能" | jq .

# 检查服务健康状态
curl "http://localhost:8888/healthz"
```

## 📞 故障排除

### Dify连接问题 ⚠️

**错误：`HTTPConnectionPool: Max retries exceeded`**

这是最常见的Dify连接问题，解决步骤：

1. **确认SearXNG服务状态**
```bash
# 检查端口是否被占用
netstat -tlnp | grep :8888

# 启动SearXNG（如果未运行）
python start_searxng.py

# 测试基本连接
curl http://localhost:8888
```

2. **网络连接配置修复**
- **Linux环境**：将Dify中的URL改为 `http://172.17.0.1:8888`
- **Windows环境**：使用 `http://localhost:8888` 或 `http://127.0.0.1:8888`
- **macOS环境**：保持 `http://host.docker.internal:8888`

3. **运行连接测试**
```bash
# 使用专用测试脚本
python test_connection.py

# 手动测试Dify格式
curl "http://localhost:8888/search?q=SearXNG&time_range=day&format=json&categories=general"
```

4. **Docker网络解决方案**
```bash
# 创建共享网络
docker network create dify-network

# 确保SearXNG配置正确的bind_address
# 在 searx/settings.yml 中确认：
# server:
#   bind_address: "0.0.0.0"
```

### 常见问题

1. **403 Forbidden**
   - 检查 `formats` 配置是否包含 `json`
   - 确认限流器设置

2. **微信搜索无结果**
   - 检查微信引擎是否启用
   - 查看引擎日志

3. **连接超时**
   - 调整 `request_timeout` 设置
   - 检查网络连接

4. **端口冲突**
```bash
# 查找占用端口的进程
lsof -i :8888
# 终止冲突进程
kill -9 <PID>
```

5. **防火墙问题**
```bash
# Ubuntu/Debian
sudo ufw allow 8888

# Windows: 在防火墙设置中允许8888端口
```

### 快速诊断工具

```bash
# 一键测试所有功能
python test_connection.py --host localhost --port 8888

# 仅测试连接（跳过搜索）
python test_connection.py --skip-search
```

### 调试模式
```bash
# 启用调试日志
export SEARXNG_DEBUG=1
python start_searxng.py

# 查看详细错误信息
python -m searx.webapp
```

### Dify工具配置示例

在Dify中配置SearXNG工具时，使用以下设置：

```
工具名称: SearXNG搜索
Base URL: http://localhost:8888
API路径: /search
方法: GET
参数:
  q: {query}
  format: json
  categories: general
超时: 30秒
```

---

🎉 **现在你的SearXNG已经完全适配Dify并支持微信专搜功能！** 