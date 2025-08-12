const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');
const https = require('https');

const app = express();
const port = 3002;

app.use(cors());
app.use(express.json());

// 完全基于案例的爬取函数
async function scrapeUrl(url) {
  try {
    console.log(`开始爬取: ${url}`);

    // 检查是否是微信文章
    const isWechatArticle = url.includes('mp.weixin.qq.com');

    let html = await getHtml(url, isWechatArticle);

    if (!html || html.trim().length === 0) {
      throw new Error('获取的HTML为空');
    }

    console.log(`获取HTML成功，长度: ${html.length}`);

    // 如果是微信文章，修复图片
    if (isWechatArticle) {
      html = fixWechatImages(html);
    }

    // 解析HTML并转换为Markdown
    const result = parseHtmlToMarkdown(html, url);

    console.log(`爬取成功: ${result.title}`);

    return {
      success: true,
      data: {
        title: result.title,
        content: result.markdown,
        markdown: result.markdown,
        html: result.content,
        metadata: {
          title: result.title,
          description: result.description || '',
          language: 'zh'
        },
        url
      }
    };

  } catch (error) {
    console.error(`爬取失败: ${error.message}`);
    throw error;
  }
}

// 获取HTML内容（完全按案例实现）
async function getHtml(url, isWechatArticle = false) {
  // 方法1：使用axios（主要方法）
  try {
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Connection': 'keep-alive',
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Sec-Fetch-User': '?1',
      'Upgrade-Insecure-Requests': '1'
    };

    if (isWechatArticle) {
      headers['Referer'] = 'https://mp.weixin.qq.com/';
    } else {
      headers['Referer'] = url;
    }

    console.log(`使用axios获取: ${url}`);

    const response = await axios.get(url, {
      headers,
      timeout: 30000,
      maxRedirects: 5,
      validateStatus: function (status) {
        return status >= 200 && status < 400;
      },
      httpsAgent: new https.Agent({
        rejectUnauthorized: false
      })
    });

    const html = response.data;

    if (!html || html.trim().length === 0) {
      throw new Error('axios获取的HTML为空');
    }

    console.log(`axios成功获取HTML，长度: ${html.length}`);
    return html;

  } catch (axiosError) {
    console.log(`axios获取失败: ${axiosError.message}，尝试备用方法`);

    // 方法2：使用Node.js原生https模块（备用方法）
    try {
      console.log(`使用原生https获取: ${url}`);

      const html = await getHtmlWithNativeHttps(url, isWechatArticle);

      if (!html || html.trim().length === 0) {
        throw new Error('原生https获取的HTML为空');
      }

      console.log(`原生https成功获取HTML，长度: ${html.length}`);
      return html;

    } catch (nativeError) {
      console.error(`原生https也失败: ${nativeError.message}`);
      throw new Error(`所有方法都失败了: axios(${axiosError.message}), native(${nativeError.message})`);
    }
  }
}

    
    if (!html || html.trim().length === 0) {
      throw new Error('获取的HTML为空');
    }
    
    console.log(`获取HTML成功，长度: ${html.length}`);
    
    // 如果是微信文章，修复图片
    if (isWechatArticle) {
      html = fixWechatImages(html);
    }
    
    // 解析HTML
    const $ = cheerio.load(html);
    
    // 移除不需要的元素
    $('script, style, nav, footer, header, aside').remove();
    
    // 获取标题
    const title = $('title').text() || '';
    
    // 获取主要内容
    let content = '';
    
    // 尝试常见的内容选择器
    const contentSelectors = [
      'article',
      '.article-content',
      '.post-content',
      '.content',
      'main',
      '.main-content',
      '#content'
    ];
    
    for (const selector of contentSelectors) {
      const element = $(selector);
      if (element.length && element.text().trim().length > 100) {
        content = element.html();
        break;
      }
    }
    
    // 如果没找到主要内容，使用body
    if (!content) {
      content = $('body').html() || '';
    }
    
    // 转换为文本
    const textContent = $(content).text().replace(/\s+/g, ' ').trim();
    
    // 简单的Markdown转换
    let markdown = `# ${title}\n\n${textContent}`;
    
    console.log(`爬取成功: ${title}`);
    
    return {
      success: true,
      data: {
        title,
        content: markdown,
        markdown,
        html: content,
        metadata: {
          title,
          description: $('meta[name="description"]').attr('content') || '',
          language: $('html').attr('lang') || 'zh'
        },
        url
      }
    };
    
  } catch (error) {
    console.error(`爬取失败: ${error.message}`);
    throw error;
  }
}

// 修复微信图片（简化版）
function fixWechatImages(html) {
  const $ = cheerio.load(html);
  
  $('img[data-src]').each((i, img) => {
    const dataSrc = $(img).attr('data-src');
    if (dataSrc) {
      $(img).attr('src', dataSrc);
    }
  });
  
  return $.html();
}

// API 路由
app.post('/v0/scrape', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({
        success: false,
        error: 'URL is required'
      });
    }
    
    const result = await scrapeUrl(url);
    res.json(result);
    
  } catch (error) {
    console.error('爬取错误:', error.message);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 健康检查
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    method: 'simple-crawler'
  });
});

// 启动服务器
app.listen(port, () => {
  console.log(`简单爬虫服务启动，端口: ${port}`);
});

process.on('SIGTERM', () => {
  console.log('收到关闭信号');
  process.exit(0);
});
