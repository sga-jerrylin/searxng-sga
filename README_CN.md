# SearXNG-SGA - 面向中国企业的私有化搜索引擎

## 🎯 项目概述

这是一个基于 SearXNG 深度优化的企业级搜索引擎，聚焦中文搜索、公众号专搜与平台集成，默认时间优先展示，结果更相关、更干净。

### ✨ 核心特性（v1.1.0）

- **📱 微信专搜API** - 专门的公众号搜索端点
- **⏱ 时间优先** - 网页端默认按时间排序（最新优先）
- **🔎 相关性重排** - 文本模板组内相关性重排（网页端）；API 轻量重排（可开启 `debug_score`）
- **🧹 结果清洁** - 列表级去重（URL 指纹 + 标题近似）、低相关过滤、标题/摘要清洗
- **🧰 稳定性** - 微信相关 UA 轮换、指数退避重试、可选代理（`WECHAT_PROXY`）
- **⚡ 缓存** - API 结果 60s 短期缓存（512 条）

## 🚀 快速开始

### 1. 启动服务（Docker）

#### 标准启动方式
```bash
# 设置环境变量并启动
python -m searx.webapp

# Windows PowerShell
$env:PYTHONPATH="$PWD"; python -m searx.webapp

# Linux/macOS
export PYTHONPATH="$PWD" && python -m searx.webapp
```

#### Docker环境（最稳定）
```bash
docker-compose up --build -d
```

### 2. 测试接口
```bash
# 测试中文搜索API（推荐）
curl "http://localhost:8888/chinese_search?q=人工智能&limit=10"

# 测试微信专搜API
curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=8"

# 测试通用搜索API
curl "http://localhost:8888/search?q=人工智能&format=json"
```

### 🪟 环境兼容性
支持 Windows / Linux / macOS 下 Docker 运行。

## 📡 API接口说明

### 🌟 中文搜索API（推荐）
```
GET/POST /chinese_search
```

**功能：** 使用优质中文搜索引擎进行搜索，自动按时间排序

**参数：**
- `q` (必需): 搜索关键词
- `limit` (可选): 返回结果数量 (1-100，默认10)
- `engines` (可选): 指定搜索引擎，用逗号分隔 (默认: sogou,baidu,360search,wechat)
- `sort_by_time` (可选): 是否按时间排序 (默认true，从最新到最旧)

**特点：**
- ✅ 锁定优质中文搜索引擎
- ✅ 支持返回条数控制
- ✅ 支持搜索引擎选择
- ✅ 完全兼容Dify平台
- ✅ 响应速度快
- ✅ 自动按时间排序（最新内容优先）

**时间排序功能：**
- 🕐 自动获取当前时间
- 📅 解析搜索结果中的发布时间
- 🔄 按发布时间降序排列（最新在前）
- 📊 支持多种时间格式：ISO 8601、标准格式等
- ⚙️ 可通过 `sort_by_time=false` 关闭排序

**示例：**
```bash
# 基本搜索（默认按时间排序）
curl "http://localhost:8888/chinese_search?q=人工智能"

# 指定搜索引擎和返回条数
curl "http://localhost:8888/chinese_search?q=人工智能&engines=sogou,baidu&limit=15"

# 只使用搜狗搜索
curl "http://localhost:8888/chinese_search?q=龙树谅&engines=sogou&limit=5"

# 关闭时间排序
curl "http://localhost:8888/chinese_search?q=人工智能&sort_by_time=false"

# 指定返回更多结果
curl "http://localhost:8888/chinese_search?q=人工智能&limit=20&sort_by_time=true"
```

### 📱 微信专搜API
```
GET/POST /wechat_search
```

**功能：** 专门搜索微信公众号内容，自动按时间排序

**参数：**
- `q` (必需): 搜索关键词
- `limit` (可选): 返回结果数量 (1-100，默认10)
- `sort_by_time` (可选): 是否按时间排序 (默认true，从最新到最旧)

**特点：**
- 专门搜索微信公众号文章
- 使用微信相关搜索引擎
- JSON格式输出
- 独立的API端点
- ✅ 自动按时间排序（最新内容优先）

**时间排序功能：**
- 🕐 自动获取当前时间
- 📅 解析微信公众号文章的发布时间
- 🔄 按发布时间降序排列（最新文章优先）
- 📊 支持多种时间格式解析
- ⚙️ 可通过 `sort_by_time=false` 关闭排序

