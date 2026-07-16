#!/usr/bin/env python3
"""
AI 资讯 HTML 生成器
用法：
  python3 news_generator.py                          # 扫描所有JSON，重新生成全部页面
  python3 news_generator.py /path/to/today.json      # 只处理指定JSON（增量）

数据源：ai-news/ 目录下的 JSON 文件（由 daily_ai_search.py 输出）
输出：
  ai-news.html          资讯首页（最新10天，分页）
  ai-news/YYYY-MM-DD.html  每日资讯详情页
  page-N.html (在ai-news目录下)  分页
"""
import json, os, sys, datetime, glob

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(BLOG_DIR, "ai-news")
PER_PAGE = 10

CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--c-bg:#fafaf7;--c-text:#2c2c2c;--c-text-light:#6a6a6a;--c-accent:#2d6a4f;--c-border:#e8e6e0;--c-tag-tech:#1a73e8;--c-tag-life:#d4641e}
@media(prefers-color-scheme:dark){:root{--c-bg:#1a1a18;--c-text:#e0ddd8;--c-text-light:#9a9a9a;--c-accent:#52b788;--c-border:#333330}}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:var(--c-bg);color:var(--c-text);line-height:1.8;-webkit-font-smoothing:antialiased}
.container{max-width:680px;margin:0 auto;padding:0 20px}
.site-header{padding:24px 0;border-bottom:1px solid var(--c-border);position:sticky;top:0;background:var(--c-bg);z-index:100}
.site-header .container{display:flex;justify-content:space-between;align-items:center}
.logo{font-size:1.25rem;font-weight:700;color:var(--c-text);text-decoration:none;letter-spacing:.05em}
.nav{display:flex;gap:24px}
.nav a{color:var(--c-text-light);text-decoration:none;font-size:.9rem;transition:color .2s}
.nav a:hover{color:var(--c-accent)}
.hero{padding:64px 0 48px;text-align:center}
.hero h1{font-size:1.75rem;font-weight:700;line-height:1.5;margin-bottom:12px}
.hero-sub{color:var(--c-text-light);font-size:1rem}
.posts{padding-bottom:48px}
.post-card{padding:28px 0;border-bottom:1px solid var(--c-border)}
.post-card:last-child{border-bottom:none}
.post-meta{display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:.8rem;color:var(--c-text-light)}
.tag{padding:2px 10px;border-radius:20px;font-size:.75rem;font-weight:500;background:var(--c-border);color:var(--c-text-light)}
.tag.news{background:rgba(45,106,79,.12);color:var(--c-accent)}
.post-card h2{font-size:1.25rem;line-height:1.4;margin-bottom:8px}
.post-card h2 a{color:var(--c-text);text-decoration:none;transition:color .2s}
.post-card h2 a:hover{color:var(--c-accent)}
.post-card p{color:var(--c-text-light);font-size:.95rem;line-height:1.7}
.pagination{display:flex;justify-content:center;gap:8px;padding:32px 0}
.pagination a,.pagination span{display:inline-block;min-width:36px;height:36px;line-height:36px;text-align:center;border-radius:12px;text-decoration:none;font-size:.9rem;color:var(--c-text-light)}
.pagination .current{background:var(--c-accent);color:#fff}
.pagination a:hover{background:var(--c-border)}
.post-body{padding:48px 0}
.post-body h1{font-size:1.75rem;margin-bottom:8px;line-height:1.4}
.post-body h2{font-size:1.3rem;margin:36px 0 12px;line-height:1.4}
.post-body h3{font-size:1.1rem;margin:28px 0 10px}
.post-body p{margin-bottom:16px;color:var(--c-text-light)}
.post-body ul{padding-left:20px;margin-bottom:16px}
.post-body li{margin-bottom:8px;color:var(--c-text-light)}
.post-body blockquote{border-left:3px solid var(--c-accent);padding-left:16px;margin:24px 0;color:var(--c-text-light);font-style:italic}
.post-body strong{color:var(--c-text);font-weight:600}
.news-item{padding:20px 0;border-bottom:1px solid var(--c-border)}
.news-item:last-child{border-bottom:none}
.news-item h3{font-size:1.05rem;margin:0 0 6px}
.news-item h3 a{color:var(--c-text);text-decoration:none}
.news-item h3 a:hover{color:var(--c-accent)}
.news-meta{font-size:.8rem;color:var(--c-text-light);margin-bottom:6px}
.news-summary{color:var(--c-text-light);font-size:.92rem}
.back-link{display:inline-block;margin-top:40px;color:var(--c-accent);text-decoration:none;font-size:.9rem}
.site-footer{padding:32px 0;border-top:1px solid var(--c-border);text-align:center}
.site-footer p{font-size:.85rem;color:var(--c-text-light)}
.footer-sub{margin-top:4px;font-size:.8rem;opacity:.6}
.site-footer a{color:var(--c-accent);text-decoration:none}
@media(max-width:640px){.hero{padding:40px 0 32px}.hero h1{font-size:1.4rem}.post-card{padding:20px 0}.post-card h2{font-size:1.1rem}.nav{gap:16px}}
"""

NAV = '<nav class="nav"><a href="/">文章</a><a href="/ai-news.html">资讯</a><a href="/about.html">关于</a><a href="/feed.xml">RSS</a></nav>'


def build_daily_page(date_str, data):
    """生成每日资讯详情页 HTML"""
    items_html = ""
    sections = data.get("sections", [])
    item_num = 0
    for section in sections:
        items_html += f'<h2>{section["name"]}</h2>\n'
        for tweet in section.get("tweets", []):
            item_num += 1
            author = tweet.get("author", "")
            username = tweet.get("username", "")
            text = tweet.get("text", "")[:500]
            link = tweet.get("link", "")
            # 中文翻译（如果Hermes已翻译）
            cn = tweet.get("cn_summary", tweet.get("translation", ""))
            metrics = tweet.get("metrics_str", "")

            # 标题：用作者名或前50字
            title = f'{author} (@{username})' if author else text[:50]
            summary = cn if cn else text

            items_html += f'<div class="news-item">\n'
            items_html += f'<div class="news-meta">{item_num}. {author} (@{username})'
            if metrics:
                items_html += f' · {metrics}'
            items_html += f'</div>\n'
            if cn:
                items_html += f'<p>{cn}</p>\n'
            items_html += f'<p class="news-summary">{text[:300]}</p>\n'
            if link:
                items_html += f'<p><a href="{link}" style="color:var(--c-accent);font-size:.85rem">查看原文 →</a></p>\n'
            items_html += f'</div>\n'

    total = data.get("total_tweets", item_num)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 资讯 · {date_str} · 海之领域</title>
<style>{CSS}</style>
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="logo">海之领域</a>
{NAV}
</div></header>
<main class="container"><article class="post-body">
<div class="post-meta"><time>{date_str}</time><span class="tag news">资讯</span></div>
<h1>AI 资讯速递 · {date_str}</h1>
<p>共 {total} 条</p>
{items_html}
<a href="/ai-news.html" class="back-link">← 资讯列表</a>
</article></main>
<footer class="site-footer"><div class="container">
<p>© 2026 海之领域</p><p class="footer-sub">xiweihai.site</p>
</div></footer>
</body></html>"""


def build_news_index(dates):
    """生成资讯首页（分页）"""
    total_pages = (len(dates) + PER_PAGE - 1) // PER_PAGE

    pages = {}
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * PER_PAGE
        page_dates = dates[start:start + PER_PAGE]

        cards = ""
        for date_str, summary_data in page_dates:
            total = summary_data.get("total_tweets", "?")
            # 取前2条推文做摘要
            top_items = []
            for section in summary_data.get("sections", []):
                for tweet in section.get("tweets", [])[:2]:
                    author = tweet.get("author", "")
                    cn = tweet.get("cn_summary", tweet.get("translation", ""))
                    text = tweet.get("text", "")[:80]
                    top_items.append(f"{author}: {cn or text}")
            summary_text = " · ".join(top_items[:3]) if top_items else f"共 {total} 条 AI 资讯"

            cards += f"""<article class="post-card"><div class="post-meta"><time>{date_str}</time><span class="tag news">资讯</span></div>
<h2><a href="/ai-news/{date_str}.html">AI 资讯速递 · {date_str}</a></h2>
<p>{summary_text}</p></article>\n"""

        # 分页
        if total_pages <= 1:
            pagination = ""
        else:
            parts = []
            for i in range(1, total_pages + 1):
                if i == page_num:
                    parts.append(f'<span class="current">{i}</span>')
                else:
                    href = "/ai-news.html" if i == 1 else f"/ai-news/page-{i}.html"
                    parts.append(f'<a href="{href}">{i}</a>')
            pagination = f'<div class="pagination">{"".join(parts)}</div>'

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 资讯 · 海之领域</title>
<style>{CSS}</style>
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="logo">海之领域</a>
{NAV}
</div></header>
<main class="container">
<section class="hero">
<h1>AI 资讯速递</h1>
<p class="hero-sub">每日精选 AI 领域热门动态</p>
</section>
<section class="posts">
{cards}</section>
{pagination}</main>
<footer class="site-footer"><div class="container">
<p>© 2026 海之领域</p><p class="footer-sub">xiweihai.site</p>
</div></footer>
</body></html>"""

        if page_num == 1:
            pages["ai-news.html"] = html
        else:
            pages[f"ai-news/page-{page_num}.html"] = html

    return pages


def main():
    os.makedirs(NEWS_DIR, exist_ok=True)

    # 扫描所有 JSON 文件
    json_files = sorted(glob.glob(os.path.join(NEWS_DIR, "*.json")), reverse=True)

    if not json_files:
        print("⚠️  没有找到资讯数据文件")
        # 生成一个空的占位页面
        pages = {
            "ai-news.html": f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 资讯 · 海之领域</title>
<style>{CSS}</style>
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="logo">海之领域</a>
{NAV}
</div></header>
<main class="container">
<section class="hero">
<h1>AI 资讯速递</h1>
<p class="hero-sub">每日精选 AI 领域热门动态</p>
</section>
<section class="posts">
<p style="text-align:center;color:var(--c-text-light);padding:48px 0">资讯即将上线，敬请期待。</p>
</section>
</main>
<footer class="site-footer"><div class="container">
<p>© 2026 海之领域</p><p class="footer-sub">xiweihai.site</p>
</div></footer>
</body></html>"""
        }
        for fn, content in pages.items():
            path = os.path.join(BLOG_DIR, fn)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  → {fn}")
        return

    print(f"📦 找到 {len(json_files)} 天的资讯数据")

    # 处理指定的 JSON（增量）或全部
    target = sys.argv[1] if len(sys.argv) > 1 else None

    dates_data = []  # [(date_str, summary_data), ...]

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)

        date_str = os.path.basename(jf).replace(".json", "")

        # 生成每日详情页
        if target is None or jf == target:
            daily_html = build_daily_page(date_str, data)
            daily_path = os.path.join(NEWS_DIR, f"{date_str}.html")
            with open(daily_path, "w", encoding="utf-8") as f:
                f.write(daily_html)
            print(f"  ✅ ai-news/{date_str}.html")

        # 收集摘要数据用于首页
        # 只取需要的信息（避免内存爆炸）
        summary = {
            "total_tweets": data.get("total_tweets", 0),
            "sections": []
        }
        for section in data.get("sections", []):
            s = {"name": section.get("name", ""), "tweets": []}
            for tweet in section.get("tweets", [])[:3]:
                s["tweets"].append({
                    "author": tweet.get("author", ""),
                    "cn_summary": tweet.get("cn_summary", tweet.get("translation", "")),
                    "text": tweet.get("text", "")[:100],
                })
            summary["sections"].append(s)
        dates_data.append((date_str, summary))

    # 生成资讯首页（分页）
    pages = build_news_index(dates_data)
    for fn, content in pages.items():
        path = os.path.join(BLOG_DIR, fn)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {fn}")

    # 清理多余分页
    total_pages = (len(dates_data) + PER_PAGE - 1) // PER_PAGE
    for f in os.listdir(NEWS_DIR):
        if f.startswith("page-") and f.endswith(".html"):
            try:
                num = int(f.replace("page-", "").replace(".html", ""))
                if num > total_pages:
                    os.remove(os.path.join(NEWS_DIR, f))
                    print(f"  🗑 ai-news/{f}")
            except ValueError:
                pass

    print(f"\n✅ 生成完成：{len(dates_data)} 天资讯，{total_pages} 页")


if __name__ == "__main__":
    main()
