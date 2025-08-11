# SearXNG-SGA v1.2.1 — 面向智能体的中文搜索引擎（企业增强版）

更懂中文、更快更干净、结果信息更“饱满”。内置微信专搜、时间优先排序、轻量正文抽取与富化返回，一次调用就能给智能体足够上下文做判断。

- 中文主文档：README_CN.md
- License：AGPL-3.0

## ✨ 亮点（v1.2.1）
- 中文与公众号内容优先：默认时间优先排序，近期内容权重更高
- 微信专搜 API：稳定应对 UA 轮换、退避重试、可选代理（WECHAT_PROXY）
- 轻量富化 expand=article：Top-K 并发抓取，抽取正文、首图/多图、小标题、命中句、提要
- 更多返回字段：`images[]`、`snippet_sentences[]`、`bullet_points[]`、`amp_url`、`canonical_url`、`source_score`、`quality_score`
- 缓存：查询 60s 短缓存，URL 级富化 6h 缓存
- 可选更强重排：设置 `ES_URL` 启用 Lucene(BM25)+时间衰减

## 🚀 快速开始
- 本地运行（Windows PowerShell）
```powershell
$env:PYTHONPATH="$PWD"; python -m searx.webapp
```
- 本地运行（Linux/macOS）
```bash
export PYTHONPATH="$PWD" && python -m searx.webapp
```
- Docker（推荐）
```bash
docker compose up --build -d
```

## 📡 API（面向智能体）
### 1) 中文搜索 `/chinese_search`
- 常用参数：
  - `q`: 关键词（必填）
  - `limit`: 返回条数，1–100（默认10）
  - `sort_by_time`: 是否时间优先（默认true）
  - `expand`: `meta | article | full`（默认 meta；article 启用正文抽取与富化）
  - `enrich_top_k`: 富化条数（默认6）
  - `enrich_per_req_ms`: 单条富化预算（默认800ms）
  - `enrich_timeout_ms`: 富化总预算（默认1200ms）
  - `max_article_chars`: 正文截断（默认1500）
  - `include`: 逗号分隔返回字段过滤，如 `article,images,quality_score`
- 示例（浏览器直开）：
  - 基础（meta 富化）：
    - `http://localhost:8888/chinese_search?q=gpt5&limit=10&expand=meta&include=cover_image,site_name,quality_score`
  - 文章抽取（Top-5，2.5s 总预算）：
    - `http://localhost:8888/chinese_search?q=gpt5&expand=article&enrich_top_k=5&enrich_per_req_ms=1000&enrich_timeout_ms=2500&max_article_chars=2000&include=article,first_image,images,headings,summary_simple,snippet_sentences,bullet_points,amp_url,canonical_url,site_name,source_score,quality_score,reason`

### 2) 微信专搜 `/wechat_search`
- 参数与 `chinese_search` 基本一致（无需 engines）
- 示例（文章抽取）：
  - `http://localhost:8888/wechat_search?q=gpt5&expand=article&enrich_top_k=4&enrich_per_req_ms=1000&enrich_timeout_ms=1800&max_article_chars=2000&include=article,first_image,images,headings,summary_simple,site_name,source_score,quality_score,reason`

## 🤖 Dify/编排平台接入
- 容器内访问宿主机请用：`http://host.docker.internal:8888`
- 推荐使用 HTTP 请求节点，选择 `/chinese_search` 或 `/wechat_search`

## ⚙️ 可选：Elasticsearch 重排
- 设置 `ES_URL=http://es:9200` 即启用（docker-compose 已包含单节点）
- API 端会将结果索引并用 BM25+时间衰减重排，相关性进一步提升

## 🛠 故障排查
- 403/JSON 问题：确保 `searx/settings.yml` 中 `search.formats` 包含 `json`
- 微信无结果：开启代理 `WECHAT_PROXY`，适度放宽 `limit`
- 超时：提升 `enrich_per_req_ms` 与 `enrich_timeout_ms`，或降低 `enrich_top_k`

## 📄 许可证
AGPL-3.0。网络部署需开源修改，详见 LICENSE。

—— 想让智能体“一次拿全料”？试试 `expand=article + include=article,images,snippet_sentences,quality_score`！
