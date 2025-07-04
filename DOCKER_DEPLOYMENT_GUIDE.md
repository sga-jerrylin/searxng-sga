# SearXNG Docker 部署指南

## 🚀 一键启动

### Windows 用户
```bash
# 双击运行
start_docker.bat

# 或者在命令行中运行
.\start_docker.bat
```

### Linux/macOS 用户
```bash
# 给脚本执行权限
chmod +x start_docker.sh

# 运行脚本
./start_docker.sh
```

## 📋 前置要求

1. **Docker 和 Docker Compose**
   - Docker Desktop (Windows/macOS)
   - Docker Engine + Docker Compose (Linux)

2. **网络端口**
   - 端口 8888 未被占用
   - 端口 6379 未被占用（Redis）

## 🔧 手动部署步骤

### 1. 创建网络
```bash
docker network create dify-network
```

### 2. 启动服务
```bash
# 构建并启动
docker-compose up --build -d

# 查看状态
docker-compose ps
```

### 3. 验证服务
```bash
# 测试基本连接
curl http://localhost:8888

# 测试搜索API
curl "http://localhost:8888/search?q=test&format=json"

# 测试微信搜索
curl "http://localhost:8888/wechat_search?q=微信"
```

## 🏗️ 架构说明

### 服务组件
- **SearXNG**: 主搜索服务（端口8888）
- **Redis**: 缓存服务（端口6379）

### 网络配置
- `searxng-net`: 内部服务通信
- `dify-network`: 与 Dify 平台通信

### 数据持久化
- `redis-data`: Redis 数据存储
- `searxng-logs`: SearXNG 日志存储

## 🔍 功能特性

### ✅ 已集成功能
- 🔍 **通用搜索API**: `/search`
- 📱 **微信专搜API**: `/wechat_search`
- 🎯 **Dify 兼容性**: 支持 JSON 格式
- 🛡️ **Windows 兼容性**: 修复了所有 Windows 相关问题
- 🚀 **自动启动**: 容器启动即可使用

### 🔧 配置特性
- 禁用了指定的搜索引擎（quark、seznam、wolframalpha等）
- 启用了微信公众号搜索
- 支持 JSON 格式输出
- 优化了超时设置

## 🌐 API 使用

### 通用搜索 API
```bash
GET http://localhost:8888/search
参数:
- q: 搜索关键词
- format: json
- categories: general,images,videos,news
- time_range: day,week,month,year
- lang: zh-CN
```

### 微信专搜 API
```bash
GET http://localhost:8888/wechat_search
参数:
- q: 搜索关键词
```

### 响应格式
```json
{
  "query": "搜索关键词",
  "number_of_results": 10,
  "results": [
    {
      "title": "标题",
      "url": "链接",
      "content": "内容摘要",
      "engine": "搜索引擎名称"
    }
  ],
  "answers": [],
  "corrections": [],
  "infoboxes": [],
  "suggestions": [],
  "unresponsive_engines": []
}
```

## 🔧 Dify 集成配置

### 通用搜索工具
```json
{
  "名称": "SearXNG通用搜索",
  "类型": "HTTP请求",
  "URL": "http://localhost:8888/search",
  "方法": "GET",
  "参数": {
    "q": "{{query}}",
    "format": "json",
    "categories": "general"
  },
  "超时": 30
}
```

### 微信专搜工具
```json
{
  "名称": "微信公众号搜索",
  "类型": "HTTP请求", 
  "URL": "http://localhost:8888/wechat_search",
  "方法": "GET",
  "参数": {
    "q": "{{query}}"
  },
  "超时": 30
}
```

## 📊 管理命令

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看 SearXNG 日志
docker-compose logs searxng

# 实时查看日志
docker-compose logs -f searxng
```

### 服务管理
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建
docker-compose up --build -d

# 查看状态
docker-compose ps
```

### 清理资源
```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi $(docker images -q "searxng-sga*")

# 清理未使用的资源
docker system prune -f
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   netstat -an | grep 8888
   
   # 修改端口（docker-compose.yml）
   ports:
     - "8889:8888"
   ```

2. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs searxng
   
   # 检查配置文件
   docker-compose config
   ```

3. **网络连接问题**
   ```bash
   # 检查网络
   docker network ls
   
   # 重新创建网络
   docker network rm dify-network
   docker network create dify-network
   ```

4. **权限问题**
   ```bash
   # Linux/macOS 下给脚本执行权限
   chmod +x start_docker.sh
   
   # 检查文件权限
   ls -la start_docker.sh
   ```

### 性能优化

1. **调整 Redis 配置**
   ```yaml
   # docker-compose.yml
   redis:
     command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
   ```

2. **调整 SearXNG 设置**
   ```yaml
   # searx/settings.yml
   outgoing:
     request_timeout: 3.0
     max_request_timeout: 10.0
   ```

## 🔒 安全建议

1. **网络安全**
   - 仅在需要时暴露端口
   - 使用防火墙限制访问
   - 定期更新镜像

2. **数据安全**
   - 定期备份配置文件
   - 监控日志文件大小
   - 使用安全的密钥

## 📈 监控和日志

### 日志位置
- SearXNG 日志: `searxng-logs` 卷
- Redis 日志: 容器内部日志

### 监控指标
- 容器状态: `docker-compose ps`
- 资源使用: `docker stats`
- 网络连接: `netstat -an | grep 8888`

## 🆕 版本更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up --build -d

# 验证更新
curl http://localhost:8888/search?q=test&format=json
```

---

## 🎉 部署完成！

现在您的 SearXNG 服务已经通过 Docker 自动启动，无需手动运行 Python 脚本！

- 🌐 **访问地址**: http://localhost:8888
- 🔍 **通用搜索**: http://localhost:8888/search
- 📱 **微信专搜**: http://localhost:8888/wechat_search
- �� **Dify 集成**: 开箱即用！ 