# SearXNG-SGA 开源项目指南

## 🎯 项目简介

SearXNG-SGA (SearXNG Super General Assistant) 是一个增强版的隐私搜索引擎，专门为AI应用开发和中文搜索场景优化。

### 🌟 项目特色

1. **🤖 AI平台集成**
   - 原生支持Dify AI开发平台
   - 标准化JSON API接口
   - 完整的API文档和示例

2. **📱 专业搜索API**
   - 微信公众号专搜API
   - 多引擎聚合搜索
   - 智能结果去重和排序

3. **🪟 跨平台兼容**
   - 完整的Windows兼容性支持
   - Docker一键部署
   - 多种启动方式

4. **🔒 隐私保护**
   - 基于SearXNG的隐私保护特性
   - 不记录用户搜索历史
   - 支持代理和匿名访问

## 🚀 快速开始

### 方式1: 直接运行（Windows推荐）
```bash
git clone https://github.com/your-repo/searxng-sga.git
cd searxng-sga
pip install -r requirements.txt
python start_searxng_simple.py
```

### 方式2: Docker部署
```bash
git clone https://github.com/your-repo/searxng-sga.git
cd searxng-sga
docker-compose up --build -d
```

### 方式3: 开发环境
```bash
git clone https://github.com/your-repo/searxng-sga.git
cd searxng-sga
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python start_searxng.py
```

## 📚 文档结构

| 文档 | 说明 |
|------|------|
| [API_USAGE.md](API_USAGE.md) | 详细的API使用说明 |
| [WINDOWS_COMPATIBILITY_GUIDE.md](WINDOWS_COMPATIBILITY_GUIDE.md) | Windows兼容性指南 |
| [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md) | Docker部署指南 |
| [DIFY_INTEGRATION_GUIDE.md](DIFY_INTEGRATION_GUIDE.md) | Dify集成配置 |
| [README_CN.md](README_CN.md) | 中文使用说明 |

## 🛠️ 技术架构

```
SearXNG-SGA 架构
├── 前端界面层
│   ├── Web UI (Simple主题)
│   └── API接口 (JSON/HTML)
├── 业务逻辑层
│   ├── 搜索聚合器
│   ├── 结果处理器
│   └── 缓存管理
├── 搜索引擎层
│   ├── 通用搜索引擎 (Google, DuckDuckGo等)
│   ├── 微信专搜引擎 (Sogou微信)
│   └── 自定义引擎适配器
└── 基础设施层
    ├── 网络客户端 (HTTPX)
    ├── 数据存储 (Redis可选)
    └── 配置管理 (YAML)
```

## 🔧 核心功能

### 1. 通用搜索API
- **端点**: `/search`
- **格式**: JSON/HTML
- **特性**: 多引擎聚合、智能排序、去重

### 2. 微信专搜API
- **端点**: `/wechat_search`
- **格式**: JSON
- **特性**: 微信公众号专搜、内容过滤

### 3. Dify集成
- **兼容性**: 完全兼容Dify平台
- **配置**: 简单的Base URL配置
- **测试**: 内置连接测试工具

## 🤝 贡献指南

### 贡献方式

1. **Bug报告**
   - 使用GitHub Issues
   - 提供详细的错误信息
   - 包含复现步骤

2. **功能建议**
   - 提交Feature Request
   - 说明使用场景
   - 提供实现思路

3. **代码贡献**
   - Fork项目
   - 创建功能分支
   - 提交Pull Request

### 开发规范

#### 代码风格
```python
# 使用Black格式化
black searx/

# 使用isort排序导入
isort searx/

# 使用flake8检查
flake8 searx/
```

#### 测试要求
```bash
# 运行单元测试
python -m pytest tests/

# 运行集成测试
python test_connection.py

# 检查API兼容性
curl "http://localhost:8888/search?q=test&format=json"
```

#### 文档更新
- 新功能必须更新API文档
- 配置变更需要更新配置说明
- 重大变更需要更新README

### 提交规范