**示例：**
```bash
# 微信公众号搜索（默认按时间排序）
curl "http://localhost:8888/wechat_search?q=ChatGPT"

# 限制返回结果
curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=8"

# 关闭时间排序
curl "http://localhost:8888/wechat_search?q=ChatGPT&sort_by_time=false"

# 获取更多微信文章
curl "http://localhost:8888/wechat_search?q=科技资讯&limit=15&sort_by_time=true"
```

### 🔄 通用搜索API（原有接口）
```
GET/POST /search?q=查询内容&format=json
```

**特点：**
- 支持HTML和JSON两种输出格式
- 使用所有配置的搜索引擎
- 保持向后兼容性
- ⚠️ Dify平台建议使用新API

## ⏰ 时间排序功能详解

### 🎯 功能概述
SearXNG-SGA 新增了强大的时间排序功能，让搜索结果自动按发布时间从最新到最旧排序，确保用户总是能获取到最新的信息。

### 🔧 技术实现
- **自动时间获取**：系统自动获取当前时间作为参考
- **智能时间解析**：支持多种时间格式的自动解析
- **降序排序**：按发布时间降序排列（最新内容优先）
- **容错处理**：没有时间信息的结果排在最后
- **性能优化**：轻量级实现，不影响响应速度

### 📊 支持的时间格式
- **ISO 8601格式**：`2024-01-15T10:30:00Z`
- **标准格式**：`2024-01-15 10:30:00`
- **自动解析**：系统会自动尝试多种时间格式

### ⚙️ 参数配置
- **`sort_by_time=true`**（默认）：启用时间排序
- **`sort_by_time=false`**：关闭时间排序，使用相关性排序
- **支持的值**：`true`, `1`, `yes` 或 `false`, `0`, `no`

### 📈 性能特点
- ✅ 轻量级排序算法，影响微乎其微
- ✅ 智能时间解析，避免无效操作
- ✅ 可通过参数关闭排序提升性能
- ✅ 详细的性能日志记录

### 🔍 使用场景
1. **新闻资讯搜索**：获取最新新闻和资讯
2. **技术文档搜索**：获取最新的技术文档和教程
3. **微信公众号搜索**：获取最新的公众号文章
4. **学术论文搜索**：获取最新的研究成果

### 📝 日志记录
系统会记录以下信息：
- 当前时间
- 排序开始和完成状态
- 有时间信息的结果数量
- 排序过程中的错误和警告

### 📊 API功能对比

| 特性 | `/chinese_search` | `/wechat_search` | `/search` |
|------|-------------------|------------------|-----------|
| **用途** | 中文搜索（推荐） | 微信专搜 | 通用搜索 |
| **搜索引擎** | 可指定中文引擎 | 微信相关引擎 | 所有配置的引擎 |
| **返回条数控制** | ✅ 1-100可调 | ✅ 1-100可调 | ❌ 固定 |
| **引擎选择** | ✅ 灵活配置 | ❌ 固定微信引擎 | ❌ 使用全部引擎 |
| **Dify兼容性** | ✅ 完全兼容 | ✅ 完全兼容 | ⚠️ 有兼容性问题 |
| **响应速度** | ✅ 快速 | ✅ 快速 | ❌ 较慢 |
| **输出格式** | JSON only | JSON only | HTML/JSON |
| **时间排序** | ✅ 自动排序 | ✅ 自动排序 | ❌ 无排序 |
| **排序参数** | ✅ `sort_by_time` | ✅ `sort_by_time` | ❌ 无参数 |
| **推荐场景** | 中文内容搜索 | 微信公众号内容 | 网页界面 |

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

### 运行建议
- 需要更强的新鲜度时，可调高过滤阈值或限定日期
- 若命中反爬，可配置 `WECHAT_PROXY` 并适度放宽 `limit`

## 💻 使用示例

### Python调用
```python
import requests

# 中文搜索（推荐）- 默认按时间排序
response = requests.get('http://localhost:8888/chinese_search', {
    'q': '人工智能',
    'limit': 10,
    'engines': 'sogou,baidu'
})
data = response.json()

# 中文搜索 - 关闭时间排序
response = requests.get('http://localhost:8888/chinese_search', {
    'q': '人工智能',
    'limit': 10,
    'engines': 'sogou,baidu',
    'sort_by_time': False
})
data = response.json()

# 微信专搜 - 默认按时间排序
wechat_response = requests.get('http://localhost:8888/wechat_search', {
    'q': 'ChatGPT',
    'limit': 8
})
wechat_data = wechat_response.json()

# 微信专搜 - 关闭时间排序
wechat_response = requests.get('http://localhost:8888/wechat_search', {
    'q': 'ChatGPT',
    'limit': 8,
    'sort_by_time': False
})
wechat_data = wechat_response.json()

# 通用搜索（兼容性）
general_response = requests.get('http://localhost:8888/search', {
    'q': '人工智能',
    'format': 'json'
})
general_data = general_response.json()
```

