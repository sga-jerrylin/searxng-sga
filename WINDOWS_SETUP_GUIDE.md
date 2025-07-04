# SearXNG Windows 平台安装配置指南

## 问题解决

您遇到的 `HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded` 错误已经完全解决！

## 解决方案总结

### 1. Windows 兼容性修复

我们修复了以下 Windows 兼容性问题：

#### A. uvloop 模块问题
- **问题**: `uvloop` 不支持 Windows 平台
- **解决**: 修改 `searx/network/client.py`，添加条件导入
- **修复代码**:
```python
# Windows兼容性修复 - uvloop不支持Windows
try:
    import uvloop
    uvloop.install()
except ImportError:
    # Windows上没有uvloop，使用默认的asyncio事件循环
    pass
```

#### B. pwd 模块问题
- **问题**: `pwd` 模块是 Unix/Linux 特有的
- **解决**: 修改 `searx/redisdb.py`，添加条件导入
- **修复代码**:
```python
# Windows兼容性修复
try:
    import pwd
    HAS_PWD = True
except ImportError:
    HAS_PWD = False
```

#### C. multiprocessing fork 问题
- **问题**: Windows 不支持 `fork` 上下文
- **解决**: 修改 `searx/plugins/calculator.py`，使用 `spawn` 上下文
- **修复代码**:
```python
# Windows兼容性修复 - fork上下文在Windows上不可用
try:
    mp_fork = multiprocessing.get_context("fork")
except ValueError:
    # Windows上使用spawn上下文
    mp_fork = multiprocessing.get_context("spawn")
```

### 2. 依赖包安装

创建了 Windows 兼容的依赖文件 `requirements-windows.txt`，移除了 `uvloop` 依赖。

### 3. 启动脚本

创建了简化的启动脚本 `start_searxng_simple.py`，可以在 Windows 上直接运行。

## 快速启动指南

### 步骤 1: 安装依赖
```powershell
pip install flask werkzeug requests pyyaml lxml babel flask-babel pygments httpx brotli python-dateutil msgspec typer-slim isodate markdown-it-py
```

### 步骤 2: 启动服务
```powershell
python start_searxng_simple.py
```

### 步骤 3: 验证服务
```powershell
python test_connection.py
```

## Dify 集成配置

### 服务状态
- ✅ SearXNG 服务运行在 `http://localhost:8888`
- ✅ 支持 JSON 格式输出
- ✅ 通用搜索 API: `/search`
- ✅ 微信专搜 API: `/wechat_search`
- ✅ Dify 兼容性测试全部通过

### Dify 工具配置

#### 通用搜索工具
```json
{
  "名称": "SearXNG通用搜索",
  "URL": "http://localhost:8888/search",
  "方法": "GET",
  "参数": {
    "q": "{{query}}",
    "format": "json",
    "categories": "general"
  }
}
```

#### 微信专搜工具
```json
{
  "名称": "微信公众号搜索",
  "URL": "http://localhost:8888/wechat_search",
  "方法": "GET",
  "参数": {
    "q": "{{query}}"
  }
}
```

### 高级配置参数

可选参数：
- `time_range`: `day`, `week`, `month`, `year`
- `categories`: `general`, `images`, `videos`, `news`, `map`, `music`, `it`, `science`
- `engines`: 指定特定搜索引擎
- `lang`: 语言代码 (如 `zh-CN`)

## 故障排除

### 常见问题

1. **端口被占用**
   ```powershell
   netstat -an | findstr 8888
   ```

2. **防火墙阻止**
   - 确保 Windows 防火墙允许 Python 访问网络
   - 检查杀毒软件是否阻止连接

3. **模块导入错误**
   - 确保所有依赖都已正确安装
   - 检查 Python 版本兼容性

### 测试命令

```powershell
# 测试基本连接
curl http://localhost:8888

# 测试搜索API
curl "http://localhost:8888/search?q=test&format=json"

# 测试微信搜索
curl "http://localhost:8888/wechat_search?q=微信"
```

## 性能优化建议

1. **生产环境部署**
   - 使用 `gunicorn` 或 `uwsgi` 替代 Flask 开发服务器
   - 配置反向代理 (nginx)
   - 启用 Redis 缓存

2. **搜索引擎优化**
   - 根据需要启用/禁用特定搜索引擎
   - 调整超时设置
   - 配置代理（如需要）

## 文件清单

创建/修改的文件：
- ✅ `requirements-windows.txt` - Windows 兼容依赖
- ✅ `start_searxng_simple.py` - 简化启动脚本
- ✅ `test_connection.py` - 连接测试脚本
- ✅ `DIFY_INTEGRATION_GUIDE.md` - Dify 集成指南
- ✅ `API_USAGE.md` - API 使用文档
- ✅ `searx/settings.yml` - 配置文件（JSON支持，搜索引擎配置）
- ✅ `searx/webapp.py` - 添加微信专搜API
- ✅ `searx/network/client.py` - Windows兼容性修复
- ✅ `searx/redisdb.py` - Windows兼容性修复
- ✅ `searx/plugins/calculator.py` - Windows兼容性修复

## 成功确认

✅ **所有测试通过**
- 基本连接测试
- 搜索API测试
- 微信搜索API测试
- Dify兼容性测试

✅ **服务正常运行**
- 端口8888正在监听
- 返回正确的JSON格式
- 搜索功能正常工作

您现在可以在 Dify 中配置 SearXNG 工具了！ 