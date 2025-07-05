.. SPDX-License-Identifier: AGPL-3.0-or-later

.. figure:: https://raw.githubusercontent.com/searxng/searxng/master/client/simple/src/brand/searxng.svg
   :target: https://docs.searxng.org/
   :alt: SearXNG
   :width: 100%
   :align: center

.. image:: https://img.shields.io/badge/SearXNG--SGA-Enhanced%20Version-blue?style=for-the-badge&logo=github
   :target: https://github.com/searxng/searxng
   :alt: SearXNG-SGA

.. image:: https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python
   :target: https://www.python.org/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker
   :target: #docker-deployment
   :alt: Docker Ready

.. image:: https://img.shields.io/badge/Windows-Compatible-green?style=for-the-badge&logo=windows
   :target: #windows-compatibility
   :alt: Windows Compatible

.. image:: https://img.shields.io/badge/Dify-Integration-orange?style=for-the-badge&logo=openai
   :target: #dify-integration
   :alt: Dify Integration

.. image:: https://img.shields.io/badge/WeChat-Search-red?style=for-the-badge&logo=wechat
   :target: #wechat-search-api
   :alt: WeChat Search

.. image:: https://img.shields.io/badge/License-AGPL%203.0-green?style=for-the-badge
   :target: https://github.com/searxng/searxng/blob/master/LICENSE
   :alt: AGPL 3.0 License

----

**SearXNG-SGA** 是基于 SearXNG 的增强版本，专为 AI 平台集成和微信公众号搜索而优化。

Privacy-respecting, hackable `metasearch engine`_ with enhanced AI integration capabilities.

.. _metasearch engine: https://en.wikipedia.org/wiki/Metasearch_engine

|SearXNG install| |SearXNG homepage| |SearXNG wiki| |AGPL License| |Issues| |commits| |weblate| |SearXNG logo|

----

.. _searx.space: https://searx.space
.. _user: https://docs.searxng.org/user
.. _admin: https://docs.searxng.org/admin
.. _developer: https://docs.searxng.org/dev
.. _homepage: https://docs.searxng.org/

.. |SearXNG logo| image:: https://raw.githubusercontent.com/searxng/searxng/master/client/simple/src/brand/searxng-wordmark.svg
   :target: https://docs.searxng.org/
   :width: 5%

.. |SearXNG install| image:: https://img.shields.io/badge/-install-blue
   :target: https://docs.searxng.org/admin/installation.html

.. |SearXNG homepage| image:: https://img.shields.io/badge/-homepage-blue
   :target: https://docs.searxng.org/

.. |SearXNG wiki| image:: https://img.shields.io/badge/-wiki-blue
   :target: https://github.com/searxng/searxng/wiki

.. |AGPL License|  image:: https://img.shields.io/badge/license-AGPL-blue.svg
   :target: https://github.com/searxng/searxng/blob/master/LICENSE

.. |Issues| image:: https://img.shields.io/github/issues/searxng/searxng?color=yellow&label=issues
   :target: https://github.com/searxng/searxng/issues

.. |commits| image:: https://img.shields.io/github/commit-activity/y/searxng/searxng?color=yellow&label=commits
   :target: https://github.com/searxng/searxng/commits/master

.. |weblate| image:: https://translate.codeberg.org/widgets/searxng/-/searxng/svg-badge.svg
   :target: https://translate.codeberg.org/projects/searxng/


✨ Enhanced Features
====================

SearXNG-SGA 在原有 SearXNG 基础上增加了以下特色功能：

🤖 **Dify AI Platform Integration**
   - 原生 JSON API 支持，完美集成 Dify AI 开发平台
   - 优化的响应格式，适配 AI 应用开发需求
   - 详细的集成文档和示例代码

📱 **WeChat Specialized Search API**
   - 专用微信公众号文章搜索 API
   - 支持多引擎备份（主引擎 + 搜狗微信搜索）
   - 优化的中文搜索体验

