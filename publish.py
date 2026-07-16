#!/usr/bin/env python3
"""
海之领域博客发布脚本
用法：
  python3 publish.py              # 重新生成首页/分页/RSS（写本地）
  python3 publish.py --deploy     # 生成 + 部署到远程服务器

发布新文章只需：
  1. 把文章 HTML 放到 posts/ 目录
  2. 在 posts/manifest.json 加一条记录
  3. python3 publish.py --deploy
"""
import json, os, sys, datetime, subprocess
import xml.sax.saxutils as saxutils

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
MANIFEST = os.path.join(POSTS_DIR, "manifest.json")
PER_PAGE = 10
SITE_URL = "https://xiweihai.site"
SITE_NAME = "海之领域"
SITE_DESC = "建平儿的技术笔记与随笔"
REMOTE = "root@xiweihai.site"
REMOTE_DIR = "/var/www/blog"
TAG_LABELS = {"tech": "技术", "life": "随笔"}

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
.tag.tech{background:rgba(26,115,232,.12);color:var(--c-tag-tech)}
.tag.life{background:rgba(212,100,30,.12);color:var(--c-tag-life)}
.post-card h2{font-size:1.25rem;line-height:1.4;margin-bottom:8px}
.post-card h2 a{color:var(--c-text);text-decoration:none;transition:color .2s}
.post-card h2 a:hover{color:var(--c-accent)}
.post-card p{color:var(--c-text-light);font-size:.95rem;line-height:1.7}
.pagination{display:flex;justify-content:center;gap:8px;padding:32px 0}
.pagination a,.pagination span{display:inline-block;min-width:36px;height:36px;line-height:36px;text-align:center;border-radius:12px;text-decoration:none;font-size:.9rem;color:var(--c-text-light)}
.pagination .current{background:var(--c-accent);color:#fff}
.pagination a:hover{background:var(--c-border)}
.site-footer{padding:32px 0;border-top:1px solid var(--c-border);text-align:center}
.site-footer p{font-size:.85rem;color:var(--c-text-light)}
.footer-sub{margin-top:4px;font-size:.8rem;opacity:.6}
.site-footer a{color:var(--c-accent);text-decoration:none}
@media(max-width:640px){.hero{padding:40px 0 32px}.hero h1{font-size:1.4rem}.post-card{padding:20px 0}.post-card h2{font-size:1.1rem}.nav{gap:16px}}
"""


def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        posts = json.load(f)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def build_card(post):
    tag = post.get("tag", "tech")
    tag_label = TAG_LABELS.get(tag, tag)
    date = post["date"]
    title = post["title"]
    file = post["file"]
    summary = post["summary"]
    return (
        '<article class="post-card">'
        '<div class="post-meta">'
        f'<time>{date}</time>'
        f'<span class="tag {tag}">{tag_label}</span>'
        '</div>'
        f'<h2><a href="/posts/{file}">{title}</a></h2>'
        f'<p>{summary}</p>'
        '</article>'
    )


def build_page(posts, page_num, total_pages):
    cards = "\n".join(build_card(p) for p in posts)

    if total_pages <= 1:
        pagination = ""
    else:
        parts = []
        for i in range(1, total_pages + 1):
            if i == page_num:
                parts.append(f'<span class="current">{i}</span>')
            else:
                href = "/" if i == 1 else f"/page-{i}.html"
                parts.append(f'<a href="{href}">{i}</a>')
        pagination = '<div class="pagination">' + "".join(parts) + '</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{SITE_NAME} — {SITE_DESC}">
<title>{SITE_NAME} · xiweihai.site</title>
<style>{CSS}</style>
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="logo">{SITE_NAME}</a>
<nav class="nav"><a href="/">文章</a><a href="/about.html">关于</a><a href="/feed.xml">RSS</a></nav>
</div></header>
<main class="container">
<section class="hero">
<h1>在代码与生活之间，<br>寻找值得记录的瞬间。</h1>
<p class="hero-sub">{SITE_DESC}</p>
</section>
<section class="posts">
{cards}
</section>
{pagination}
</main>
<footer class="site-footer"><div class="container">
<p>© 2026 {SITE_NAME} · 由 <a href="https://hermes-agent.nousresearch.com">Hermes Agent</a> 驱动</p>
<p class="footer-sub">xiweihai.site</p>
</div></footer>
</body></html>"""


def build_feed(posts):
    items = []
    for p in posts:
        dt = datetime.datetime.strptime(p["date"], "%Y-%m-%d")
        rfc = dt.strftime("%a, %d %b %Y 00:00:00 +0800")
        title_esc = saxutils.escape(p["title"])
        summary_esc = saxutils.escape(p["summary"])
        items.append(
            f"<item>\n"
            f"<title>{title_esc}</title>\n"
            f"<link>{SITE_URL}/posts/{p['file']}</link>\n"
            f"<description>{summary_esc}</description>\n"
            f"<pubDate>{rfc}</pubDate>\n"
            f"</item>"
        )
    now = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    body = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>{SITE_NAME}</title>
<link>{SITE_URL}</link>
<description>{SITE_DESC}</description>
<language>zh-CN</language>
<lastBuildDate>{now}</lastBuildDate>
{body}
</channel>
</rss>"""


def generate_all(posts):
    total = len(posts)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    files = {}

    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * PER_PAGE
        end = start + PER_PAGE
        page_posts = posts[start:end]
        html = build_page(page_posts, page_num, total_pages)
        if page_num == 1:
            files["index.html"] = html
        else:
            files[f"page-{page_num}.html"] = html

    # 删除多余分页
    for f in os.listdir(BLOG_DIR):
        if f.startswith("page-") and f.endswith(".html") and f not in files:
            os.remove(os.path.join(BLOG_DIR, f))
            print(f"  🗑 删除多余分页: {f}")

    files["feed.xml"] = build_feed(posts)
    return files


def _is_remote():
    """检测是否运行在远程服务器上"""
    try:
        return os.path.exists("/var/www/blog/publish.py")
    except Exception:
        return False


def deploy(files):
    on_remote = _is_remote()
    for filename, content in files.items():
        local_path = os.path.join(BLOG_DIR, filename)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)
        if not on_remote:
            result = subprocess.run(
                ["scp", local_path, f"{REMOTE}:{REMOTE_DIR}/{filename}"],
                capture_output=True, text=True, timeout=30
            )
            ok = "✅" if result.returncode == 0 else "❌"
            print(f"  {ok} {filename}")
        else:
            print(f"  ✅ {filename}")

    if not on_remote:
        result = subprocess.run(
            ["scp", "-r", POSTS_DIR, f"{REMOTE}:{os.path.dirname(REMOTE_DIR)}/"],
            capture_output=True, text=True, timeout=30
        )
        ok = "✅" if result.returncode == 0 else "❌"
        print(f"  {ok} posts/ 目录已同步")


def main():
    print(f"📖 {SITE_NAME} 博客发布脚本\n")

    posts = load_manifest()
    print(f"📦 共 {len(posts)} 篇文章")

    missing = [p["file"] for p in posts if not os.path.exists(os.path.join(POSTS_DIR, p["file"]))]
    if missing:
        print(f"⚠️  警告: 文件不存在: {missing}")

    total_pages = (len(posts) + PER_PAGE - 1) // PER_PAGE
    print(f"📄 分页: {total_pages} 页（每页 {PER_PAGE} 篇）\n")

    files = generate_all(posts)
    print(f"🔧 生成 {len(files)} 个文件:")
    for fn in files:
        print(f"   → {fn}")

    if "--deploy" in sys.argv:
        print("\n🚀 部署中...")
        deploy(files)
        print(f"\n✅ 完成！访问 {SITE_URL}")
    else:
        for filename, content in files.items():
            with open(os.path.join(BLOG_DIR, filename), "w", encoding="utf-8") as f:
                f.write(content)
        print(f"\n✅ 本地生成完成。加 --deploy 部署。")


if __name__ == "__main__":
    main()
