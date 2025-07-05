# SearXNG 中文搜索 API 使用指南

## 📋 API 概览

SearXNG-SGA 提供了两个专门的中文搜索API：

1. **`/chinese_search`** - 通用中文搜索API
2. **`/wechat_search`** - 微信公众号专搜API

## 🔍 1. 中文搜索API (`/chinese_search`)

### 功能特点
- 使用优质中文搜索引擎：sogou, baidu, 360search, wechat
- 支持自定义搜索引擎组合
- 可控制返回结果数量
- 专门优化中文搜索体验

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | ✅ | - | 搜索关键词 |
| `limit` | integer | ❌ | 10 | 返回结果数量 (1-100) |
| `engines` | string | ❌ | sogou,baidu,360search,wechat | 指定搜索引擎，用逗号分隔 |
| `sort_by_time` | boolean | ❌ | true | 是否按时间排序（从最新到最旧） |

### 使用示例

```bash
# 基本搜索
curl "http://localhost:8888/chinese_search?q=龙树谅"

# 限制返回5条结果
curl "http://localhost:8888/chinese_search?q=龙树谅&limit=5"

# 只使用搜狗和百度
curl "http://localhost:8888/chinese_search?q=龙树谅&engines=sogou,baidu"

# 返回更多结果
curl "http://localhost:8888/chinese_search?q=龙树谅&limit=20"

# 关闭时间排序
curl "http://localhost:8888/chinese_search?q=龙树谅&sort_by_time=false"
```

### Python 调用示例

```python
import requests

# 基本搜索
response = requests.get('http://localhost:8888/chinese_search', params={
    'q': '龙树谅',
    'limit': 10
})
results = response.json()

# 指定搜索引擎
response = requests.get('http://localhost:8888/chinese_search', params={
    'q': '龙树谅',
    'engines': 'sogou,baidu',
    'limit': 15
})
results = response.json()
```

## 📱 2. 微信搜索API (`/wechat_search`)

### 功能特点
- 专门搜索微信公众号内容
- 使用微信相关搜索引擎
- 独立的API端点，保持专业性

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | ✅ | - | 搜索关键词 |
| `limit` | integer | ❌ | 10 | 返回结果数量 (1-100) |
| `sort_by_time` | boolean | ❌ | true | 是否按时间排序（从最新到最旧） |

### 使用示例

```bash
# 微信公众号搜索
curl "http://localhost:8888/wechat_search?q=龙树谅"

# 限制返回结果
curl "http://localhost:8888/wechat_search?q=龙树谅&limit=8"

# 关闭时间排序
curl "http://localhost:8888/wechat_search?q=龙树谅&sort_by_time=false"
```

### Python 调用示例

```python
import requests

# 微信搜索
response = requests.get('http://localhost:8888/wechat_search', params={
    'q': '龙树谅',
    'limit': 10
})
results = response.json()
```

## 🎯 3. Dify 集成示例

### 工具配置

```json
{
  "name": "chinese_search",
  "description": "中文搜索工具",
  "parameters": {
    "type": "object",
    "properties": {
      "q": {
        "type": "string",
        "description": "搜索关键词"
      },
      "limit": {
        "type": "integer",
        "description": "返回结果数量",
        "default": 10,
        "minimum": 1,
        "maximum": 100
      },
      "engines": {
        "type": "string",
        "description": "搜索引擎，用逗号分隔",
        "default": "sogou,baidu,360search,wechat"
      },
      "sort_by_time": {
        "type": "boolean",
        "description": "是否按时间排序（从最新到最旧）",
        "default": true
      }
    },
    "required": ["q"]
  }
}
```

### 调用示例

```python
# Dify 工具调用
def chinese_search_tool(q, limit=10, engines="sogou,baidu,360search,wechat", sort_by_time=True):
    url = "http://localhost:8888/chinese_search"
    params = {
        "q": q,
        "limit": limit,
        "engines": engines,
        "sort_by_time": sort_by_time
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

## 🔧 4. 可用搜索引擎

### 中文搜索引擎
- `sogou` - 搜狗搜索
- `baidu` - 百度搜索  
- `360search` - 360搜索
- `wechat` - 微信搜索

### 微信专搜引擎
- `wechat` - 微信公众号搜索
- `sogou wechat` - 搜狗微信搜索

## 📊 5. 响应格式

### 成功响应
```json
{
  "query": "龙树谅",
  "number_of_results": 5,
  "results": [
    {
      "title": "文章标题",
      "url": "https://example.com",
      "content": "文章摘要内容...",
      "engine": "sogou"
    }
  ],
  "answers": [],
  "corrections": [],
  "infoboxes": [],
  "suggestions": [],
  "unresponsive_engines": []
}
```

### 错误响应
```json
{
  "error": "No query provided",
  "message": "请提供搜索关键词"
}
```

## 🚀 6. 性能优化建议

1. **合理设置limit**：根据需要设置返回结果数量，避免过多无用结果
2. **选择合适引擎**：根据搜索内容选择最相关的搜索引擎
3. **缓存结果**：对于相同查询，可以缓存结果减少API调用
4. **错误处理**：实现重试机制和错误处理逻辑
5. **时间排序**：默认启用时间排序获取最新内容，如不需要可设置`sort_by_time=false`提升性能

## 📝 7. 注意事项

- API 默认返回 JSON 格式
- 搜索引擎可能因网络问题暂时不可用
- 建议在生产环境中设置适当的超时时间
- 微信搜索API专门用于微信内容，通用搜索请使用中文搜索API

## 🔗 8. 相关链接

- [SearXNG 官方文档](https://docs.searxng.org/)
- [API 兼容性修复说明](./DIFY_COMPATIBILITY_FIX.md)
- [中文配置指南](./README_CN.md) 