⏰ **Time-based Sorting**
   - 自动按发布时间排序（最新内容优先）
   - 支持多种时间格式解析
   - 可配置的排序参数
   - 智能时间解析和错误处理
   - 详细的排序日志记录

**时间排序功能特点：**
  - 🕐 自动获取当前时间
  - 📅 解析搜索结果中的 `publishedDate` 字段
  - 🔄 按发布时间降序排列（最新在前）
  - 📊 支持多种时间格式：ISO 8601、标准格式等
  - ⚙️ 可通过 `sort_by_time=false` 关闭排序
  - 📈 轻量级实现，不影响响应速度
  - 🔍 智能时间解析，避免无效操作

🖥️ **Windows Platform Compatibility**
   - 完整的 Windows 平台支持
   - 解决 pwd、uvloop、multiprocessing 等兼容性问题
   - 提供多种启动方式（脚本、Docker、手动）

🐳 **Docker Deployment Ready**
   - 优化的 Docker 配置
   - 支持 ARM64 和 ARM/v7 架构
   - 一键部署脚本

📚 **Comprehensive Documentation**
   - Windows 兼容性指南
   - Docker 部署指南
   - Dify 集成指南
   - API 使用说明


🚀 Quick Start
==============

**1. 快速启动（推荐）**

.. code-block:: bash

   # 使用简化启动脚本
   python start_searxng_simple.py

**2. 标准启动**

.. code-block:: bash

   # 设置环境变量并启动
   $env:PYTHONPATH="$PWD"; python -m searx.webapp

**3. Docker 启动**

.. code-block:: bash

   # 使用 Docker 部署
   docker-compose up -d

**4. 测试 API**

.. code-block:: bash

   # 测试通用搜索 API
   curl "http://localhost:8888/search?q=artificial%20intelligence&format=json"

   # 测试微信搜索 API
   curl "http://localhost:8888/wechat_search?q=ChatGPT"

   # 测试中文搜索 API（推荐）
   curl "http://localhost:8888/chinese_search?q=人工智能&limit=10"

**5. Python 调用示例**

.. code-block:: python

   import requests

   # 中文搜索 - 默认按时间排序
   response = requests.get('http://localhost:8888/chinese_search', {
       'q': '人工智能',
       'limit': 10,
       'engines': 'sogou,baidu'
   })
   data = response.json()

   # 中文搜索 - 关闭时间排序
   response = requests.get('http://localhost:8888/chinese_search', {
       'q': '人工智能',
       'limit': 10,
       'engines': 'sogou,baidu',
       'sort_by_time': False
   })
   data = response.json()

   # 微信搜索 - 默认按时间排序
   wechat_response = requests.get('http://localhost:8888/wechat_search', {
       'q': 'ChatGPT',
       'limit': 8
   })
   wechat_data = wechat_response.json()

   # 微信搜索 - 关闭时间排序
   wechat_response = requests.get('http://localhost:8888/wechat_search', {
       'q': 'ChatGPT',
       'limit': 8,
       'sort_by_time': False
   })
   wechat_data = wechat_response.json()


🔧 API Endpoints
================

**Chinese Search API (Recommended)**
-----------------------------------

.. code-block:: bash

   # JSON format with time sorting (default)
   curl "http://localhost:8888/chinese_search?q=artificial%20intelligence&limit=10"

   # Disable time sorting
   curl "http://localhost:8888/chinese_search?q=artificial%20intelligence&sort_by_time=false"

   # Specify engines and enable time sorting
   curl "http://localhost:8888/chinese_search?q=artificial%20intelligence&engines=sogou,baidu&sort_by_time=true"

   # Response format with time-based sorting
   {
     "query": "artificial intelligence",
     "results": [
       {
         "title": "Latest AI News",
         "url": "https://example.com/latest",
         "content": "Latest artificial intelligence developments...",
         "publishedDate": "2024-01-15T10:30:00Z",
         "engine": "sogou"
       },
       {
         "title": "AI Technology Trends",
         "url": "https://example.com/trends",
         "content": "Current trends in artificial intelligence...",
         "publishedDate": "2024-01-12T14:20:00Z",
         "engine": "baidu"
       }
     ],
     "suggestions": [...],
     "infoboxes": [...]
   }

