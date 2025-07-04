# Windows 兼容性指南

## 概述
SearXNG 原本主要针对Linux环境设计，在Windows环境下运行时会遇到一些兼容性问题。本指南详细说明了这些问题及其解决方案。

## 主要兼容性问题

### 1. pwd 模块问题
**问题**: Windows系统不支持 `pwd` 模块（Unix专用）
**错误信息**: `ModuleNotFoundError: No module named 'pwd'`
**解决方案**: 已修复 `searx/redisdb.py`，使用条件导入处理Windows兼容性

### 2. uvloop 模块问题
**问题**: Windows系统不支持 `uvloop` 模块（Unix专用事件循环）
**错误信息**: `No module named 'uvloop'`
**解决方案**: 已修复 `searx/network/client.py`，Windows环境下自动跳过uvloop

### 3. multiprocessing fork 问题
**问题**: Windows不支持 `fork` 多进程上下文
**错误信息**: `ValueError: cannot find context for 'fork'`
**解决方案**: 已修复 `searx/plugins/calculator.py`，Windows环境下使用 `spawn` 上下文

## 修复后的文件

### searx/redisdb.py
```python
# Windows兼容性修复
try:
    import pwd
    PWD_AVAILABLE = True
except ImportError:
    PWD_AVAILABLE = False
    pwd = None

# 在使用pwd的地方添加条件检查
if PWD_AVAILABLE and pwd:
    # 使用pwd的代码
else:
    # Windows兼容的替代方案
```

### searx/network/client.py
```python
# Windows兼容性修复
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False
    uvloop = None

# 条件使用uvloop
if UVLOOP_AVAILABLE and uvloop:
    # 使用uvloop的代码
else:
    # 使用标准asyncio
```

### searx/plugins/calculator.py
```python
# Windows兼容性修复
import platform
if platform.system() == "Windows":
    mp_fork = multiprocessing.get_context("spawn")
else:
    mp_fork = multiprocessing.get_context("fork")
```

## 启动方式

### 方式1: 使用简化启动脚本（推荐）
```bash
python start_searxng_simple.py
```

### 方式2: 使用Docker（最稳定）
```bash
# 构建并启动
docker-compose up --build -d

# 查看日志
docker-compose logs -f
```

### 方式3: 直接启动Flask
```bash
# 设置环境变量
$env:PYTHONPATH="$PWD"
$env:FLASK_APP="searx.webapp"

# 启动服务
flask run --host=0.0.0.0 --port=8888
```

## 网络连接问题

### 常见错误
- `ConnectTimeout`: 网络连接超时
- `HTTPConnectionPool`: 连接池问题

### 解决方案
1. **检查网络连接**
   ```bash
   # 测试基本连接
   python test_connection.py
   ```

2. **调整超时设置**
   在 `searx/settings.yml` 中：
   ```yaml
   request_timeout: 10.0
   max_request_timeout: 20.0
   ```

3. **使用代理**（如果需要）
   ```yaml
   proxies:
     http: http://proxy:port
     https: https://proxy:port
   ```

## Dify 集成配置

### Windows Docker Desktop
```yaml
# Dify配置中使用
base_url: "http://host.docker.internal:8888"
```

### 本地开发
```yaml
# Dify配置中使用
base_url: "http://localhost:8888"
```

## 性能优化

### 1. 禁用不必要的搜索引擎
```yaml
# 在 searx/settings.yml 中
engines:
  - name: google
    disabled: true  # 如果网络访问受限
```

### 2. 调整并发设置
```yaml
# 降低并发数以提高稳定性
max_workers: 2
```

### 3. 增加缓存
```yaml
# 启用缓存以减少网络请求
cache:
  enabled: true
  ttl: 3600
```

## 故障排除

### 1. 模块导入错误
```bash
# 安装缺失依赖
pip install -r requirements.txt
```

### 2. 权限问题
```bash
# 以管理员身份运行PowerShell
```

### 3. 端口占用
```bash
# 检查端口占用
netstat -ano | findstr :8888

# 杀死占用进程
taskkill /PID <PID> /F
```

### 4. 防火墙问题
- 确保Windows防火墙允许Python访问网络
- 添加防火墙例外规则

## 开发建议

### 1. 环境隔离
```bash
# 使用虚拟环境
python -m venv venv
venv\Scripts\activate
```

### 2. 依赖管理
```bash
# 生成requirements文件
pip freeze > requirements-windows.txt
```

### 3. 测试
```bash
# 运行兼容性测试
python test_connection.py
```

## 已知限制

1. **性能**: Windows下性能可能低于Linux
2. **并发**: 多进程支持有限
3. **网络**: 某些网络库在Windows下表现不同
4. **文件系统**: 路径分隔符差异

## 贡献指南

如果您发现新的Windows兼容性问题：

1. 创建Issue描述问题
2. 提供错误日志
3. 说明Windows版本和Python版本
4. 提供复现步骤

## 相关文档

- [Docker部署指南](DOCKER_DEPLOYMENT_GUIDE.md)
- [Dify集成指南](DIFY_INTEGRATION_GUIDE.md)
- [API使用说明](API_USAGE.md)
- [连接测试工具](test_connection.py)

## 版本兼容性

- **Python**: 3.8+
- **Windows**: 10/11
- **PowerShell**: 5.1+
- **Docker Desktop**: 4.0+

---

**注意**: 此项目已针对Windows环境进行了优化，但仍建议在Linux环境下部署生产环境以获得最佳性能。 