# Dify 工作流集成指南

## 🎯 概述

本指南详细说明如何在 Dify 平台中集成 SearXNG-SGA 的专用搜索 API，实现高效的中文搜索和微信公众号搜索功能。

## ⚠️ 重要提醒

**Dify 平台内置的 SearXNG 插件与本项目 API 不兼容！**

请使用 Dify 工作流中的 **HTTP 请求节点** 调用我们的专用 API。

## 🔧 工作流配置步骤

### 1. 创建新的工作流

1. 在 Dify 平台中创建新的工作流
2. 选择 "工作流" 类型
3. 进入工作流编辑界面

### 2. 添加 HTTP 请求节点

#### 中文搜索工具配置

**节点名称**: `chinese_search`

**基本配置**:
```json
{
  "name": "chinese_search",
  "description": "中文搜索工具，使用优质中文搜索引擎",
  "method": "GET",
  "url": "http://host.docker.internal:8888/chinese_search"
}
```

### ⚠️ 重要提醒
**在Dify平台中，必须使用 `host.docker.internal` 而不是 `localhost`！**

**请求参数**:
```json
{
  "q": "{{query}}",
  "limit": "{{limit|default:10}}",
  "engines": "{{engines|default:sogou,baidu,360search,wechat}}"
}
```

**请求头**:
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

#### 微信搜索工具配置

**节点名称**: `wechat_search`

**基本配置**:
```json
{
  "name": "wechat_search",
  "description": "微信公众号专搜工具",
  "method": "GET",
  "url": "http://host.docker.internal:8888/wechat_search"
}
```

**请求参数**:
```json
{
  "q": "{{query}}",
  "limit": "{{limit|default:10}}"
}
```

**请求头**:
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

### 3. 配置输入变量

#### 中文搜索工具输入变量

| 变量名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `query` | 文本 | ✅ | - | 搜索关键词 |
| `limit` | 数字 | ❌ | 10 | 返回结果数量 (1-100) |
| `engines` | 文本 | ❌ | sogou,baidu,360search,wechat | 搜索引擎列表 |

#### 微信搜索工具输入变量

| 变量名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `query` | 文本 | ✅ | - | 搜索关键词 |
| `limit` | 数字 | ❌ | 10 | 返回结果数量 (1-100) |

### 4. 配置输出处理

#### 响应数据结构

```json
{
  "query": "搜索关键词",
  "number_of_results": 10,
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

#### 输出变量提取

**主要结果**:
- `{{chinese_search.results}}` - 搜索结果数组
- `{{chinese_search.query}}` - 搜索关键词
- `{{chinese_search.number_of_results}}` - 结果数量

**单个结果字段**:
- `{{result.title}}` - 文章标题
- `{{result.url}}` - 文章链接
- `{{result.content}}` - 文章摘要
- `{{result.engine}}` - 搜索引擎

### 5. 错误处理配置

#### 超时设置
- **建议超时时间**: 30 秒
- **重试次数**: 2-3 次
- **重试间隔**: 1-2 秒

#### 错误处理逻辑

```json
{
  "error_handling": {
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 1,
    "fallback_response": {
      "query": "{{query}}",
      "results": [],
      "error": "搜索服务暂时不可用"
    }
  }
}
```

## 🎨 完整工作流示例

### 智能搜索助手工作流

```yaml
name: "智能搜索助手"
description: "结合中文搜索和微信搜索的智能助手"

workflow:
  # 步骤1: 判断搜索类型
  - name: "search_type_decision"
    type: "condition"
    condition: "{{query.contains('微信') or query.contains('公众号')}}"
    
  # 步骤2a: 微信搜索分支
  - name: "wechat_search"
    type: "http_request"
    condition: "{{search_type_decision == true}}"
    config:
      method: "GET"
      url: "http://localhost:8888/wechat_search"
      params:
        q: "{{query}}"
        limit: "{{limit|default:10}}"
    
  # 步骤2b: 中文搜索分支
  - name: "chinese_search"
    type: "http_request"
    condition: "{{search_type_decision == false}}"
    config:
      method: "GET"
      url: "http://localhost:8888/chinese_search"
      params:
        q: "{{query}}"
        limit: "{{limit|default:10}}"
        engines: "{{engines|default:sogou,baidu}}"
    
  # 步骤3: 结果整合
  - name: "result_processing"
    type: "code"
    code: |
      # 整合搜索结果
      if wechat_search.results:
          results = wechat_search.results
          search_type = "微信搜索"
      else:
          results = chinese_search.results
          search_type = "中文搜索"
      
      # 格式化输出
      formatted_results = []
      for result in results[:5]:  # 取前5条
          formatted_results.append({
              "title": result.get("title", ""),
              "summary": result.get("content", "")[:200] + "...",
              "url": result.get("url", ""),
              "source": result.get("engine", "")
          })
      
      return {
          "search_type": search_type,
          "results": formatted_results,
          "total_count": len(results)
      }
```

### 简单搜索工作流

```yaml
name: "简单中文搜索"
description: "基础的中文搜索功能"

