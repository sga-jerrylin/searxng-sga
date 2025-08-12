## SearXNG-SGA v1.4.0 — 面向中国企业的私有化搜索引擎

更懂中文，更贴企业；以"可私有化部署"为底座，对 SearXNG 做了面向中国企业的深度改造：中文优先、微信专搜、时间优先排序、智能富化增强，以及面向智能体/知识工作流的开箱即用 API。

- 中文完整文档：`README_CN.md`
- 许可证：AGPL-3.0

### 项目定位
- **谁在用**：中国企业/事业单位/研究机构，希望在内网/专有网络中搭建"安全合规"的聚合搜索与资料发现能力。
- **做什么**：融合多源中文内容（含微信公众号），默认时间优先 + 轻量相关性重排；直接返回"模型可用"的富化信息，减少二次爬取与等待。
- **怎么用**：Docker 一键部署；HTTP API 直连智能体/编排平台（Dify、LangChain、Flow 等）。

### 面向中国企业的深度改造
- **中文与公众号优先**：内置中文引擎选择与权重，提供 `/wechat_search` 专用端点
- **时间优先**：默认"最新优先"，更符合新闻/热点/舆情类需求
- **稳定性工程**：微信链路 UA 轮换、指数退避重试、可选代理（`WECHAT_PROXY`）
- **结果去噪与聚合**：列表级去重、低相关过滤、标题/摘要清洗、聚合/跳转域降权
- **智能富化增强（v1.4新增）**：集成 Simple-Crawler 服务，智能内容抽取与质量评分；支持 `enrich_top_k` 参数精确控制富化数量
- **富化返回（expand=full）**：在可控时延内抽取正文、首图/多图、小标题、命中句、提要；一次调用就能给模型"吃饱"
- **可选更强重排**：配置 `ES_URL` 即启用 Lucene(BM25)+时间衰减，更强的相关性与新鲜度平衡

### 适用场景
- 内部情报/舆情监测：新闻/公众号"最新优先"，快速定向检索与比对
- 智能体工具链：HTTP API 直连，减少二段抓取；结果"信息更饱满"更利于快速决策
- 知识沉淀/知识库补齐：结合 ES 重排与富化返回，做主题采集与初步筛选

### 核心能力一览（v1.4.0）
- **API 端点**：`/chinese_search`（推荐）、`/wechat_search`、`/search`
- **富化模式**：`expand=meta | article | full`（默认 meta；full 启用智能富化）
- **智能富化**：`enrich_top_k=N` 精确控制富化数量；集成 Simple-Crawler 服务（端口3002）
- **富化字段**：`article`、`content`、`content_excerpt`、`first_image`、`images[]`、`headings`、`summary_simple`、`snippet_sentences[]`、`bullet_points[]`、`canonical_url`、`site_name`、`source_score`、`quality_score`、`reason[]`
- **缓存策略**：查询结果 60s 短缓存；URL 级富化结果 6h 缓存
- **稳定性保障**：微信链路 UA 轮换、退避重试、可选代理 `WECHAT_PROXY`

### 架构与技术路线（简述）
- **Web 层（Flask）**：路由、参数解析、短缓存、富化控制、ES 可选重排
- **引擎层**：`searx/engines/*`（含 `wechat.py`、`sogou_wechat.py` 等）
- **聚合与去噪**：`searx/results.py` + Web 层清洗/重排工具
- **智能富化服务**：Simple-Crawler（Node.js）+ 质量评分算法；严格 Top-K 与超时预算
- **可选 ES**：`ES_URL` 存在即索引 + BM25+时间衰减重排

### 快速部署
- Docker（推荐）
```bash
docker compose up --build -d
```
- Windows PowerShell（快速体验）
```powershell
$env:PYTHONPATH="$PWD"; python -m searx.webapp
```
- Linux/macOS（快速体验）
```bash
export PYTHONPATH="$PWD" && python -m searx.webapp
```

### API 使用指南（面向智能体）

#### 1. 搜索 API 端点
- **中文搜索（推荐）**：`/chinese_search` - 中文优化，时间优先排序
- **微信专搜**：`/wechat_search` - 专门搜索微信公众号内容
- **通用搜索**：`/search` - 兼容原版 SearXNG API

#### 2. 智能富化参数（v1.4新增）
- `expand=full` - 启用智能富化模式
- `enrich_top_k=N` - 对前N个结果进行富化（推荐2-5）
- `enrich_timeout_ms=2500` - 富化总超时时间（毫秒）

#### 3. API 调用示例
```bash
# 中文搜索 + 智能富化（推荐）
curl "http://localhost:8888/chinese_search?q=人工智能&expand=full&enrich_top_k=3"

# 微信公众号专搜 + 富化
curl "http://localhost:8888/wechat_search?q=GPT&expand=full&enrich_top_k=2"

# 基础搜索（无富化）
curl "http://localhost:8888/chinese_search?q=新闻&expand=meta"
```

#### 4. 爬虫 API（Simple-Crawler 服务）
```bash
# 直接调用爬虫服务（端口3002）
curl -X POST http://localhost:3002/v0/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### 5. 富化响应字段说明
- `site_name`: 站点名称（富化后为"Crawler Enhanced"）
- `quality_score`: 内容质量评分（0-1）
- `source_score`: 来源可信度评分（0-1）
- `content`: 完整文章内容
- `content_excerpt`: 内容摘要
- `canonical_url`: 规范化URL
- `reason`: 质量评分依据

#### 6. 网页界面
- **搜索界面**：`http://localhost:8888/` - 可视化搜索界面
- **设置页面**：`http://localhost:8888/preferences` - 搜索引擎配置
- **统计信息**：`http://localhost:8888/stats` - 使用统计

### 服务架构说明
- **SearXNG 主服务**：端口 8888 - 搜索聚合与API服务
- **Simple-Crawler**：端口 3002 - 智能内容抓取服务
- **Elasticsearch**：端口 9200 - 可选的重排服务
- **Redis**：端口 6379 - 缓存服务

### 与开源 SearXNG 的差异
- 中文生态优化：引擎优选、时间优先、去噪清洗、聚合域识别
- 微信专搜：专用端点 + 稳定性工程（UA/退避/代理）
- 面向智能体的富化返回：一次调用就拿到"可判别"的上下文
- 可选 ES 重排：生产级相关性与新鲜度融合
- 智能富化增强：集成专用爬虫服务，质量评分算法

### 安全与合规（要点）
- 私有化部署（内网/专有网络），不上传企业数据
- 建议按企业合规要求配置出口代理与访问白名单
- 对微信公众号等来源，请遵循平台条款与当地法律法规

### v1.4.0 更新内容
- ✅ 新增 Simple-Crawler 智能富化服务
- ✅ 支持 `enrich_top_k` 参数精确控制富化数量
- ✅ 智能内容质量评分算法
- ✅ 富化结果缓存优化
- ✅ 完善的错误处理与降级机制
- ✅ 详细的调试日志与监控

### Roadmap（方向）
- 富化质量持续优化（领域模板、规则增强）
- 企业级观测与审计（指标、日志、追踪）
- 更多中文内容源接入与质量打分
- 多语言富化支持

### 许可证
AGPL-3.0（网络部署需开源修改，详见 LICENSE）。

—— 让企业的"私域搜索"更懂中文、更安全可控，也更"好用"。如果你在智能体或知识工作流中用到它，欢迎在 Issues 里分享实践与想法！