### JavaScript调用
```javascript
// 中文搜索（推荐）
const searchChinese = async (query, limit = 10, engines = 'sogou,baidu') => {
    const url = new URL('/chinese_search', window.location.origin);
    url.searchParams.set('q', query);
    url.searchParams.set('limit', limit);
    url.searchParams.set('engines', engines);
    const response = await fetch(url);
    return await response.json();
};

// 微信专搜
const searchWechat = async (query, limit = 10) => {
    const url = new URL('/wechat_search', window.location.origin);
    url.searchParams.set('q', query);
    url.searchParams.set('limit', limit);
    const response = await fetch(url);
    return await response.json();
};

// 通用搜索（兼容性）
const searchGeneral = async (query) => {
    const response = await fetch(`/search?q=${encodeURIComponent(query)}&format=json`);
    return await response.json();
};
```

## 🔗 Dify集成配置

### ⚠️ 重要提醒
**Dify 平台内置的 SearXNG 插件与本项目 API 不兼容！**

请使用 Dify 工作流中的 **HTTP 请求节点** 调用我们的专用 API。

### 🚨 关键配置要求
**在 Dify Docker 环境中，必须使用 `host.docker.internal` 地址！**

- ❌ 错误：`http://localhost:8888/chinese_search`
- ✅ 正确：`http://host.docker.internal:8888/chinese_search`

这是因为 Dify 运行在 Docker 容器内，无法直接访问宿主机的 localhost。

### 🎯 推荐集成方案

#### 1. 中文搜索工具（推荐）
- **API 端点**: `/chinese_search`
- **特点**: 锁定优质中文搜索引擎，自动时间排序
- **支持引擎**: sogou, baidu, 360search, wechat
- **参数控制**: 返回条数、搜索引擎选择、时间排序

#### 2. 微信专搜工具
- **API 端点**: `/wechat_search`
- **特点**: 专门搜索微信公众号内容，自动时间排序
- **支持引擎**: 微信搜索、搜狗微信搜索

### 🔧 Dify 工作流配置

