新增
- Lucene(BM25)+时间衰减重排（API 端，配置 ES_URL 即启用；无则自动回退本地重排）

API
- /wechat_search、/chinese_search：默认开启时间排序；缓存键包含 time 维度；支持 debug_score 透出

稳定性
- 微信引擎：request() 返回修复；跳转 URL 解析修正；UA 轮换与退避重试；可选代理 WECHAT_PROXY

结果质量
- 列表级去重（URL 指纹 + 标题近似）、低相关过滤、标题/摘要清洗

文档
- 新增 ARCHITECTURE_CN.md；更新 README_CN.md / README.md 到 v1.2.0

版本
- v1.2.0