**WeChat Specialized Search API**
--------------------------------

.. code-block:: bash

   # Dedicated WeChat search with time sorting (default)
   curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=8"

   # Disable time sorting for WeChat search
   curl "http://localhost:8888/wechat_search?q=ChatGPT&sort_by_time=false"

   # Get more WeChat articles with time sorting
   curl "http://localhost:8888/wechat_search?q=ChatGPT&limit=15&sort_by_time=true"

   # Specialized response for WeChat articles
   {
     "query": "ChatGPT",
     "wechat_results": [
       {
         "title": "WeChat Article Title",
         "content": "Article summary...",
         "url": "https://wechat.com/article",
         "publishedDate": "2024-01-12T14:20:00Z",
         "engine": "wechat"
       }
     ],
     "total_results": 10
   }

**General Search API (Legacy)**
-------------------------------

.. code-block:: bash

   # JSON format for Dify integration
   curl "http://localhost:8888/search?q=artificial%20intelligence&format=json"

   # Response format optimized for AI platforms
   {
     "query": "artificial intelligence",
     "results": [...],
     "suggestions": [...],
     "infoboxes": [...]
   }

**Time-based Sorting Features:**
  - ✅ Automatic sorting by publication date (newest first)
  - ✅ Support for multiple time formats (ISO 8601, standard format)
  - ✅ Configurable sorting parameter (`sort_by_time`)
  - ✅ Fallback for results without time information
  - ✅ Enhanced logging and error handling

**Time Sorting Parameters:**
  - ``sort_by_time=true`` (default): Enable time-based sorting
  - ``sort_by_time=false``: Disable time sorting (use relevance sorting)
  - Supported values: ``true``, ``1``, ``yes`` or ``false``, ``0``, ``no``

**Supported Time Formats:**
  - ISO 8601: ``2024-01-15T10:30:00Z``
  - Standard format: ``2024-01-15 10:30:00``
  - Automatic parsing of multiple formats

**Supported Output Formats:**
  - ``html`` (默认网页界面)
  - ``json`` (API 集成专用)

**WeChat Search Engines:**
  - 主微信搜索引擎
  - 搜狗微信搜索（备用）


⏰ Time-based Sorting Feature
=============================

**Overview**
SearXNG-SGA includes a powerful time-based sorting feature that automatically sorts search results by publication date, ensuring users always get the latest information.

**Technical Implementation**
- **Automatic Time Detection**: System automatically gets current time as reference
- **Smart Time Parsing**: Supports automatic parsing of multiple time formats
- **Descending Sort**: Results sorted by publication date (newest first)
- **Error Handling**: Results without time information are placed at the end
- **Performance Optimization**: Lightweight implementation with minimal impact

**Supported Time Formats**
- **ISO 8601 Format**: ``2024-01-15T10:30:00Z``
- **Standard Format**: ``2024-01-15 10:30:00``
- **Auto Parsing**: System automatically tries multiple time formats

**Parameter Configuration**
- **``sort_by_time=true``** (default): Enable time-based sorting
- **``sort_by_time=false``**: Disable time sorting, use relevance sorting
- **Supported Values**: ``true``, ``1``, ``yes`` or ``false``, ``0``, ``no``

**Performance Characteristics**
- ✅ Lightweight sorting algorithm with minimal impact
- ✅ Smart time parsing to avoid invalid operations
- ✅ Can be disabled via parameter to improve performance
- ✅ Detailed performance logging

**Use Cases**
1. **News Search**: Get latest news and information
2. **Technical Documentation**: Get latest technical docs and tutorials
3. **WeChat Articles**: Get latest WeChat public account articles
4. **Academic Papers**: Get latest research results

