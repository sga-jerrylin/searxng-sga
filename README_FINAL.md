# SearXNG Dify 集成项目 - 最终版本

## 🎉 项目完成状态

✅ **所有需求已实现并测试通过！**

### 主要成果
1. ✅ **禁用指定搜索引擎** - 已禁用 quark、seznam、wolframalpha 等
2. ✅ **Dify 平台集成** - 支持 JSON 格式，完全兼容
3. ✅ **微信专搜 API** - 专门的微信公众号搜索接口
4. ✅ **Windows 兼容性** - 修复所有 Windows 相关问题
5. ✅ **Docker 自动化** - 容器启动即可使用，无需手动运行脚本

## 🚀 快速开始

### 方式一：Docker 部署（推荐）
```bash
# Windows 用户
.\start_docker.bat

# Linux/macOS 用户
chmod +x start_docker.sh && ./start_docker.sh
```

### 方式二：直接运行（开发模式）
```bash
# Windows 用户
python start_searxng_simple.py

# 测试连接
python test_connection.py
```

## 🌐 服务地址

启动后可通过以下地址访问：

- **SearXNG 主页**: http://localhost:8888
- **通用搜索 API**: http://localhost:8888/search
- **微信专搜 API**: http://localhost:8888/wechat_search

## 🔧 Dify 集成配置

### 通用搜索工具
```json
{
  "名称": "SearXNG通用搜索",
  "URL": "http://localhost:8888/search",
  "参数": "q={{query}}&format=json&categories=general"
}
```

### 微信专搜工具
```json
{
  "名称": "微信公众号搜索",
  "URL": "http://localhost:8888/wechat_search",
  "参数": "q={{query}}"
}
```

## 📁 项目文件结构

### 核心文件
- `searx/settings.yml` - 主配置文件
- `searx/webapp.py` - Web 应用（包含微信专搜 API）
- `docker-compose.yml` - Docker 编排文件
- `Dockerfile` - Docker 镜像构建文件

### 启动脚本
- `start_docker.bat` - Windows Docker 启动脚本
- `start_docker.sh` - Linux/macOS Docker 启动脚本
- `start_searxng_simple.py` - 简化的 Python 启动脚本

### 测试工具
- `test_connection.py` - 连接测试脚本
- `requirements-windows.txt` - Windows 兼容的依赖文件

### 文档
- `DOCKER_DEPLOYMENT_GUIDE.md` - Docker 部署指南
- `WINDOWS_SETUP_GUIDE.md` - Windows 安装指南
- `DIFY_INTEGRATION_GUIDE.md` - Dify 集成指南
- `API_USAGE.md` - API 使用文档

## 🔍 功能特性

### 搜索引擎配置
- ✅ 禁用了以下搜索引擎：
  - quark
  - seznam
  - wolframalpha
  - crowdview
  - mojeek
  - mwmbl
  - naver
  - bing (images, news, videos)
  - bpb

- ✅ 启用了微信公众号搜索：
  - sogou wechat

### API 功能
- ✅ **通用搜索 API** (`/search`)
  - 支持多种搜索引擎
  - JSON 格式输出
  - 支持分类搜索
  - 支持时间范围筛选

- ✅ **微信专搜 API** (`/wechat_search`)
  - 专门搜索微信公众号内容
  - 强制 JSON 格式输出
  - 优化的搜索结果

### 兼容性修复
- ✅ **Windows 兼容性**
  - 修复 `uvloop` 不支持 Windows 的问题
  - 修复 `pwd` 模块在 Windows 上不可用的问题
  - 修复 `multiprocessing.fork` 在 Windows 上不支持的问题

- ✅ **Dify 平台兼容性**
  - 支持 JSON 格式响应
  - 支持 GET 和 POST 请求
  - 优化的超时设置
  - 标准化的 API 响应格式

## 🐛 已解决的问题

### 连接问题
- ✅ 解决了 `HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded` 错误
- ✅ 修复了端口绑定问题（从 127.0.0.1 改为 0.0.0.0）
- ✅ 优化了超时设置

### 模块导入问题
- ✅ 解决了 `No module named 'uvloop'` 错误
- ✅ 解决了 `No module named 'pwd'` 错误
- ✅ 解决了 `cannot find context for 'fork'` 错误

### 依赖问题
- ✅ 创建了 Windows 兼容的 requirements 文件
- ✅ 自动安装所有必需的依赖包

## 📊 测试结果

所有测试都已通过：
- ✅ 基本连接测试
- ✅ 搜索 API 测试
- ✅ 微信搜索 API 测试
- ✅ Dify 兼容性测试
- ✅ Windows 兼容性测试
- ✅ Docker 部署测试

## 🎯 使用建议

### 生产环境
- 推荐使用 Docker 部署
- 配置反向代理（nginx）
- 启用 Redis 缓存
- 定期备份配置文件

### 开发环境
- 可以直接使用 Python 脚本启动
- 使用测试脚本验证功能
- 查看日志排查问题

## 🔮 后续扩展

项目已经为以下扩展做好了准备：
- 添加更多搜索引擎
- 自定义搜索结果处理
- 增加缓存策略
- 添加监控和告警
- 支持更多输出格式

## 🙏 项目总结

这个项目成功实现了：
1. **SearXNG 与 Dify 的完美集成**
2. **Windows 平台的全面兼容**
3. **微信公众号的专门搜索**
4. **Docker 的自动化部署**
5. **完整的文档和测试**

现在您可以：
- 🚀 一键启动 Docker 服务
- 🔍 在 Dify 中使用搜索功能
- 📱 专门搜索微信公众号内容
- 🛠️ 根据需要自定义配置

**项目已经完全就绪，可以投入使用！** 🎉 