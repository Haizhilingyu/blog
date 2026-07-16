# 海之领域博客 — Agent 写作指南

> 本文件由 Hermes Agent 自动加载。任何在此仓库中工作的 Agent 必须遵循以下规范。

## 仓库说明

这是「海之领域」（xiweihai.site）个人博客的源码仓库。纯 HTML+CSS，零框架。
作者：建平儿（GitHub: Haizhilingyu）。技术笔记 + 生活随笔。

## 写作风格

- **语言**：中文，口语化但不随意。像跟同事聊天，不是写文档。
- **真实性**：内容必须基于作者真实经历。不编造技术细节和生活故事。
- **长度**：每篇 800-1500 字。宁可短而有料，不要长而空洞。
- **语气**：技术文章讲清楚"为什么这么做"；随笔有真实的自我反思。
- **标题**：简洁有信息量，不要标题党。例："NAS 自托管完全指南"而非"你绝对想不到 NAS 还能这样玩"。
- **标签**：`tech`（技术）或 `life`（随笔），必选其一。

## 文章 HTML 模板

**每篇文章必须使用以下模板**，保持全站视觉一致性。CSS 已内联，无需额外引入。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{文章标题} · 海之领域</title>
<style>
<!-- 见 templates/article-template.html，包含完整的内联 CSS -->
</style>
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="logo">海之领域</a>
<nav class="nav"><a href="/">文章</a><a href="/about.html">关于</a></nav>
</div></header>
<main class="container"><article class="post-body">
<div class="post-meta"><time>{YYYY-MM-DD}</time><span class="tag {tech|life}">{技术|随笔}</span></div>
<h1>{文章标题}</h1>

<!-- 正文内容 -->
<p>正文段落...</p>

<h2>二级标题</h2>
<p>...</p>

<blockquote>引用文字</blockquote>

<pre><code>代码块</code></pre>

<ul>
<li>列表项</li>
</ul>

<a href="/" class="back-link">← 返回首页</a>
</article></main>
<footer class="site-footer"><div class="container">
<p>© 2026 海之领域</p><p class="footer-sub">xiweihai.site</p>
</div></footer>
</body></html>
```

**完整 CSS 模板见 `templates/article-template.html`，写新文章时复制该文件、替换正文内容即可。**

## 发布流程（两步）

### 第 1 步：创建文章文件

把写好的 HTML 文件放到 `posts/` 目录，文件名用英文短横线命名（如 `my-new-post.html`）。

### 第 2 步：注册到 manifest + 部署

在 `posts/manifest.json` **顶部**（数组第一个元素）加一条：

```json
{
  "date": "2026-07-16",
  "tag": "tech",
  "title": "文章标题",
  "file": "my-new-post.html",
  "summary": "首页列表中显示的摘要，一两句话，不要超过100字。"
}
```

然后运行部署：

```bash
# 在服务器上（SSH: ssh root@xiweihai.site）
cd /var/www/blog
python3 publish.py
```

脚本自动处理：
- ✅ 首页展示最新 10 篇，超出自动分页
- ✅ RSS 订阅自动更新（含所有文章）
- ✅ 分页增减（文章减少时自动删除多余 page-N.html）

### 第 3 步：验证

```bash
# 验证文章可访问
curl -sI https://xiweihai.site/posts/my-new-post.html | head -1
# 验证首页更新
curl -s https://xiweihai.site/ | grep "文章标题"
# 验证 RSS
curl -s https://xiweihai.site/feed.xml | grep "文章标题"
```

三个检查都返回结果 = 发布成功。

## 常见错误

1. **忘记在 manifest.json 注册** → 文章文件存在但首页不显示、RSS 不收录
2. **manifest.json 日期格式错误** → 必须是 `YYYY-MM-DD`，否则排序错乱
3. **tag 值写错** → 只能是 `tech` 或 `life`（小写），写成 `技术` 或 `Tech` 会样式失效
4. **文章 HTML 没用模板** → 样式和全站不一致，必须从 `templates/article-template.html` 复制
5. **summary 含双引号** → JSON 解析失败，双引号用中文引号或转义
6. **跑 publish.py 前没传文章文件到服务器** → 首页有链接但点进去 404

## 服务器信息

- **SSH**: `root@xiweihai.site`（阿里云 ECS，8.137.16.20）
- **博客目录**: `/var/www/blog`
- **Web 服务器**: Caddy（自动 HTTPS）
- **域名**: `xiweihai.site`

## 文章索引格式

`posts/manifest.json` 是唯一数据源，字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 发布日期 `YYYY-MM-DD`，决定排序 |
| `tag` | string | `tech` 或 `life` |
| `title` | string | 文章标题（显示在首页卡片和 `<title>`） |
| `file` | string | `posts/` 目录下的文件名 |
| `summary` | string | 首页卡片摘要，一两句话 |


## AI 资讯模块

资讯页面独立于博客文章，由 VPS Hermes 每天自动采集生成。

### 文件说明

| 文件 | 作用 |
|------|------|
| `news_generator.py` | 扫描 `ai-news/*.json`，生成资讯首页（分页）+ 每日详情页 |
| `save_news.py` | 桥接脚本：接收采集 JSON → 保存快照 → 调用生成器 |
| `ai-news/YYYY-MM-DD.json` | 每日资讯数据快照（唯一数据源） |
| `ai-news/YYYY-MM-DD.html` | 每日资讯详情页（自动生成） |
| `ai-news.html` | 资讯首页，最新 10 天（自动生成） |

### 数据采集流程

```
VPS cron job (每天 23:00 UTC)
  ↓ daily_ai_search.py 搜索 X 推文
  ↓ Hermes 翻译英文推文为中文
  ↓ 保存 ai-news/YYYY-MM-DD.json
  ↓ news_generator.py 生成 HTML
  ↓ 资讯首页自动更新
```

### JSON 快照格式

```json
{
  "total_tweets": 15,
  "sections": [
    {
      "name": "全球AI热门",
      "tweets": [
        {
          "author": "Sam Altman",
          "username": "sama",
          "text": "原文内容",
          "cn_summary": "中文翻译摘要",
          "link": "https://x.com/...",
          "metrics_str": "❤️ 12000 | 🔁 3000"
        }
      ]
    }
  ]
}
```

### 资讯不加入 RSS

资讯页面独立于博客文章的 RSS feed，`feed.xml` 只包含手写文章。