**Logging Information**
The system logs the following information:
- Current time
- Sorting start and completion status
- Number of results with time information
- Errors and warnings during sorting process

🖥️ Windows Compatibility
=========================

SearXNG-SGA 完全兼容 Windows 平台，解决了以下兼容性问题：

✅ **已解决的问题:**
  - pwd 模块缺失（Windows 不支持）
  - uvloop 不支持（Windows 限制）
  - multiprocessing fork 问题（Windows 不支持）
  - 路径分隔符兼容性
  - 环境变量设置

✅ **提供的解决方案:**
  - 条件导入和平台检测
  - 替代模块和兼容性包装
  - Windows 专用启动脚本
  - PowerShell 和批处理脚本

📖 详细指南请参考：`WINDOWS_COMPATIBILITY_GUIDE.md`_


🐳 Docker Deployment
====================

**快速部署:**

.. code-block:: bash

   # 克隆项目
   git clone https://github.com/your-repo/searxng-sga.git
   cd searxng-sga

   # 使用 Docker Compose 启动
   docker-compose up -d

   # 或使用 Docker 命令
   docker build -t searxng-sga .
   docker run -d -p 8888:8888 searxng-sga

**支持的架构:**
  - x86_64
  - ARM64
  - ARM/v7

📖 详细指南请参考：`DOCKER_DEPLOYMENT_GUIDE.md`_


🤖 Dify Integration
===================

**⚠️ 重要提醒：Dify 平台内置的 SearXNG 插件与本项目 API 不兼容！**

请使用 Dify 工作流中的 **HTTP 请求节点** 调用我们的专用 API。

**🚨 关键配置要求：**
在 Dify Docker 环境中，必须使用 `host.docker.internal` 地址！

- ❌ 错误：`http://localhost:8888/chinese_search`
- ✅ 正确：`http://host.docker.internal:8888/chinese_search`

这是因为 Dify 运行在 Docker 容器内，无法直接访问宿主机的 localhost。

**推荐集成方案：**

1. **中文搜索工具（推荐）**
   - API 端点：`/chinese_search`
   - 特点：锁定优质中文搜索引擎，自动时间排序
   - 支持引擎：sogou, baidu, 360search, wechat

2. **微信专搜工具**
   - API 端点：`/wechat_search`
   - 特点：专门搜索微信公众号内容，自动时间排序

**Dify 工作流配置示例：**

.. code-block:: json

   {
     "name": "chinese_search",
     "description": "中文搜索工具，使用优质中文搜索引擎，自动按时间排序",
     "method": "GET",
     "url": "http://host.docker.internal:8888/chinese_search",
     "parameters": {
       "q": "{{query}}",
       "limit": "{{limit|default:10}}",
       "engines": "{{engines|default:sogou,baidu,360search,wechat}}",
       "sort_by_time": "{{sort_by_time|default:true}}"
     },
     "headers": {
       "Content-Type": "application/json"
     }
   }

**详细集成指南：**
  - `📖 Dify 集成指南 <DIFY_WORKFLOW_GUIDE.md>`_
  - `📱 API 使用说明 <API_USAGE_GUIDE.md>`_

📱 WeChat Search API
====================

专用微信公众号搜索功能：

**API 端点:**
  - 主端点：`/wechat_search`
  - 格式：JSON only
  - 引擎：微信 + 搜狗微信

**使用示例:**

.. code-block:: bash

   # 搜索微信公众号文章
   curl "http://localhost:8888/wechat_search?q=人工智能&format=json"

   # 带参数的搜索
   curl "http://localhost:8888/wechat_search?q=ChatGPT&pageno=1&format=json"

**响应格式:**

.. code-block:: json

   {
     "query": "人工智能",
     "wechat_results": [
       {
         "title": "文章标题",
         "content": "文章摘要",
         "url": "文章链接",
         "author": "公众号名称",
         "publish_time": "发布时间"
       }
     ],
     "total_results": 10,
     "pageno": 1
   }


