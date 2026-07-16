# 海之领域 · 个人博客

> 在代码与生活之间，寻找值得记录的瞬间。

建平儿的技术笔记与随笔。纯 HTML+CSS，零框架，部署在阿里云 ECS + Caddy。

**线上地址**：[https://xiweihai.site](https://xiweihai.site)

## 技术栈

- 纯静态 HTML + CSS，零框架依赖
- Caddy 反向代理 + 自动 HTTPS
- 暗色模式自适应（`prefers-color-scheme`）
- 移动优先响应式布局
- RSS 订阅（`/feed.xml`）

## 目录结构

```
├── index.html          # 首页（自动生成）
├── page-2.html         # 分页（自动生成，超过10篇才出现）
├── feed.xml            # RSS（自动生成）
├── about.html          # 关于页
├── publish.py          # 发布脚本
└── posts/
    ├── manifest.json   # 文章索引（唯一数据源）
    ├── hello-world.html
    ├── ai-agent-pipeline.html
    ├── tech-vs-understanding.html
    ├── nas-self-hosting.html
    └── learning-tcm.html
```

## 发布新文章

1. 把文章 HTML 放到 `posts/` 目录
2. 在 `posts/manifest.json` 顶部加一条：
   ```json
   {"date": "2026-07-16", "tag": "tech", "title": "标题", "file": "new.html", "summary": "摘要"}
   ```
3. 运行：
   ```bash
   python3 publish.py --deploy
   ```

脚本自动处理首页分页、RSS 更新。

## Agent 写作指南

本仓库包含 `AGENTS.md`，Hermes Agent 克隆后会自动加载。
包含完整的文章写作规范、HTML 模板和部署流程，确保任何 Agent 写出的文章风格一致。

文章模板：`templates/article-template.html`

## License

MIT