使用Conventional Commits格式：
```
feat: 添加微信专搜API
fix: 修复Windows兼容性问题
docs: 更新API文档
style: 代码格式化
refactor: 重构搜索引擎
test: 添加单元测试
chore: 更新依赖包
```

## 🔍 搜索引擎配置

### 已启用的引擎
- **通用搜索**: DuckDuckGo, Google, Startpage, Brave
- **微信搜索**: Sogou微信, 微信公众号
- **知识库**: Wikipedia, Wikidata
- **开发者**: GitHub, Stack Overflow

### 已禁用的引擎
- **性能原因**: Bing系列, Yandex
- **地区限制**: Baidu, Naver
- **稳定性**: 部分小众引擎

### 自定义引擎
```python
# 添加新搜索引擎
# searx/engines/your_engine.py
def request(query, params):
    # 实现搜索请求
    pass

def response(resp):
    # 处理搜索结果
    pass
```

## 📊 性能优化

### 1. 缓存策略
```yaml
# 启用Redis缓存
redis:
  url: redis://localhost:6379/0
  
# 配置缓存TTL
cache:
  ttl: 3600  # 1小时
```

### 2. 并发优化
```yaml
# 调整并发设置
request_timeout: 10.0
max_request_timeout: 20.0
pool_connections: 100
pool_maxsize: 20
```

### 3. 网络优化
```yaml
# 配置代理
proxies:
  http: http://proxy:port
  https: https://proxy:port
```

## 🔐 安全配置

### 1. 访问控制
```yaml
# 限制访问IP
server:
  bind_address: "127.0.0.1"  # 仅本地访问
  # bind_address: "0.0.0.0"  # 允许外部访问
```

### 2. 速率限制
```yaml
# 配置限流
limiter:
  enabled: true
  rate: "10/minute"
```

### 3. 安全头
```yaml
# 启用安全头
security:
  enable_csp: true
  enable_hsts: true
```

## 🌍 国际化支持

### 语言支持
- 中文（简体/繁体）
- 英语
- 日语、韩语
- 德语、法语、西班牙语
- 更多语言持续添加中...

### 添加新语言
```bash
# 提取翻译字符串
python -m babel extract -F babel.cfg -k lazy_gettext -o messages.pot searx/

# 创建新语言
python -m babel init -i messages.pot -d searx/translations -l zh_CN

# 更新翻译
python -m babel update -i messages.pot -d searx/translations

# 编译翻译
python -m babel compile -d searx/translations
```

## 📈 监控和日志

### 1. 日志配置
```yaml
# 配置日志级别
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 2. 性能监控
```python
# 使用内置监控
from searx.metrics import get_metrics
metrics = get_metrics()
```

### 3. 健康检查
```bash
# 检查服务状态
curl http://localhost:8888/healthz

# 检查搜索引擎状态
curl http://localhost:8888/stats
```

## 🚀 部署建议

### 生产环境
1. **使用Docker部署**
2. **配置反向代理** (Nginx/Apache)
3. **启用HTTPS**
4. **配置监控和日志**
5. **设置自动备份**

### 开发环境
1. **使用虚拟环境**
2. **启用调试模式**
3. **配置热重载**
4. **使用开发数据库**

## 📄 许可证

本项目基于 **GNU Affero General Public License v3.0** 开源。

### 许可证要点
- ✅ 商业使用
- ✅ 修改
- ✅ 分发
- ✅ 专利使用
- ❌ 责任
- ❌ 保证

### 义务
- 📋 包含许可证
- 📋 包含版权声明
- 📋 声明更改
- 📋 公开源代码（如果网络部署）

## 🙏 致谢

感谢以下项目和贡献者：

- [SearXNG](https://github.com/searxng/searxng) - 原始项目
- [Dify](https://github.com/langgenius/dify) - AI平台集成
- 所有贡献者和用户

## 📞 联系我们

- **GitHub Issues**: 报告问题和建议
- **Discussions**: 技术讨论和交流
- **Wiki**: 详细文档和教程

---

🎉 **欢迎加入SearXNG-SGA开源社区！** 

让我们一起构建更好的隐私搜索引擎！ 