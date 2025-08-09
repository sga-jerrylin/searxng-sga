## 技术架构（SearXNG-SGA v1.1.1）

### 1. 总览
- Web 层：`searx/webapp.py`（Flask）
  - 路由：`/search`、`/chinese_search`、`/wechat_search`、`/healthz`
  - 统一参数解析、结果渲染、轻量缓存（内存 TTL）
- 引擎层：`searx/engines/*.py`
  - 例如：`wechat.py`、`sogou_wechat.py`、`sogou.py`、`baidu.py` 等
  - 负责拼装请求、抓取 HTML/JSON 并解析为统一结果结构
- 网络层：`searx/network/*`（基于 httpx）
  - 统一超时/重试/代理/HTTP 错误处理，支持流式响应
- 结果容器：`searx/results.py`
  - 统一聚合、去重、评分、排序、分组、元数据统计
- 排序与清洗：`searx/webapp.py` 内部工具函数
  - 列表级去重、文本清洗、低相关过滤
  - 相关性启发式重排 + 时间微偏好
  - 可选 Elasticsearch（Lucene BM25 + 时间衰减）重排
- 配置：`searx/settings.yml` + 环境变量
  - 引擎开关、分类、格式、端口、默认主题等
- 运行：Docker/Docker Compose 或 Python 直接运行

### 2. API 流程（/wechat_search、/chinese_search）
1) 参数解析：`q`、`limit`、`engines`（仅中文）、`sort_by_time`（默认 true）
2) 构造 `SearchQuery` 并强制引擎列表（仅微信或指定中文引擎）
3) 搜索执行：`searx.search.SearchWithPlugins(...).search()`，返回 `ResultContainer`
4) 结果处理：
   - `get_ordered_results()` → 列表级去重、文本清洗
   - 轻量相关性重排 + 时间偏好（可 `debug_score` 透出）
   - 可选时间排序（`sort_by_time`）与 `limit` 截断
   - 可选 ES 重排（见第 4 节）
5) JSON 输出：`searx/webutils.get_json_response()`（保证类型安全/可序列化）
6) 短期缓存：60s 内存缓存（键包含 query/limit/time/debug 等）

### 3. 微信引擎稳健性
- UA 轮换 + 真实 Referer + 禁缓存控制头
- 指数退避重试（`wechat.py:parse_url2`）
- 可选代理：`WECHAT_PROXY=http://host:port`
- 规范化链接解析（sogou/weixin 跳转）

### 4. Lucene（Elasticsearch）重排
- 开关：设置 `ES_URL` 即启用；未设置则回退到本地重排
- 流程：
  1) `结果 → _bulk` 索引到 `sga`（字段：url/title/content/publishedDate）
  2) `function_score` 查询：BM25 + `gauss(publishedDate, origin=now, scale=7d)`
  3) 根据 `_score` 对结果排序或融合
- 适用：`/wechat_search`、`/chinese_search`
- 网页端 `/search`：默认未接 ES（可按需启用）

### 5. 排序与过滤（本地）
- 相关性启发（标题/摘要包含度、前缀强化、覆盖率）
- 时间偏好（最近 7 天线性加权）
- 组内重排（仅网页端同模板分组）
- 低相关过滤（对聚合/跳转域更严格）
- 列表级去重（URL 指纹 + 标题近似）

### 6. 配置与环境变量
- `ES_URL`：启用 ES/Lucene 重排（例：`http://es:9200`）
- `WECHAT_PROXY`：微信引擎出网代理（例：`http://host.docker.internal:7890`）
- `server.bind_address/port`：监听地址/端口
- `search.formats`：启用 `json` 格式
- 引擎开关/分类：`searx/settings.yml`

### 7. 运行与部署
- Docker Compose（推荐）：`redis` + `es` + `searxng`
- 端口：`searxng:8888`、`es:9200`
- Windows 下 ES 资源限制：`ES_JAVA_OPTS=-Xms512m -Xmx512m`

### 8. 观测与故障排查
- `/healthz`：存活检查
- `docker compose logs -f searxng`：查看错误堆栈（关键词：`wechat search error`）
- 常见：
  - 反爬：加 `WECHAT_PROXY` 并适度放宽 `limit`
  - ES 未就绪：会自动回退，不应 500；若异常请贴堆栈
  - JSON 403：确保 `search.formats` 包含 `json`

### 9. 版本与发布
- 版本号：`searx/version.py`（若无 git 环境，使用 fallback 值）
- Release：打 tag（如 `v1.1.1`），Docker 重建并推送，生成发行说明


