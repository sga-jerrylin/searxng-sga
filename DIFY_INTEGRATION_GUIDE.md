# Dify + SearXNG 集成故障排除指南

## 问题诊断

您遇到的错误表明Dify无法连接到SearXNG服务：
```
HTTPConnectionPool(host='host.docker.internal', port=8888): Max retries exceeded
[Errno 101] Network is unreachable
```

## 解决方案

### 1. 检查SearXNG服务状态

首先确认SearXNG是否正在运行：

```bash
# 检查8888端口是否被占用
netstat -tlnp | grep :8888
# 或者使用
ss -tlnp | grep :8888

# 如果使用Docker
docker ps | grep searxng
```

### 2. 启动SearXNG服务

#### 方案A：使用Docker Compose (推荐)

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8888:8080"
    volumes:
      - ./searx:/etc/searxng:rw
    environment:
      - SEARXNG_BASE_URL=http://localhost:8888/
    restart: unless-stopped
    networks:
      - searxng-net

  redis:
    image: redis:alpine
    container_name: searxng-redis
    command: redis-server --save 30 1 --loglevel warning
    volumes:
      - redis-data:/data
    networks:
      - searxng-net
    restart: unless-stopped

volumes:
  redis-data:

networks:
  searxng-net:
    driver: bridge
```

启动服务：
```bash
docker-compose up -d
```

#### 方案B：直接运行Python服务

```bash
# 进入项目目录
cd searxng-sga

# 安装依赖
pip install -r requirements.txt

# 启动服务
python searx/webapp.py
```

### 3. 网络连接配置

#### Docker网络问题解决

1. **检查host.docker.internal可用性**：
```bash
# 在Docker容器内测试
docker run --rm -it alpine ping host.docker.internal
```

2. **替代连接方式**：

如果`host.docker.internal`不可用，使用以下替代方案：

**Linux系统**：
- 使用宿主机IP：`172.17.0.1:8888`
- 或者：`$(ip route show default | awk '/default/ {print $3}'):8888`

**Windows系统**：
- 使用：`localhost:8888` 或 `127.0.0.1:8888`

**macOS系统**：
- 使用：`host.docker.internal:8888`

### 4. SearXNG配置调整

确保SearXNG配置支持外部访问，编辑 `searx/settings.yml`：

```yaml
# 服务器配置
server:
  port: 8080
  bind_address: "0.0.0.0"  # 允许外部访问
  base_url: "http://localhost:8888/"
  
# 搜索配置
search:
  safe_search: 0
  autocomplete: ""
  default_lang: "zh-CN"
  formats:
    - html
    - json    # 确保支持JSON格式
    
# 禁用某些安全限制（仅用于开发测试）
general:
  debug: false
  instance_name: "SearXNG for Dify"
```

### 5. 防火墙配置

确保8888端口可访问：

```bash
# Ubuntu/Debian
sudo ufw allow 8888

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload

# Windows
# 在Windows防火墙中添加入站规则允许8888端口
```

### 6. Dify配置测试

#### 在Dify中配置SearXNG工具：

1. **基础URL配置**：
   - 本地部署：`http://localhost:8888`
   - Docker部署：`http://host.docker.internal:8888`
   - 如果上述不可用：`http://172.17.0.1:8888`

2. **API端点**：
   - 通用搜索：`/search`
   - 微信专搜：`/wechat_search`

3. **测试参数**：
```json
{
  "q": "测试查询",
  "format": "json",
  "categories": "general"
}
```

#### 连接测试脚本：

```bash
# 测试SearXNG是否可访问
curl -X GET "http://localhost:8888/search?q=test&format=json"

# 测试微信专搜API
curl -X GET "http://localhost:8888/wechat_search?q=微信测试"
```

### 7. Docker网络详细配置

如果使用Docker部署Dify和SearXNG，创建共享网络：

```yaml
# 在docker-compose.yml中添加网络配置
version: '3.8'

services:
  searxng:
    # ... 其他配置
    networks:
      - dify-network

networks:
  dify-network:
    external: true  # 使用外部网络
```

创建共享网络：
```bash
docker network create dify-network
```

### 8. 常见问题解决

#### 问题1：端口冲突
```bash
# 查找占用8888端口的进程
lsof -i :8888
# 终止进程
kill -9 <PID>
```

#### 问题2：权限问题
```bash
# 给予配置文件正确权限
chmod 755 searx/settings.yml
```

#### 问题3：DNS解析问题
在`/etc/hosts`中添加：
```
127.0.0.1 host.docker.internal
```

### 9. 验证安装

运行以下测试确保一切正常：

```python
import requests

# 测试基本连接
response = requests.get('http://localhost:8888/search?q=SearXNG&format=json')
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")

# 测试微信搜索
response = requests.get('http://localhost:8888/wechat_search?q=微信公众号')
print(f"微信搜索状态码: {response.status_code}")
print(f"微信搜索响应: {response.json()}")
```

### 10. 性能优化建议

在`searx/settings.yml`中添加：

```yaml
# 网络优化
outgoing:
  request_timeout: 10.0
  max_request_timeout: 30.0
  pool_connections: 100
  pool_maxsize: 20

# 缓存配置
redis:
  url: "redis://localhost:6379/0"

# API响应优化
search:
  max_page: 3
  formats:
    - json
```

## 快速解决步骤

1. 确保SearXNG服务在8888端口运行
2. 测试网络连接：`curl http://localhost:8888/search?q=test&format=json`
3. 在Dify中使用正确的连接地址
4. 检查防火墙设置
5. 验证Docker网络配置

如果问题持续存在，请提供具体的部署环境信息以获得更精确的帮助。 