# Git 部署指南

## 🎯 概述

本指南将帮助您将SearXNG-SGA项目推送到GitHub仓库，使其成为一个开源项目。

## 🚀 快速部署

### 方式1: 新建GitHub仓库（推荐）

1. **在GitHub上创建新仓库**
   - 访问 [GitHub](https://github.com)
   - 点击右上角的 "+" 按钮
   - 选择 "New repository"
   - 仓库名称建议：`searxng-sga`
   - 描述：`SearXNG Super General Assistant - 增强版隐私搜索引擎`
   - 选择 "Public"（公开仓库）
   - 不要初始化README、.gitignore或LICENSE（我们已经有了）

2. **运行Git设置脚本**
   ```bash
   # 在项目根目录运行
   git_setup.bat
   ```

3. **连接远程仓库并推送**
   ```bash
   # 替换为您的仓库URL
   git remote add origin https://github.com/YOUR_USERNAME/searxng-sga.git
   git branch -M main
   git push -u origin main
   ```

### 方式2: 使用自动化脚本

1. **运行推送脚本**
   ```bash
   git_push.bat
   ```

2. **输入仓库URL**
   - 脚本会提示您输入GitHub仓库URL
   - 例如：`https://github.com/username/searxng-sga.git`

3. **等待推送完成**
   - 脚本会自动处理所有Git操作
   - 推送完成后会显示成功信息

## 📋 手动部署步骤

如果您prefer手动操作，可以按照以下步骤：

### 1. 初始化Git仓库
```bash
git init
```

### 2. 添加文件到暂存区
```bash
git add .
```

### 3. 创建初始提交
```bash
git commit -m "feat: 初始化SearXNG-SGA项目

- 添加Dify集成支持
- 添加微信专搜API
- 完整的Windows兼容性支持
- Docker部署支持
- 详细的文档和使用指南"
```

### 4. 连接远程仓库
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 5. 推送到GitHub
```bash
git branch -M main
git push -u origin main
```

## 🔧 Git配置建议

### 设置用户信息
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 设置默认分支
```bash
git config --global init.defaultBranch main
```

### 设置推送策略
```bash
git config --global push.default simple
```

## 📁 项目结构说明

推送到GitHub后，您的仓库将包含以下重要文件：

```
searxng-sga/
├── 📚 文档文件
│   ├── README_CN.md                    # 中文说明文档
│   ├── OPEN_SOURCE_GUIDE.md           # 开源项目指南
│   ├── WINDOWS_COMPATIBILITY_GUIDE.md # Windows兼容性指南
│   ├── DOCKER_DEPLOYMENT_GUIDE.md     # Docker部署指南
│   ├── DIFY_INTEGRATION_GUIDE.md      # Dify集成指南
│   └── API_USAGE.md                   # API使用说明
├── 🚀 启动脚本
│   ├── start_searxng_simple.py        # Windows简化启动脚本
│   ├── start_searxng.py               # 完整启动脚本
│   └── test_connection.py             # 连接测试工具
├── 🐳 Docker文件
│   ├── docker-compose.yml             # Docker编排文件
│   ├── Dockerfile                     # Docker镜像文件
│   ├── start_docker.bat               # Windows Docker启动
│   └── start_docker.sh                # Linux Docker启动
├── 🔧 配置文件
│   ├── requirements.txt               # Python依赖
│   ├── requirements-windows.txt       # Windows专用依赖
│   └── searx/settings.yml             # 主配置文件
└── 📦 核心代码
    ├── searx/                         # 主要代码目录
    ├── tests/                         # 测试文件
    └── utils/                         # 工具脚本
```

## 🌟 GitHub仓库设置建议

### 1. 仓库描述
```
SearXNG Super General Assistant - 增强版隐私搜索引擎，支持Dify集成和微信专搜
```

### 2. 主题标签
添加以下标签：
- `searxng`
- `search-engine`
- `privacy`
- `dify`
- `wechat`
- `docker`
- `windows`
- `python`
- `flask`
- `api`

### 3. 启用功能
- ✅ Issues（问题反馈）
- ✅ Wiki（文档）
- ✅ Discussions（讨论）
- ✅ Projects（项目管理）
- ✅ Actions（CI/CD）

### 4. 保护分支
为main分支设置保护规则：
- 要求pull request审核
- 要求状态检查通过
- 限制推送权限

## 📊 项目推广

### 1. 创建Release
```bash
# 创建标签
git tag -a v1.0.0 -m "首个正式版本"
git push origin v1.0.0
```

### 2. 编写Release说明
包含以下内容：
- 主要功能介绍
- 安装和使用说明
- 更新日志
- 已知问题

### 3. 社区推广
- 在相关论坛分享
- 提交到awesome列表
- 写技术博客介绍

## 🤝 贡献指南

### 1. 设置Issue模板
创建以下模板：
- Bug报告
- 功能请求
- 问题询问

### 2. 设置PR模板
包含以下检查项：
- 代码风格检查
- 测试通过
- 文档更新
- 变更日志

### 3. 设置自动化
- GitHub Actions CI/CD
- 代码质量检查
- 自动化测试
- 文档生成

## 🔒 安全配置

### 1. 敏感信息保护
- 不要提交密码、密钥
- 使用环境变量
- 设置.gitignore

### 2. 依赖安全
- 定期更新依赖
- 使用安全扫描工具
- 监控漏洞通知

### 3. 访问控制
- 设置合理的权限
- 使用分支保护
- 启用二次验证

## 📞 技术支持

### 遇到问题？
1. 检查Git配置是否正确
2. 确认网络连接正常
3. 查看错误日志
4. 参考GitHub文档

### 常见错误解决
- **认证失败**: 检查用户名和密码/Token
- **推送被拒绝**: 可能需要先pull远程更改
- **文件过大**: 使用Git LFS处理大文件

---

🎉 **恭喜！您的SearXNG-SGA项目即将成为一个优秀的开源项目！**

通过遵循本指南，您将拥有一个专业、完整的开源项目，为开源社区贡献力量！ 