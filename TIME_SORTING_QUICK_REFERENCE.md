# ⏰ 时间排序功能快速参考指南

## 🚀 快速开始

### 基本用法（默认启用时间排序）
```bash
# 中文搜索 - 自动按时间排序
curl "http://localhost:8080/chinese_search?q=人工智能"

# 微信搜索 - 自动按时间排序
curl "http://localhost:8080/wechat_search?q=ChatGPT"
```

### 高级用法（可配置排序）
```bash
# 关闭时间排序
curl "http://localhost:8080/chinese_search?q=人工智能&sort_by_time=false"

# 指定返回条数
curl "http://localhost:8080/chinese_search?q=人工智能&limit=20&sort_by_time=true"

# 指定搜索引擎
curl "http://localhost:8080/chinese_search?q=人工智能&engines=sogou,baidu&sort_by_time=true"
```

## 📋 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sort_by_time` | boolean | `true` | 是否按时间排序（从最新到最旧） |
| 支持的值 | - | - | `true`, `1`, `yes` 或 `false`, `0`, `no` |

## 🔧 Python 调用示例

```python
import requests

# 默认启用时间排序
response = requests.get('http://localhost:8080/chinese_search', {
    'q': '人工智能',
    'limit': 10
})

# 关闭时间排序
response = requests.get('http://localhost:8080/chinese_search', {
    'q': '人工智能',
    'sort_by_time': False
})

# 微信搜索 - 默认启用时间排序
response = requests.get('http://localhost:8080/wechat_search', {
    'q': 'ChatGPT',
    'limit': 8
})
```

## 🔗 Dify 集成配置

### 重要提醒
**在 Dify Docker 环境中，必须使用 `host.docker.internal` 地址！**

```json
{
  "name": "chinese_search",
  "description": "中文搜索工具，自动按时间排序",
  "method": "GET",
  "url": "http://host.docker.internal:8888/chinese_search",
  "parameters": {
    "q": "{{query}}",
    "limit": "{{limit|default:10}}",
    "engines": "{{engines|default:sogou,baidu,360search,wechat}}",
    "sort_by_time": "{{sort_by_time|default:true}}"
  }
}
```

## 📊 响应格式示例

```json
{
  "query": "人工智能",
  "number_of_results": 5,
  "results": [
    {
      "title": "2024年人工智能最新突破",
      "url": "https://example.com/ai-2024",
      "content": "最新的人工智能技术发展...",
      "publishedDate": "2024-01-15T10:30:00Z",
      "engine": "sogou"
    },
    {
      "title": "AI技术在医疗领域的应用",
      "url": "https://example.com/ai-medical",
      "content": "人工智能在医疗诊断中的应用...",
      "publishedDate": "2024-01-12T14:20:00Z",
      "engine": "baidu"
    }
  ]
}
```

## ⚡ 性能优化建议

1. **默认启用排序**：获取最新、最相关的内容
2. **合理设置limit**：避免返回过多结果影响性能
3. **必要时关闭排序**：如果不需要时间排序，可设置 `sort_by_time=false` 提升性能
4. **选择合适引擎**：根据内容类型选择最佳搜索引擎

## 🔍 使用场景

- **新闻资讯搜索**：获取最新新闻和资讯
- **技术文档搜索**：获取最新的技术文档和教程
- **微信公众号搜索**：获取最新的公众号文章
- **学术论文搜索**：获取最新的研究成果

## 📝 技术细节

### 支持的时间格式
- ISO 8601: `2024-01-15T10:30:00Z`
- 标准格式: `2024-01-15 10:30:00`
- 自动解析多种格式

### 排序逻辑
1. 提取 `publishedDate` 字段
2. 解析时间格式
3. 转换为时间戳
4. 按负时间戳排序（最新在前）
5. 无时间信息的结果排到最后

### 错误处理
- 时间解析失败时跳过该结果
- 记录警告日志
- 不影响其他结果的排序 