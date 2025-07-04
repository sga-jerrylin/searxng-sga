# SearXNG - 增强版隐私搜索引擎

## 🎯 项目概述

这是一个增强版的SearXNG隐私搜索引擎，专门针对AI应用开发和中文搜索场景进行了优化。

### ✨ 新增功能

- **🤖 Dify集成支持** - 原生JSON API，完美适配Dify AI开发平台
- **📱 微信专搜API** - 专门的微信公众号搜索接口
- **🔧 优化配置** - 针对中文用户优化的搜索引擎配置

## 🚀 快速开始

### 1. 启动服务

#### Windows环境（推荐）
```bash
# 使用简化启动脚本（已解决兼容性问题）
python start_searxng_simple.py
```

#### Linux/macOS环境
```bash
python -m searx.webapp
```

#### Docker环境（最稳定）
```bash
docker-compose up --build -d
```

### 2. 测试接口
```bash
# 测试Dify集成接口
curl "http://localhost:8888/search?q=人工智能&format=json"

# 测试微信专搜接口  
curl "http://localhost:8888/wechat_search?q=ChatGPT"
```

### 🪟 Windows兼容性
本项目已针对Windows环境进行全面优化，解决了以下兼容性问题：
- ✅ **pwd模块兼容性** - Unix专用模块在Windows下的替代方案
- ✅ **uvloop模块兼容性** - 异步事件循环在Windows下的优化
- ✅ **multiprocessing fork兼容性** - 多进程上下文在Windows下的适配

详细信息请参考 [Windows兼容性指南](WINDOWS_COMPATIBILITY_GUIDE.md)

## 📡 API接口说明

### 通用搜索API（Dify兼容）
```
GET/POST /search?q=查询内容&format=json
```

**特点：**
- 支持HTML和JSON两种输出格式
- 兼容Dify平台调用
- 聚合多个搜索引擎结果

### 微信专搜API
```
GET/POST /wechat_search?q=查询内容
```

**特点：**
- 专门搜索微信公众号文章
- 强制JSON格式输出
- 使用微信专用搜索引擎

## 🔧 配置说明

### JSON格式支持
```yaml
# searx/settings.yml
search:
  formats:
    - html
    - json
```

### 微信搜索引擎
```yaml
# 已启用的微信搜索引擎
- name: wechat           # 主要微信搜索
- name: sogou wechat     # 搜狗微信搜索（备用）
```

### 已禁用的搜索引擎
为了提升性能，以下搜索引擎已被禁用：
- quark、seznam、wolframalpha
- crowdview、mojeek、mwmbl
- naver、bing系列、bpb

## 💻 使用示例

### Python调用
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

### JavaScript调用
```javascript
// 通用搜索
const searchGeneral = async (query) => {
    const response = await fetch(`/search?q=${encodeURIComponent(query)}&format=json`);
    return await response.json();
};

// 微信专搜
const searchWechat = async (query) => {
    const response = await fetch(`/wechat_search?q=${encodeURIComponent(query)}`);
    return await response.json();
};
```

## 🔗 Dify集成配置

1. **在Dify中安装SearXNG插件**
2. **配置Base URL**：`http://localhost:8888`
3. **测试连接**：`curl "http://localhost:8888/search?q=test&format=json"`

## 📁 文件结构

```
├── searx/
│   ├── settings.yml          # 主配置文件（已优化）
│   ├── webapp.py            # Web应用（新增微信API）
│   └── engines/
│       ├── wechat.py        # 微信搜索引擎
│       └── sogou_wechat.py  # 搜狗微信搜索
├── API_USAGE.md             # 详细API文档
├── WINDOWS_COMPATIBILITY_GUIDE.md  # Windows兼容性指南
├── DOCKER_DEPLOYMENT_GUIDE.md      # Docker部署指南
├── DIFY_INTEGRATION_GUIDE.md       # Dify集成指南
├── GIT_DEPLOYMENT_GUIDE.md         # Git部署指南
├── start_searxng_simple.py         # Windows简化启动脚本
├── test_connection.py              # 连接测试工具
├── docker-compose.yml             # Docker编排文件
├── git_setup.bat                   # Git初始化脚本
├── git_push.bat                    # Git推送脚本
├── README.rst                     # 英文README
└── README_CN.md                  # 中文README（本文件）
```

## 🛠️ 故障排除

### 常见问题

1. **403 Forbidden**
   - 检查`formats`配置是否包含`json`
   - 确认限流器设置

2. **微信搜索无结果**
   - 检查微信引擎是否启用
   - 查看引擎日志

3. **连接超时**
   - 调整`request_timeout`设置
   - 检查网络连接

### 调试模式
```bash
export SEARXNG_DEBUG=1
python -m searx.webapp
```

## 📞 技术支持

详细的API文档和使用说明请参考：`API_USAGE.md`

## 🌟 开源项目

本项目现已开源！欢迎参与贡献：

- **开源指南**: [OPEN_SOURCE_GUIDE.md](OPEN_SOURCE_GUIDE.md)
- **Git部署指南**: [GIT_DEPLOYMENT_GUIDE.md](GIT_DEPLOYMENT_GUIDE.md)
- **贡献指南**: 查看开源指南中的贡献章节
- **Issue反馈**: 通过GitHub Issues报告问题
- **功能建议**: 提交Feature Request

### 🚀 快速推送到GitHub
```bash
# 方式1: 使用自动化脚本
git_push.bat

# 方式2: 手动推送
git_setup.bat
```

### 主要特性
- ✅ **完整的Windows兼容性支持**
- ✅ **Dify AI平台原生集成**
- ✅ **微信公众号专搜API**
- ✅ **Docker一键部署**
- ✅ **详细的文档和示例**

## 📄 许可证

本项目基于 **GNU Affero General Public License v3.0** 开源。

### 许可证要点
- ✅ 商业使用、修改、分发
- 📋 需要包含许可证和版权声明
- 📋 网络部署需要公开源代码

---

🎉 **现在你拥有了一个完全适配Dify且支持微信专搜的开源隐私搜索引擎！** 