⚙️ Configuration
=================

**JSON API 支持配置:**

.. code-block:: yaml

   # searx/settings.yml
   search:
     formats:
       - html
       - json
     default_format: html

**启用的微信搜索引擎:**

.. code-block:: yaml

   engines:
     - name: wechat
       engine: wechat
       disabled: false
       timeout: 10.0

     - name: sogou wechat  
       engine: sogou_wechat
       disabled: false
       timeout: 10.0

**性能优化配置:**

.. code-block:: yaml

   # 禁用的搜索引擎（性能优化）
   disabled_engines:
     - quark
     - seznam
     - wolframalpha
     - crowdview
     - mojeek
     - mwmbl
     - naver
     - bing_images
     - bing_news
     - bing_videos
     - bpb


📚 Documentation
================

完整的文档体系：

- `📖 Windows 兼容性指南 <WINDOWS_COMPATIBILITY_GUIDE.md>`_
- `🐳 Docker 部署指南 <DOCKER_DEPLOYMENT_GUIDE.md>`_
- `🤖 Dify 集成指南 <DIFY_INTEGRATION_GUIDE.md>`_
- `📱 API 使用说明 <API_USAGE.md>`_
- `🚀 开源项目指南 <OPEN_SOURCE_GUIDE.md>`_
- `📋 Git 部署指南 <GIT_DEPLOYMENT_GUIDE.md>`_


🔗 Community & Support
======================

**社区交流:**

IRC
  `#searxng on libera.chat <https://web.libera.chat/?channel=#searxng>`_
  (bridged to Matrix)

Matrix
  `#searxng:matrix.org <https://matrix.to/#/#searxng:matrix.org>`_

**问题反馈:**
  - GitHub Issues: `报告问题 <https://github.com/searxng/searxng/issues>`_
  - 功能建议: `功能请求 <https://github.com/searxng/searxng/issues>`_


🌐 Translations
===============

.. _Weblate: https://translate.codeberg.org/projects/searxng/searxng/

Help translate SearXNG at `Weblate`_

.. figure:: https://translate.codeberg.org/widgets/searxng/-/multi-auto.svg
   :target: https://translate.codeberg.org/projects/searxng/


🤝 Contributing
===============

我们欢迎所有形式的贡献！

**开发者指南:**
  - `开发快速入门 <https://docs.searxng.org/dev/quickstart.html>`_
  - `开发者文档 <https://docs.searxng.org/dev/index.html>`_

**贡献方式:**
  - 🐛 报告 Bug
  - 💡 提出功能建议
  - 📝 改进文档
  - 🔧 提交代码
  - 🌍 翻译本地化

**开发环境设置:**

.. code-block:: bash

   # 克隆项目
   git clone https://github.com/your-repo/searxng-sga.git
   cd searxng-sga

   # 安装依赖
   pip install -r requirements.txt

   # 启动开发服务器
   python start_searxng_simple.py


💻 GitHub Codespaces
====================

You can contribute from your browser using `GitHub Codespaces`_:

- Fork the repository
- Click on the ``<> Code`` green button
- Click on the ``Codespaces`` tab instead of ``Local``
- Click on ``Create codespace on master``
- VSCode is going to start in the browser
- Wait for ``git pull && make install`` to appear and then disappear
- You have `120 hours per month`_ (see also your `list of existing Codespaces`_)
- You can start SearXNG using ``make run`` in the terminal or by pressing ``Ctrl+Shift+B``

.. _GitHub Codespaces: https://docs.github.com/en/codespaces/overview
.. _120 hours per month: https://github.com/settings/billing
.. _list of existing Codespaces: https://github.com/codespaces


📄 License
==========

This project is licensed under the `AGPL-3.0 License <https://github.com/searxng/searxng/blob/master/LICENSE>`_.

----

**SearXNG-SGA** - Enhanced Privacy-Respecting Metasearch Engine with AI Integration

*Built with ❤️ for the open source community*
