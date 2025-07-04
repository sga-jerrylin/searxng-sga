# Dify 连接 SearXNG 配置指南

## 🔗 连接地址配置

根据您的部署环境，Dify 连接 SearXNG 需要使用不同的地址：

### 1. 本地 Docker 部署

#### Windows Docker Desktop
```json
{
  "通用搜索": "http://host.docker.internal:8888/search",
  "微信专搜": "http://host.docker.internal:8888/wechat_search"
}
```

#### Linux Docker
```json
{
  "通用搜索": "http://172.17.0.1:8888/search",
  "微信专搜": "http://172.17.0.1:8888/wechat_search"
}
```

#### macOS Docker Desktop
```json
{
  "通用搜索": "http://host.docker.internal:8888/search",
  "微信专搜": "http://host.docker.internal:8888/wechat_search"
}
```

### 2. 同一 Docker 网络部署

如果 Dify 和 SearXNG 在同一个 Docker 网络中：
```json
{
  "通用搜索": "http://searxng-dify:8888/search",
  "微信专搜": "http://searxng-dify:8888/wechat_search"
}
```

### 3. 云服务器部署

使用服务器的公网 IP 或域名：
```json
{
  "通用搜索": "http://YOUR_SERVER_IP:8888/search",
  "微信专搜": "http://YOUR_SERVER_IP:8888/wechat_search"
}
```

## 🔧 Dify 工具配置

### 通用搜索工具配置

**工具名称**: SearXNG通用搜索

**配置参数**:
```json
{
  "method": "GET",
  "url": "http://host.docker.internal:8888/search",
  "params": {
    "q": "{{query}}",
    "format": "json",
    "categories": "general"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "timeout": 30
}
```

### 微信专搜工具配置

**工具名称**: 微信公众号搜索

**配置参数**:
```json
{
  "method": "GET", 
  "url": "http://host.docker.internal:8888/wechat_search",
  "params": {
    "q": "{{query}}"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "timeout": 30
}
```

## 🐛 故障排除

### 1. 连接被拒绝 (Connection Refused)

**问题**: `Connection refused` 或 `Max retries exceeded`

**解决方案**:
1. 检查 SearXNG 是否正在运行:
   ```bash
   docker-compose ps
   ```

2. 检查端口是否监听:
   ```bash
   netstat -an | findstr 8888
   ```

3. 尝试不同的连接地址:
   - Windows: `host.docker.internal:8888`
   - Linux: `172.17.0.1:8888`
   - 本地: `localhost:8888`

### 2. 网络不可达 (Network Unreachable)

**问题**: `Network is unreachable`

**解决方案**:
1. 确保 Docker 网络正确配置:
   ```bash
   docker network ls
   docker network inspect dify-network
   ```

2. 重新创建网络:
   ```bash
   docker network rm dify-network
   docker network create dify-network
   ```

### 3. 超时错误 (Timeout)

**问题**: `Request timeout`

**解决方案**:
1. 增加 Dify 中的超时设置 (30-60秒)
2. 检查防火墙设置
3. 检查 SearXNG 服务状态

### 4. DNS 解析问题

**问题**: `Name resolution failed`

**解决方案**:
1. 使用 IP 地址而不是域名
2. 检查 Docker DNS 配置
3. 在 docker-compose.yml 中添加 extra_hosts

## 🔍 连接测试

### 手动测试连接

#### Windows PowerShell
```powershell
# 测试基本连接
Invoke-WebRequest -Uri "http://localhost:8888" -Method GET

# 测试搜索API
Invoke-WebRequest -Uri "http://localhost:8888/search?q=test&format=json" -Method GET
```

#### Linux/macOS
```bash
# 测试基本连接
curl http://localhost:8888

# 测试搜索API
curl "http://localhost:8888/search?q=test&format=json"
```

### 使用测试脚本
```bash
python test_connection.py
```

## 📋 完整的 Dify 配置示例

### HTTP 请求工具配置

**步骤 1**: 在 Dify 中添加 HTTP 请求工具

**步骤 2**: 配置通用搜索

```json
{
  "name": "SearXNG搜索",
  "description": "使用SearXNG进行网络搜索",
  "method": "GET",
  "url": "http://host.docker.internal:8888/search",
  "authorization": {
    "type": "no-auth"
  },
  "params": [
    {
      "name": "q",
      "type": "string",
      "required": true,
      "description": "搜索关键词"
    },
    {
      "name": "format",
      "type": "string",
      "required": true,
      "default": "json"
    },
    {
      "name": "categories",
      "type": "string", 
      "required": false,
      "default": "general"
    }
  ]
}
```

**步骤 3**: 配置微信专搜

```json
{
  "name": "微信公众号搜索",
  "description": "搜索微信公众号内容",
  "method": "GET",
  "url": "http://host.docker.internal:8888/wechat_search",
  "authorization": {
    "type": "no-auth"
  },
  "params": [
    {
      "name": "q",
      "type": "string",
      "required": true,
      "description": "搜索关键词"
    }
  ]
}
```

## 🌐 不同环境的连接地址总结

| 环境 | 连接地址 | 说明 |
|------|----------|------|
| Windows Docker Desktop | `host.docker.internal:8888` | 推荐 |
| Windows 本地 | `localhost:8888` | 直接运行时 |
| Linux Docker | `172.17.0.1:8888` | Docker 网桥IP |
| macOS Docker Desktop | `host.docker.internal:8888` | 推荐 |
| 同一网络容器 | `searxng-dify:8888` | 容器名 |
| 云服务器 | `YOUR_IP:8888` | 公网IP |

## ✅ 验证配置

配置完成后，在 Dify 中测试工具：

1. **测试搜索**: 输入 "测试搜索" 看是否返回结果
2. **测试微信搜索**: 输入 "微信公众号" 看是否返回微信内容
3. **检查响应格式**: 确保返回 JSON 格式数据

如果仍有问题，请检查：
- SearXNG 容器是否运行
- 端口是否正确映射
- 网络配置是否正确
- 防火墙是否阻止连接 