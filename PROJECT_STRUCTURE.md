# 项目文件结构说明

## 📁 根目录结构（已清理）

```
searxng-sga/
├── 📖 文档文件
│   ├── README.rst                      # 英文主文档
│   ├── README_CN.md                   # 中文主文档
│   ├── API_USAGE_GUIDE.md            # API使用指南
│   ├── DIFY_WORKFLOW_GUIDE.md        # Dify工作流集成指南
│   ├── WINDOWS_COMPATIBILITY_GUIDE.md # Windows兼容性指南
│   ├── DOCKER_DEPLOYMENT_GUIDE.md    # Docker部署指南
│   ├── GIT_DEPLOYMENT_GUIDE.md       # Git部署指南
│   └── OPEN_SOURCE_GUIDE.md          # 开源项目指南
│
├── 🐳 Docker配置
│   ├── docker-compose.yml            # Docker编排文件
│   ├── Dockerfile                    # Docker镜像构建文件
│   ├── start_docker.bat              # Docker启动脚本（Windows）
│   ├── start_docker.sh               # Docker启动脚本（Linux/macOS）
│   └── docker-settings.yml           # Docker专用设置
│
├── 🔧 Git工具
│   ├── git_setup.bat                 # Git初始化脚本
│   └── git_push.bat                  # Git推送脚本
│
├── ⚙️ 配置文件
│   ├── requirements.txt              # Python依赖（Linux/macOS）
│   ├── requirements-windows.txt      # Python依赖（Windows）
│   └── limiter.toml                  # 限流器配置
│
├── 📦 核心代码
│   ├── searx/                        # SearXNG核心代码
│   │   ├── settings.yml              # 主配置文件
│   │   ├── webapp.py                 # Web应用（含新API）
│   │   ├── engines/                  # 搜索引擎
│   │   ├── plugins/                  # 插件
│   │   └── ...                       # 其他核心文件
│   │
│   ├── searxng_extra/                # 扩展功能
│   ├── tests/                        # 单元测试
│   ├── docs/                         # 官方文档
│   ├── utils/                        # 工具脚本
│   └── client/                       # 前端资源
│
└── 🔒 项目配置
    ├── .gitignore                    # Git忽略文件
    ├── .dockerignore                 # Docker忽略文件
    ├── LICENSE                       # 开源许可证
    ├── CHANGELOG.rst                 # 更新日志
    ├── AUTHORS.rst                   # 作者信息
    └── ...                           # 其他配置文件
```

## 📋 文件用途说明

### 📖 文档文件

| 文件 | 用途 | 目标用户 |
|------|------|----------|
| `README.rst` | 英文主文档，项目概述 | 国际用户 |
| `README_CN.md` | 中文主文档，详细说明 | 中文用户 |
| `API_USAGE_GUIDE.md` | 完整API使用指南 | 开发者 |
| `DIFY_WORKFLOW_GUIDE.md` | Dify平台集成指南 | AI开发者 |
| `WINDOWS_COMPATIBILITY_GUIDE.md` | Windows平台适配说明 | Windows用户 |
| `DOCKER_DEPLOYMENT_GUIDE.md` | Docker部署完整指南 | 运维人员 |
| `GIT_DEPLOYMENT_GUIDE.md` | Git部署和版本控制 | 开发者 |
| `OPEN_SOURCE_GUIDE.md` | 开源项目贡献指南 | 贡献者 |

### 🐳 Docker启动脚本

| 文件 | 用途 | 平台 |
|------|------|------|
| `start_docker.bat` | Docker启动脚本 | Windows |
| `start_docker.sh` | Docker启动脚本 | Linux/macOS |

### 🔧 Git工具

| 文件 | 用途 | 使用场景 |
|------|------|----------|
| `git_setup.bat` | 初始化Git仓库 | 首次部署 |
| `git_push.bat` | 推送代码到GitHub | 日常更新 |

## 🗑️ 已删除的重复文件

为了保持项目结构清晰，已删除以下重复和无用的文件：

### 删除的文档文件
- ~~`README_FINAL.md`~~ - 与README_CN.md重复
- ~~`README-WeChat.md`~~ - 内容已整合到主README
- ~~`API_USAGE.md`~~ - 使用新的API_USAGE_GUIDE.md
- ~~`DIFY_CONNECTION_GUIDE.md`~~ - 与DIFY_WORKFLOW_GUIDE.md重复
- ~~`DIFY_INTEGRATION_GUIDE.md`~~ - 使用新的工作流指南
- ~~`WINDOWS_SETUP_GUIDE.md`~~ - 与WINDOWS_COMPATIBILITY_GUIDE.md重复
- ~~`PUSH_TO_GITHUB.md`~~ - 与GIT_DEPLOYMENT_GUIDE.md重复

### 删除的脚本文件
- ~~`推送说明.txt`~~ - 中文说明文件
- ~~`覆盖master分支.bat`~~ - 危险操作脚本
- ~~`update_repo.ps1`~~ - 与其他脚本重复
- ~~`update_repo.bat`~~ - 与其他脚本重复
- ~~`quick_push.bat`~~ - 功能与git_push.bat重复
- ~~`start_searxng.py`~~ - 复杂版本，保留简化版

## 📝 使用建议

### 🔰 新用户快速开始
1. 阅读 `README_CN.md` 了解项目概述
2. 使用标准方式启动服务：`python -m searx.webapp`
3. 参考 `API_USAGE_GUIDE.md` 学习API使用

### 🤖 Dify平台集成
1. 阅读 `DIFY_WORKFLOW_GUIDE.md` 了解集成方案
2. 直接使用新的API端点进行集成
3. 参考工作流指南配置HTTP请求节点

### 🐳 Docker部署
1. 阅读 `DOCKER_DEPLOYMENT_GUIDE.md` 了解部署方法
2. 使用 `start_docker.bat` 或 `start_docker.sh` 启动
3. 编辑 `docker-settings.yml` 自定义配置

### 🖥️ Windows平台
1. 阅读 `WINDOWS_COMPATIBILITY_GUIDE.md` 了解兼容性
2. 使用 `requirements-windows.txt` 安装依赖
3. 使用标准方式启动：`python -m searx.webapp`

### 🔧 开发和贡献
1. 阅读 `OPEN_SOURCE_GUIDE.md` 了解贡献方式
2. 使用 `git_setup.bat` 初始化Git仓库
3. 使用 `git_push.bat` 推送代码更新

## 🎯 项目特色

- ✅ **文档完整** - 覆盖所有使用场景
- ✅ **结构清晰** - 文件分类明确，易于查找
- ✅ **平台兼容** - 支持Windows、Linux、macOS
- ✅ **部署简单** - 提供多种启动方式
- ✅ **测试完善** - 包含各种测试脚本
- ✅ **持续更新** - 定期清理和优化

现在项目结构更加清晰，文档更加完善，使用更加方便！ 