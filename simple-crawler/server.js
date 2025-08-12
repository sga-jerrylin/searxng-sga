const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');
const https = require('https');
const http = require('http');
const { URL } = require('url');

// 添加更多HTTP客户端选项
const fetch = require('node-fetch');
const { HttpsProxyAgent } = require('https-proxy-agent');

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

// 获取HTML内容（完全按案例实现 - 模拟HuTool + JSoup备选）
async function getHtml(url, isWechatArticle = false) {
  console.log(`开始获取HTML: ${url}`);

  // 方法1：模拟HuTool HTTP请求（主要方法）
  try {
    console.log(`使用HuTool风格请求获取: ${url}`);

    const headers = {
      // 完全按照案例的请求头
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Connection': 'keep-alive',
      'Referer': isWechatArticle ? 'https://mp.weixin.qq.com/' : url,
      'Cookie': '', // 按案例设置空cookie
    };

    // 使用fetch模拟HuTool的行为
    const response = await fetch(url, {
      method: 'GET',
      headers,
      timeout: 30000,
      redirect: 'follow', // 启用重定向
      agent: new https.Agent({
        rejectUnauthorized: false
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const html = await response.text();

    if (!html || html.trim().length === 0) {
      throw new Error('HuTool风格请求获取的HTML为空');
    }

    console.log(`成功从 ${url} 获取HTML，长度: ${html.length}`);

    if (isWechatArticle) {
      // 针对微信文章进行特殊处理，尝试修复图片URL
      return fixWechatImages(html);
    }

    return html;

  } catch (hutoolError) {
    console.log(`HuTool风格请求失败: ${hutoolError.message}，尝试JSoup备选方案`);

    // 方法2：使用JSoup风格连接（备用方法）
    try {
      console.log(`尝试使用JSoup风格连接获取HTML`);

      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        },
        timeout: 30000,
        maxRedirects: 5,
        httpsAgent: new https.Agent({
          rejectUnauthorized: false
        })
      });

      const html = response.data;

      if (!html || html.trim().length === 0) {
        throw new Error('JSoup风格连接获取的HTML为空');
      }

      console.log(`JSoup风格连接成功获取HTML，长度: ${html.length}`);

      if (isWechatArticle) {
        return fixWechatImages(html);
      }

      return html;

    } catch (jsoupError) {
      console.error(`JSoup风格连接也失败: ${jsoupError.message}`);
      throw new Error(`所有方法都失败了: HuTool(${hutoolError.message}), JSoup(${jsoupError.message})`);
    }
  }
}



// 解析HTML并转换为Markdown（按案例实现）
function parseHtmlToMarkdown(html, url) {
  const $ = cheerio.load(html);
  
  // 移除不需要的元素
  $('script, style, iframe, nav, footer, header, .adsbygoogle, .advertisement, #sidebar, .sidebar, .nav, .menu, .comment').remove();
  
  // 获取标题
  const title = $('title').text() || '';
  
  // 尝试获取主要内容
  let mainContent = '';
  
  // 尝试常见的内容容器
  const contentSelectors = [
    'article',
    '.content, .main, #content, #main, .post, .entry',
    'main',
    '.article-content, .post-content',
    '.rich_media_content', // 微信文章
    '#js_content' // 微信文章
  ];
  
  for (const selector of contentSelectors) {
    const element = $(selector);
    if (element.length > 0) {
      const text = element.text().trim();
      if (text.length > mainContent.length) {
        mainContent = text;
      }
    }
  }
  
  // 如果内容太短，可能没有正确提取到，尝试获取body所有文本
  if (mainContent.length < 100) {
    mainContent = $('body').text().trim();
  }
  
  // 清理内容
  mainContent = mainContent.replace(/\s+/g, ' ').trim();
  
  // 组合结果为Markdown格式
  const markdown = `# ${title}\n\n${mainContent}`;
  
  return {
    title,
    content: mainContent,
    markdown,
    description: $('meta[name="description"]').attr('content') || ''
  };
}

// 修复微信图片（完全按案例实现）
function fixWechatImages(html) {
  const $ = cheerio.load(html);

  console.log('开始处理微信文章图片');

  // 处理微信特有的图片样式
  const wxImages = $('.rich_pages, .wxw-img, .rich_pages.wxw-img');
  console.log(`找到微信特殊图片: ${wxImages.length} 张`);
  wxImages.each((i, img) => {
    const dataSrc = $(img).attr('data-src');
    if (dataSrc) {
      console.log(`修复微信图片data-src: ${dataSrc}`);
      $(img).attr('src', dataSrc);
    }
  });

  // 处理所有section中的图片
  const sectionImages = $('section img');
  console.log(`找到section中的图片: ${sectionImages.length} 张`);
  sectionImages.each((i, img) => {
    const dataSrc = $(img).attr('data-src');
    if (dataSrc && (!$(img).attr('src') || $(img).attr('src').includes('data:'))) {
      console.log(`修复section中图片data-src: ${dataSrc}`);
      $(img).attr('src', dataSrc);
    }
  });

  // 处理懒加载图片
  const lazyImages = $('img[data-src]');
  console.log(`找到懒加载图片: ${lazyImages.length} 张`);
  lazyImages.each((i, img) => {
    const dataSrc = $(img).attr('data-src');
    if (dataSrc) {
      console.log(`修复懒加载图片data-src: ${dataSrc}`);
      $(img).attr('src', dataSrc);
    }
  });

  // 处理其他常见的微信图片属性
  const allImages = $('img');
  console.log(`找到所有图片: ${allImages.length} 张`);
  let fixedCount = 0;
  allImages.each((i, img) => {
    // 检查各种可能的属性
    const possibleAttrs = ['data-src', 'data-original', 'data-backupSrc', 'data-backsrc', 'data-imgfileid'];
    for (const attr of possibleAttrs) {
      const value = $(img).attr(attr);
      if (value && (!$(img).attr('src') || $(img).attr('src').includes('data:'))) {
        console.log(`通过属性${attr}修复图片: ${value}`);
        $(img).attr('src', value);
        fixedCount++;
        break;
      }
    }

    // 确保所有图片都有alt属性，即使为空
    if (!$(img).attr('alt')) {
      $(img).attr('alt', '');
    }
  });
  console.log(`修复了 ${fixedCount} 张图片的URL`);

  // 特别检查目标图片是否存在并正确处理
  const targetImage = $('img[src*=fFKE45D7xmicHicSr92dA3YoaeO9IAyleH]');
  if (targetImage.length > 0) {
    console.log(`找到目标图片: ${targetImage.attr('src')}`);
  } else {
    console.log('未找到目标图片');
    // 尝试在data-src中查找
    const dataTargetImage = $('img[data-src*=fFKE45D7xmicHicSr92dA3YoaeO9IAyleH]');
    if (dataTargetImage.length > 0) {
      console.log(`在data-src中找到目标图片: ${dataTargetImage.attr('data-src')}`);
      dataTargetImage.attr('src', dataTargetImage.attr('data-src'));
    }
  }

  // 有些微信图片URL可能带有转义字符，修正它们
  let html2 = $.html().replace(/&amp;/g, '&');

  console.log('已修复微信文章中的图片URL');
  return html2;
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
    console.error('API错误:', error);
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
    service: 'simple-crawler'
  });
});

app.listen(port, () => {
  console.log(`简单爬虫服务启动，端口: ${port}`);
});
