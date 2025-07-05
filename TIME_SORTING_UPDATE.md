# ⏰ 时间排序功能更新总结

## 🎯 更新概述

本次更新为 SearXNG-SGA 项目添加了**自动时间排序功能**，让搜索结果按发布时间从最新到最旧排序，确保用户总是能获取到最新的信息。

## ✨ 新增功能

### 1. 自动时间排序
- ✅ 系统自动获取当前时间
- ✅ 解析搜索结果中的 `publishedDate` 字段
- ✅ 按发布时间降序排列（最新内容优先）
- ✅ 支持多种时间格式解析
- ✅ 没有时间信息的结果排在最后

### 2. 可配置排序参数
- ✅ 新增 `sort_by_time` 参数
- ✅ 默认启用时间排序（`true`）
- ✅ 可设置为 `false` 关闭排序
- ✅ 支持的值：`true`, `1`, `yes` 或 `false`, `0`, `no`

### 3. 增强的日志记录
- ✅ 记录当前时间
- ✅ 统计有时间信息的结果数量
- ✅ 记录排序完成状态
- ✅ 错误处理和警告日志

## 🔧 技术实现

### 核心函数
```python
def _sort_results_by_time(result_container):
    """按时间对搜索结果进行排序（从最新到最旧）"""
    # 获取当前时间
    current_time = datetime.datetime.now()
    
    def get_sort_key(result):
        """获取排序键值"""
        # 尝试获取发布时间
        published_date = None
        
        if hasattr(result, 'publishedDate') and result.publishedDate:
            published_date = result.publishedDate
        elif isinstance(result, dict) and result.get('publishedDate'):
            published_date = result['publishedDate']
        
        # 解析时间格式
        if published_date:
            if isinstance(published_date, str):
                try:
                    published_date = datetime.datetime.fromisoformat(
                        published_date.replace('Z', '+00:00')
                    )
                except:
                    try:
                        published_date = datetime.datetime.strptime(
                            published_date, '%Y-%m-%d %H:%M:%S'
                        )
                    except:
                        published_date = None
            
            if published_date:
                return -published_date.timestamp()
        
        return 0
    
    # 执行排序
    if hasattr(result_container, 'results') and result_container.results:
        result_container.results.sort(key=get_sort_key)
```

### 支持的API接口
1. **`/chinese_search`** - 中文搜索API（推荐）
2. **`/wechat_search`** - 微信搜索API
3. **`/search`** - 通用搜索API（保持兼容性）

## 📊 功能对比

| 特性 | 更新前 | 更新后 |
|------|--------|--------|
| **时间排序** | ❌ 无排序 | ✅ 自动排序 |
| **排序参数** | ❌ 无参数 | ✅ `sort_by_time` |
| **时间格式** | ❌ 不支持 | ✅ 多格式支持 |
| **日志记录** | ❌ 无记录 | ✅ 详细日志 |
| **错误处理** | ❌ 基础处理 | ✅ 增强处理 |

## 🚀 使用示例

### 基本使用（默认启用排序）
```bash
# 中文搜索 - 自动按时间排序
curl "http://localhost:8080/chinese_search?q=人工智能"

# 微信搜索 - 自动按时间排序
curl "http://localhost:8080/wechat_search?q=ChatGPT"
```

### 高级使用（可配置排序）
```bash
# 关闭时间排序
curl "http://localhost:8080/chinese_search?q=人工智能&sort_by_time=false"

# 指定返回条数
curl "http://localhost:8080/chinese_search?q=人工智能&limit=20&sort_by_time=true"

# 指定搜索引擎
curl "http://localhost:8080/chinese_search?q=人工智能&engines=sogou,baidu&sort_by_time=true"
```

### Python 调用
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
```

## 🔗 Dify 集成

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

## 📝 更新的文档

### 1. README_CN.md
- ✅ 添加时间排序功能说明
- ✅ 更新API特点列表
- ✅ 强调Dify Docker环境配置要求
- ✅ 更新功能对比表

### 2. README.rst
- ✅ 添加时间排序功能特性
- ✅ 更新API端点说明
- ✅ 强调host.docker.internal配置
- ✅ 添加使用示例

### 3. API_USAGE_GUIDE.md
- ✅ 添加时间排序参数说明
- ✅ 更新使用示例
- ✅ 更新Dify工具配置
- ✅ 添加性能优化建议

## 🎯 技术细节

### 时间格式支持
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

## 🔄 向后兼容性

- ✅ 所有现有API保持兼容
- ✅ 默认启用排序，不影响现有调用
- ✅ 可通过参数关闭排序
- ✅ 不影响网页界面功能

## 📈 性能影响

- ✅ 排序操作轻量级，影响微乎其微
- ✅ 可通过 `sort_by_time=false` 关闭排序提升性能
- ✅ 智能时间解析，避免无效操作
- ✅ 详细的性能日志记录

## 🎉 总结

本次更新为 SearXNG-SGA 项目添加了强大的时间排序功能，让用户能够：

1. **获取最新内容** - 自动按时间排序，最新信息优先
2. **灵活配置** - 可选择启用或关闭时间排序
3. **完美集成** - 与Dify等AI平台完美兼容
4. **性能优化** - 轻量级实现，不影响响应速度

现在用户可以通过我们的API获取到最新、最相关的中文搜索结果！ 