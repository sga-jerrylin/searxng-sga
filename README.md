# SearXNG-SGA

面向中文搜索与企业集成优化的 SearXNG 增强版本，提供中文优先排序、微信公众号专搜与更友好的 API 接口。

- 中文详细说明与完整文档请查看：README_CN.md
- 许可证：AGPL-3.0

## 亮点功能（v1.1.x）
- 中文搜索 API（时间优先排序，最新内容优先）
- 微信公众号专搜 API
- 轻量相关性重排、列表级去重与摘要清洗
- 可选代理、UA 轮换与指数退避重试
- 60s 缓存（API 层）

## 快速开始

### 本地运行
```bash
# Windows PowerShell
$env:PYTHONPATH="$PWD"; python -m searx.webapp

# Linux / macOS
export PYTHONPATH="$PWD" && python -m searx.webapp
```

### Docker（推荐）
```bash
docker-compose up --build -d
```

### API 例子
```bash
# 中文搜索（推荐）
curl "http://localhost:8888/chinese_search?q=人工智能&limit=10"

# 微信专搜
curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=8"
```

更多接口说明与 Dify 集成示例：README_CN.md

---

## 云端部署更新指南（适用于已在云端部署的用户）
> 场景：你已经在一台云服务器上部署了 v1.1.0，现在希望从 GitHub Release 升级到最新的 v1.1.1。

以下两种方式二选一：

### 方式 A：通过 Git 标签升级（从源码部署）
1. 登录你的云服务器（通过 SSH）
2. 进入项目目录：
   ```bash
   cd /path/to/searxng-sga
   ```
3. 拉取最新代码与标签：
   ```bash
   git fetch --all --tags
   ```
4. 切换到目标版本（示例：v1.1.1）：
   ```bash
   git checkout v1.1.1
   ```
5. 使用 Docker 重建并后台运行：
   ```bash
   docker-compose up --build -d
   ```
6. 验证服务：
   ```bash
   curl "http://localhost:8888/healthz"
   ```

注意：如果你未使用 Docker 而是直接运行 Python，请确保：
```bash
pip install -r requirements.txt
export PYTHONPATH="$PWD" && python -m searx.webapp
```

### 方式 B：仍在 master 跟随最新提交（不固定版本）
1. 登录云服务器，进入项目目录
2. 拉取并切换到 master 最新：
   ```bash
   git checkout master
   git pull --ff-only
   ```
3. 使用 Docker 重建并后台运行：
   ```bash
   docker-compose up --build -d
   ```
4. 验证服务：
   ```bash
   curl "http://localhost:8888/healthz"
   ```

建议生产环境使用“方式 A”按版本标签升级，方便回滚与追踪变更。

---

## 与 Dify 的集成
- Dify 运行在 Docker 环境时，请使用 `http://host.docker.internal:8888` 访问本服务
- 推荐在工作流中使用 HTTP 请求节点调用：`/chinese_search`、`/wechat_search`
- 详细示例见 README_CN.md

---

## 路线图（Roadmap）
- v1.1.x：文档完善、稳定性提升
- v1.2.x：更多中文内容源端点、可选的更强重排策略

欢迎在 Issues 提需求或反馈问题。

