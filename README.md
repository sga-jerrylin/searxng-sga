# SearXNG-SGA

更懂中文、更易集成的 SearXNG 企业增强版：中文优先排序、微信公众号专搜、开箱即用的 API 与 Docker 部署。

- 中文完整文档：README_CN.md
- License：AGPL-3.0

## ✨ 本版本亮点（v1.2.0）
- Web 前端
  - ⏱ 默认“按时间”排序（最新优先）
  - 🔎 组内相关性轻重排、列表级去重、标题/摘要清洗
- API 端
  - 🌟 新增中文搜索 API（/chinese_search）
  - 📱 微信专搜 API（/wechat_search）
  - ⚡ 轻量重排、60s 短缓存、可选 debug_score、可选 Lucene(BM25)+时间衰减
- 稳定性
  - 🧰 UA 轮换、指数退避重试、可选代理（WECHAT_PROXY）

## 🚀 快速开始
- 本地运行
  ```bash
  # Windows PowerShell
  $env:PYTHONPATH="$PWD"; python -m searx.webapp
  # Linux / macOS
  export PYTHONPATH="$PWD" && python -m searx.webapp
  ```
- Docker（推荐）
  ```bash
  docker-compose up --build -d
  ```
- API 示例
  ```bash
  # 中文搜索（推荐）
  curl "http://localhost:8888/chinese_search?q=人工智能&limit=10"
  # 微信专搜
  curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=8"
  ```

## ☁️ 云端部署更新指南（已在云端部署用户）
场景：已部署 v1.1.0，升级到 v1.1.1。

方式 A：按版本标签升级（推荐）
1) git fetch --all --tags
2) git checkout v1.2.0
3) docker-compose up --build -d
4) curl http://localhost:8888/healthz

方式 B：跟随 master（不固定版本）
1) git checkout master && git pull --ff-only
2) docker-compose up --build -d
3) curl http://localhost:8888/healthz

未使用 Docker：
```bash
pip install -r requirements.txt
export PYTHONPATH="$PWD" && python -m searx.webapp
```

## 🔗 与 Dify 的集成
- Dify Docker 环境请使用 `http://host.docker.internal:8888`
- 推荐 HTTP 请求节点调用 `/chinese_search`、`/wechat_search`
- 更多示例见 README_CN.md

## 🗺️ Roadmap
- v1.1.x：文档完善与稳定性优化
- v1.2.x：更多中文内容源与可选更强重排策略

欢迎在 Issues 提需求或反馈问题。