workflow:
  # 步骤1: 执行搜索
  - name: "search"
    type: "http_request"
    config:
      method: "GET"
      url: "http://localhost:8888/chinese_search"
      params:
        q: "{{query}}"
        limit: "{{limit|default:10}}"
        engines: "sogou,baidu"
      timeout: 30
    
  # 步骤2: 格式化结果
  - name: "format_results"
    type: "template"
    template: |
      搜索关键词: {{query}}
      找到 {{search.number_of_results}} 条结果:
      
      {% for result in search.results %}
      {{ loop.index }}. **{{result.title}}**
         摘要: {{result.content[:150]}}...
         链接: {{result.url}}
         来源: {{result.engine}}
      
      {% endfor %}
```

## 🚀 使用示例

### 1. 基本搜索调用

```bash
# 本地测试
curl -X GET "http://localhost:8888/chinese_search?q=人工智能&limit=5&engines=sogou,baidu"

# Dify平台测试（重要：使用host.docker.internal）
curl -X GET "http://host.docker.internal:8888/chinese_search?q=人工智能&limit=5&engines=sogou,baidu"
curl -X GET "http://host.docker.internal:8888/wechat_search?q=ChatGPT&limit=8"
```

### 2. Python 调用示例

```python
import requests

def call_chinese_search(query, limit=10, engines="sogou,baidu"):
    """调用中文搜索API"""
    # 本地开发使用localhost，Dify平台使用host.docker.internal
    url = "http://host.docker.internal:8888/chinese_search"
    params = {
        "q": query,
        "limit": limit,
        "engines": engines
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "results": []}

def call_wechat_search(query, limit=10):
    """调用微信搜索API"""
    # 本地开发使用localhost，Dify平台使用host.docker.internal
    url = "http://host.docker.internal:8888/wechat_search"
    params = {
        "q": query,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "results": []}

# 使用示例
results = call_chinese_search("人工智能", limit=5, engines="sogou,baidu")
wechat_results = call_wechat_search("ChatGPT", limit=8)
```

### 3. JavaScript 调用示例

```javascript
// 中文搜索函数
async function chineseSearch(query, limit = 10, engines = "sogou,baidu") {
    // 本地开发使用localhost，Dify平台使用host.docker.internal
    const url = new URL("http://host.docker.internal:8888/chinese_search");
    url.searchParams.set("q", query);
    url.searchParams.set("limit", limit);
    url.searchParams.set("engines", engines);
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        return { error: error.message, results: [] };
    }
}

// 微信搜索函数
async function wechatSearch(query, limit = 10) {
    // 本地开发使用localhost，Dify平台使用host.docker.internal
    const url = new URL("http://host.docker.internal:8888/wechat_search");
    url.searchParams.set("q", query);
    url.searchParams.set("limit", limit);
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        return { error: error.message, results: [] };
    }
}

// 使用示例
(async () => {
    const results = await chineseSearch("人工智能", 5, "sogou,baidu");
    const wechatResults = await wechatSearch("ChatGPT", 8);
    
    console.log("中文搜索结果:", results);
    console.log("微信搜索结果:", wechatResults);
})();
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 连接超时
**问题**: 请求超时，无法获取结果
**解决方案**:
- 增加超时时间到30-60秒
- 检查SearXNG服务是否正常运行
- 确认网络连接正常

#### 2. 搜索引擎不可用
**问题**: 特定搜索引擎返回错误
**解决方案**:
- 检查 `unresponsive_engines` 字段
- 尝试使用其他搜索引擎
- 减少并发搜索引擎数量

#### 3. 返回结果为空
**问题**: 搜索返回空结果
**解决方案**:
- 尝试不同的搜索关键词
- 检查搜索引擎是否被屏蔽
- 使用微信搜索API进行对比

#### 4. JSON 解析错误
**问题**: 响应格式不正确
**解决方案**:
- 检查API端点是否正确
- 确认请求参数格式
- 查看服务器日志

### 调试技巧

1. **启用详细日志**:
```bash
export SEARXNG_DEBUG=1
python -m searx.webapp
```

2. **使用测试脚本**:
```bash
python test_new_apis.py
```

3. **检查服务状态**:
```bash
curl "http://localhost:8888/healthz"
```

## 📊 性能优化建议

### 1. 搜索引擎选择
- **快速搜索**: 使用 `sogou` 或 `360search`
- **全面搜索**: 使用 `sogou,baidu,360search`
- **微信专搜**: 使用 `/wechat_search` 端点

### 2. 结果数量控制
- **快速预览**: `limit=5`
- **标准搜索**: `limit=10`
- **详细搜索**: `limit=20`

### 3. 缓存策略
- 对相同查询结果进行缓存
- 设置合理的缓存过期时间
- 使用Redis或内存缓存

### 4. 并发控制
- 限制同时进行的搜索请求数量
- 使用队列管理搜索任务
- 实现请求去重机制

## 📖 相关文档

- [API 使用指南](API_USAGE_GUIDE.md) - 完整的API文档
- [兼容性修复说明](DIFY_COMPATIBILITY_FIX.md) - 技术细节
- [测试脚本使用](test_new_apis.py) - 功能测试

## 🎉 总结

通过本指南，您可以在 Dify 平台中成功集成 SearXNG-SGA 的专用搜索API，实现：

- ✅ 高效的中文搜索功能
- ✅ 专业的微信公众号搜索
- ✅ 灵活的搜索引擎选择
- ✅ 可控的返回结果数量
- ✅ 完善的错误处理机制

现在您可以构建强大的AI搜索应用了！ 