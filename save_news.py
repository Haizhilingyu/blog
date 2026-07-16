#!/usr/bin/env python3
"""
桥接脚本：读取 daily_ai_search.py 的输出 JSON，保存快照并生成 HTML

工作流程：
  daily_ai_search.py stdout → 本脚本 → ai-news/YYYY-MM-DD.json → news_generator.py

用法（在 cron job 中替换原来的直接调用）：
  python3 /root/kasm-browser/daily_ai_search.py 2>/dev/null | python3 /var/www/blog/save_news.py

或单独运行（传入JSON文件）：
  python3 /var/www/blog/save_news.py < news_data.json
"""
import json, sys, os, subprocess, datetime

BLOG_DIR = "/var/www/blog"
NEWS_DIR = os.path.join(BLOG_DIR, "ai-news")


def main():
    # 读取 stdin 的 JSON
    raw = sys.stdin.read().strip()
    if not raw:
        print("⚠️ 没有收到数据", file=sys.stderr)
        return

    # 解析采集结果
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # 如果不是JSON，可能是混合输出，尝试提取JSON部分
        lines = raw.split("\n")
        for line in reversed(lines):
            try:
                data = json.loads(line.strip())
                break
            except:
                continue
        else:
            print("⚠️ 无法解析JSON，保存原始输出", file=sys.stderr)
            today = datetime.date.today().isoformat()
            os.makedirs(NEWS_DIR, exist_ok=True)
            with open(os.path.join(NEWS_DIR, f"{today}.txt"), "w") as f:
                f.write(raw)
            return

    today = datetime.date.today().isoformat()
    os.makedirs(NEWS_DIR, exist_ok=True)

    # 如果数据来自飞书文档（标准格式），需要转换
    # daily_ai_search.py 输出格式: {"doc_url": "...", "total_tweets": N, ...}
    # 但完整推文数据在脚本内部，stdout只有摘要
    # 所以这里我们保存飞书文档URL，并尝试从stderr日志中提取

    # 保存快照
    snapshot_path = os.path.join(NEWS_DIR, f"{today}.json")
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 资讯快照已保存: {snapshot_path}", file=sys.stderr)

    # 生成 HTML
    result = subprocess.run(
        ["python3", os.path.join(BLOG_DIR, "news_generator.py"), snapshot_path],
        capture_output=True, text=True, timeout=30,
        cwd=BLOG_DIR
    )
    print(result.stdout, file=sys.stderr)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # 重新生成首页列表（确保新的一天出现在列表中）
    result2 = subprocess.run(
        ["python3", os.path.join(BLOG_DIR, "news_generator.py")],
        capture_output=True, text=True, timeout=30,
        cwd=BLOG_DIR
    )
    print(result2.stdout, file=sys.stderr)

    print(f"✅ HTML 页面已生成", file=sys.stderr)


if __name__ == "__main__":
    main()
