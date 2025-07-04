# SearXNG 微信搜索扩展部署指南

本项目基于 SearXNG 开源搜索引擎，扩展了微信公众号文章搜索功能。

## 功能特性

- ✅ 支持微信公众号文章搜索
- ✅ 基于 Docker 容器化部署
- ✅ 支持 JSON API 接口
- ✅ 可配置多种搜索引擎
- ✅ 数据隐私保护

## 快速开始

### 方法一：使用部署脚本（推荐）

1. **运行部署脚本**
   ```bash
   ./deploy.sh
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **访问服务**
   - 打开浏览器访问：http://localhost:8081
   - 使用 `!wx` 前缀搜索微信内容，例如：`!wx 人工智能`

### 方法二：手动部署

1. **创建目录结构**
   ```bash
   mkdir -p searx/engines
   ```

2. **复制配置文件**
   ```bash
   cp docker-settings.yml searx/settings.yml
   cp limiter.toml searx/limiter.toml
   cp searx/engines/wechat.py searx/engines/wechat.py
   ```

3. **修改配置**
   - 编辑 `searx/settings.yml`，将 `your-custom-secret-key-here` 替换为您的自定义密钥
   - 根据需要调整其他配置项

4. **启动服务**
   ```bash
   docker-compose up -d
   ```

## 文件说明

```
searxng-master/
├── docker-compose.yml          # Docker Compose 配置文件
├── docker-settings.yml         # SearXNG 配置模板
├── limiter.toml                # 限流器配置
├── deploy.sh                   # 一键部署脚本
├── searx/
│   ├── engines/
│   │   └── wechat.py           # 微信搜索引擎
│   ├── settings.yml            # SearXNG 主配置文件
│   └── limiter.toml            # 限流器配置
└── README-WeChat.md            # 本文件
```

## 使用说明

### 搜索方式

1. **常规搜索**：直接输入关键词，会同时搜索多个引擎
2. **微信专搜**：使用 `!wx` 前缀，例如：
   - `!wx 机器学习`
   - `!wx 区块链技术`
   - `!wx 投资理财`

### API 接口

SearXNG 支持 JSON API，可用于 AI 应用的联网搜索：

```bash
# 搜索请求
curl "http://localhost:8081/search?q=人工智能&format=json"

# 微信专搜
curl "http://localhost:8081/search?q=!wx%20人工智能&format=json"
```

## 配置说明

### 主要配置项

- **端口配置**：默认使用 8081 端口，可在 `docker-compose.yml` 中修改
- **搜索引擎**：在 `searx/settings.yml` 中配置启用/禁用的搜索引擎
- **超时设置**：微信搜索默认超时 6 秒，可根据网络情况调整
- **调试模式**：默认开启，生产环境建议关闭

### 自定义配置

1. **修改端口**
   ```yaml
   # docker-compose.yml
   ports:
     - 8082:8080  # 改为 8082 端口
   ```

2. **添加搜索引擎**
   ```yaml
   # searx/settings.yml
   engines:
     - name: 自定义引擎
       engine: 引擎名称
       disabled: false
   ```

3. **配置代理**（如需要）
   ```python
   # searx/engines/wechat.py
   # 取消注释并配置代理
   proxy = {
       'http': '127.0.0.1:7890',
       'https': '127.0.0.1:7890',
   }
   ```

## 常见问题

### Q: 微信搜索无结果或报错？
A: 可能是网络问题或被反爬虫限制，可以：
1. 检查网络连接
2. 配置代理（如果需要）
3. 查看容器日志：`docker-compose logs -f searxng`

### Q: 如何查看日志？
A: 执行 `docker-compose logs -f searxng` 查看实时日志

### Q: 如何停止服务？
A: 执行 `docker-compose down`

### Q: 如何更新配置？
A: 修改配置文件后，执行：
```bash
docker-compose down
docker-compose up -d
```

## 技术原理

微信搜索功能通过以下方式实现：

1. **搜索接口**：使用搜狗微信搜索 API
2. **结果解析**：通过 XPath 解析 HTML 结果
3. **URL 处理**：处理搜狗的重定向链接获取真实 URL
4. **反爬虫**：配置合适的 User-Agent 和 Cookie

## 参考资料

- [SearXNG 官方文档](https://docs.searxng.org/)
- [SearXNG GitHub](https://github.com/searxng/searxng)
- [微信搜索实现参考](https://github.com/ava131/Searxng-with-WeChat)

## 许可证

本项目遵循 SearXNG 的开源许可证。 