#### 中文搜索工具配置
```json
{
  "name": "chinese_search",
  "description": "中文搜索工具，使用优质中文搜索引擎，自动按时间排序",
  "method": "GET",
  "url": "http://host.docker.internal:8888/chinese_search",
  "parameters": {
    "q": "{{query}}",
    "limit": "{{limit|default:10}}",
    "engines": "{{engines|default:sogou,baidu,360search,wechat}}",
    "sort_by_time": "{{sort_by_time|default:true}}"
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### 微信搜索工具配置
```json
{
  "name": "wechat_search",
  "description": "微信公众号搜索工具，自动按时间排序",
  "method": "GET",
  "url": "http://host.docker.internal:8888/wechat_search",
  "parameters": {
    "q": "{{query}}",
    "limit": "{{limit|default:10}}",
    "sort_by_time": "{{sort_by_time|default:true}}"
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

### 🚀 使用示例

#### 本地测试（直接访问）
```bash
# 中文搜索（推荐）
curl "http://localhost:8888/chinese_search?q=人工智能&limit=10&engines=sogou,baidu"

# 微信专搜
curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=8"

# 指定单个搜索引擎
curl "http://localhost:8888/chinese_search?q=龙树谅&engines=sogou&limit=5"
```

#### Dify平台调用（Docker环境）
```bash
# 中文搜索（推荐）
curl "http://host.docker.internal:8888/chinese_search?q=人工智能&limit=10&engines=sogou,baidu"

# 微信专搜
curl "http://host.docker.internal:8888/wechat_search?q=ChatGPT&limit=8"
```

### 📋 参数说明

#### 中文搜索 API 参数
- `q` (必需): 搜索关键词
- `limit` (可选): 返回结果数量 (1-100，默认10)
- `engines` (可选): 指定搜索引擎，用逗号分隔 (默认: sogou,baidu,360search,wechat)

#### 微信搜索 API 参数
- `q` (必需): 搜索关键词
- `limit` (可选): 返回结果数量 (1-100，默认10)

### 🎨 Dify 工作流设计建议

1. **创建 HTTP 请求节点**
   - 节点类型：HTTP 请求
   - 请求方法：GET
   - URL：使用上述 API 端点

2. **设置输入变量**
   - 搜索关键词：`query` (文本类型)
   - 返回条数：`limit` (数字类型，默认10)
   - 搜索引擎：`engines` (文本类型，仅中文搜索)

3. **配置输出处理**
   - 解析 JSON 响应
   - 提取 `results` 数组
   - 格式化搜索结果

4. **错误处理**
   - 设置超时时间 (建议30秒)
   - 添加重试机制
   - 处理网络异常

### ✅ 优势对比

| 特性 | Dify 内置插件 | SearXNG-SGA API |
|------|---------------|-----------------|
| 中文搜索引擎 | ❌ 不支持锁定 | ✅ 锁定优质引擎 |
| 返回条数控制 | ❌ 固定数量 | ✅ 1-100 可调节 |
| 微信专搜 | ❌ 不支持 | ✅ 独立API端点 |
| 搜索引擎选择 | ❌ 无法指定 | ✅ 灵活配置 |
| 响应格式 | ❌ 格式限制 | ✅ 优化JSON格式 |
| 兼容性 | ❌ 调用失败 | ✅ 完全兼容 |

### 🧪 测试验证
```bash
# 测试中文搜索API
curl "http://localhost:8888/chinese_search?q=人工智能&limit=5"

# 测试微信搜索API
curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=5"

# 检查服务状态
curl "http://localhost:8888/healthz"
```

### 🔧 故障排除

如果遇到Dify调用错误，请参考：
- [API使用指南](API_USAGE_GUIDE.md) - 完整API使用说明
- [Dify工作流指南](DIFY_WORKFLOW_GUIDE.md) - 详细集成步骤
- 使用curl命令测试API是否正常工作

## 📁 文件结构

项目根目录已经过清理整理，删除了重复和无用的文件。

详细的文件结构说明请参考：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

### 核心文件概览

```
searxng-sga/
├── 📖 主要文档
│   ├── README_CN.md                   # 中文主文档（本文件）
│   ├── API_USAGE_GUIDE.md            # API使用指南
│   ├── DIFY_WORKFLOW_GUIDE.md        # Dify工作流集成指南
│   └── PROJECT_STRUCTURE.md          # 完整文件结构说明
│
├── 🐳 Docker启动脚本
│   ├── start_docker.bat              # Docker启动脚本（Windows）
│   └── start_docker.sh               # Docker启动脚本（Linux/macOS）
│
├── 🐳 Docker配置
│   ├── docker-compose.yml            # Docker编排文件
│   └── Dockerfile                    # Docker镜像构建文件
│
└── 📦 核心代码
    └── searx/
        ├── settings.yml              # 主配置文件（已优化）
        ├── webapp.py                 # Web应用（新增中文搜索和微信API）
        └── engines/                  # 搜索引擎
            ├── wechat.py             # 微信搜索引擎
            └── sogou_wechat.py       # 搜狗微信搜索
```

### 🗑️ 已删除的重复文件

为保持项目结构清晰，已删除以下重复和无用的文件：
- 重复的README文件（README_FINAL.md、README-WeChat.md）
- 重复的API文档（API_USAGE.md）
- 重复的Git脚本（多个推送脚本）
- 重复的集成指南（旧版Dify指南）
- 重复的启动脚本（复杂版本）

详细的清理记录请参考：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#已删除的重复文件)

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
如需企业级定制与支持，请在 Issue 中联系。

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

### 本版本要点（v1.1.0）
- Web：时间优先排序、组内相关性重排（文本）、列表级去重、低相关过滤、标题/摘要清洗
- API：轻量相关性重排（`debug_score` 可透出）、60s 缓存、去重清洗
- 稳定性：微信 UA 轮换、退避重试、可选代理
- 精简：移除无关脚本文档，Docker/compose 精简

## 📄 许可证

本项目基于 **GNU Affero General Public License v3.0** 开源。

### 许可证要点
- ✅ 商业使用、修改、分发
- 📋 需要包含许可证和版权声明
- 📋 网络部署需要公开源代码

---

🎉 **现在你拥有了一个完全适配Dify且支持微信专搜的开源隐私搜索引擎！** 