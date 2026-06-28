from __future__ import annotations

from html import escape
from typing import Any


STYLE_CSS = """
:root {
  --ink: #18181B;
  --ink-soft: #27272A;
  --gray-1: #3F3F46;
  --gray-2: #52525B;
  --gray-3: #71717A;
  --gray-4: #A1A1AA;
  --gray-5: #C4C4CA;
  --line: #ECECEF;
  --line-2: #F1F1F3;
  --surface: #FAFAFA;
  --border: #E4E4E7;
  --card-border: #ECECEF;
  --amber: #EA580C;
  --amber-text: #A16207;
  --red: #DC2626;
  --white: #FFFFFF;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", Roboto, Helvetica, Arial, sans-serif;
  color: var(--ink);
  background: #F4F4F5;
  -webkit-font-smoothing: antialiased;
}
.page { max-width: 880px; margin: 24px auto; background: var(--white); border: 1px solid #E6E7E8; border-radius: 14px; overflow: hidden; }
a { color: inherit; text-decoration: none; }
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 14px 28px; background: var(--ink); }
.brand { font-size: 16px; font-weight: 500; color: #fff; letter-spacing: .3px; }
.brand .flame { color: #FB923C; }
.nav { display: flex; gap: 24px; font-size: 13.5px; color: var(--gray-4); }
.nav a:hover, .nav a.active { color: #fff; }
.nav a.active { font-weight: 500; }
.subscribe { font-size: 12.5px; color: var(--ink); background: var(--surface); padding: 6px 14px; border-radius: 8px; font-weight: 500; }
.section-head { padding: 22px 28px 6px; display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; }
.section-title { margin: 0; font-size: 20px; font-weight: 500; }
.section-sub { margin: 3px 0 0; font-size: 13px; color: var(--gray-3); }
.chips { display: flex; gap: 7px; flex-wrap: wrap; justify-content: flex-end; }
.chip { font-size: 12.5px; padding: 6px 13px; border-radius: 18px; background: #F4F4F5; color: var(--gray-2); }
.chip.on { background: var(--ink); color: #fff; }
.flame-score { color: var(--amber); font-weight: 500; }
.top-badge { font-size: 11.5px; font-weight: 500; color: #fff; background: var(--red); padding: 3px 11px; border-radius: 6px; }
.lead-card { margin: 14px 28px 6px; background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 20px 22px; }
.lead-meta { display: flex; align-items: center; gap: 9px; margin-bottom: 10px; font-size: 12px; color: var(--gray-3); }
.lead-title { margin: 0 0 8px; font-size: 22px; font-weight: 500; line-height: 1.3; }
.lead-summary { margin: 0 0 14px; font-size: 14px; line-height: 1.7; color: var(--gray-2); }
.lead-foot { display: flex; align-items: center; gap: 14px; font-size: 12.5px; color: var(--gray-3); }
.list { padding: 10px 28px 22px; display: flex; flex-direction: column; gap: 9px; }
.row { display: flex; gap: 16px; align-items: center; padding: 13px 18px; border: 1px solid var(--card-border); border-radius: 12px; }
.row:hover, .entry:hover, .mr:hover { background: #FAFAFA; }
.rank { font-size: 19px; font-weight: 500; color: var(--gray-5); width: 22px; text-align: center; }
.row-body { flex: 1; min-width: 0; }
.row-title { margin: 0 0 3px; font-size: 15px; font-weight: 500; line-height: 1.4; }
.row-meta { margin: 0; font-size: 12.5px; color: var(--gray-3); }
.muted { color: var(--gray-3); }
.back { padding: 14px 28px; font-size: 13px; color: var(--gray-3); display: block; }
.detail { padding: 0 28px 24px; }
.detail-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-size: 12.5px; color: var(--gray-3); }
.detail-title { font-size: 26px; font-weight: 500; line-height: 1.3; margin: 0 0 18px; }
.ai-summary { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; margin-bottom: 24px; }
.ai-label { margin: 0 0 6px; font-size: 11.5px; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; color: var(--amber-text); }
.ai-text { margin: 0; font-size: 14.5px; line-height: 1.8; color: var(--gray-1); }
.sources-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.sources-head .t { font-size: 15px; font-weight: 500; }
.src { display: flex; gap: 13px; padding: 14px 0; border-top: 1px solid var(--line); align-items: flex-start; }
.src:last-child { border-bottom: 1px solid var(--line); }
.src-icon { width: 34px; height: 34px; flex-shrink: 0; border-radius: 8px; background: #F4F4F5; display: flex; align-items: center; justify-content: center; color: var(--gray-2); font-size: 13px; }
.src-body { flex: 1; min-width: 0; }
.src-title { margin: 0 0 2px; font-size: 14.5px; line-height: 1.4; }
.src-meta { margin: 0; font-size: 12px; color: var(--gray-4); }
.src-ext { color: var(--gray-5); align-self: center; }
.feed-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 28px 12px; }
.feed-head .t { margin: 0; font-size: 18px; font-weight: 500; }
.feed-head .s { margin: 2px 0 0; font-size: 12.5px; color: var(--gray-3); }
.feed-body { display: flex; border-top: 1px solid var(--line); }
.sidebar { width: 188px; flex-shrink: 0; border-right: 1px solid var(--line); padding: 16px 12px; }
.sidebar .h { margin: 0 0 10px; font-size: 11px; color: var(--gray-4); letter-spacing: 1px; text-transform: uppercase; }
.filter { display: flex; flex-direction: column; gap: 3px; font-size: 13px; }
.filter span { padding: 7px 10px; border-radius: 8px; color: var(--gray-1); display: flex; justify-content: space-between; gap: 12px; }
.filter span.on { background: var(--ink); color: #fff; }
.stream { flex: 1; min-width: 0; padding: 6px 0 12px; }
.time-group { padding: 8px 20px 4px; font-size: 11px; color: var(--gray-4); letter-spacing: .5px; }
.entry { display: flex; gap: 12px; padding: 11px 20px; border-bottom: 1px solid var(--line-2); }
.entry .ts { font-size: 11.5px; color: var(--gray-4); flex-shrink: 0; width: 48px; padding-top: 2px; }
.entry .eb { flex: 1; min-width: 0; }
.entry .et { margin: 0 0 2px; font-size: 14px; line-height: 1.45; }
.entry .em { margin: 0; font-size: 12px; color: var(--gray-4); }
.digest-head { padding: 22px 28px 4px; }
.digest-label { margin: 0 0 4px; font-size: 11.5px; letter-spacing: 1px; text-transform: uppercase; color: var(--amber-text); }
.digest-title { margin: 0; font-size: 24px; font-weight: 500; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 16px 28px; }
.stat { background: var(--surface); border-radius: 10px; padding: 14px 16px; }
.stat .l { margin: 0; font-size: 12px; color: var(--gray-3); }
.stat .v { margin: 3px 0 0; font-size: 24px; font-weight: 500; }
.narrative { padding: 0 28px 8px; }
.narrative p { margin: 0 0 14px; font-size: 15px; line-height: 1.85; color: var(--ink-soft); }
.must-read { padding: 10px 28px 24px; }
.must-read .h { margin: 0 0 12px; font-size: 13px; font-weight: 500; color: var(--gray-2); letter-spacing: .5px; }
.mr-list { display: flex; flex-direction: column; gap: 8px; }
.mr { display: flex; gap: 12px; align-items: center; padding: 12px 16px; border: 1px solid var(--card-border); border-radius: 11px; }
.mr .rk { font-size: 15px; color: var(--gray-5); font-weight: 500; width: 42px; text-align: center; flex-shrink: 0; }
.mr .tx { flex: 1; font-size: 14.5px; }
.mr .sc { font-size: 12px; flex-shrink: 0; }
@media (max-width: 720px) {
  .page { margin: 0; border-radius: 0; border-left: 0; border-right: 0; }
  .topbar, .section-head, .feed-head { padding-left: 16px; padding-right: 16px; }
  .nav { gap: 12px; font-size: 12.5px; }
  .subscribe { display: none; }
  .section-head { align-items: flex-start; flex-direction: column; }
  .lead-card, .list, .detail, .stats, .narrative, .must-read { margin-left: 16px; margin-right: 16px; padding-left: 0; padding-right: 0; }
  .lead-card { padding: 16px; }
  .feed-body { flex-direction: column; }
  .sidebar { width: auto; border-right: 0; border-bottom: 1px solid var(--line); }
  .stats { grid-template-columns: 1fr; }
}
"""


def render_home(items: list[dict[str, Any]], day: str | None = None) -> str:
    lead = items[0] if items else None
    rows = items[1:]
    lead_html = ""
    if lead:
        lead_html = f"""
        <a class="lead-card" style="display:block" href="/story/{h(lead['story_id'])}">
          <div class="lead-meta">
            <span class="top-badge">TOP 1</span>
            <span>{h(lead['source_type'])} · {time_text(lead['published_at'])}</span>
            <span style="margin-left:auto" class="flame-score">&#128293; {score_text(lead)}</span>
          </div>
          <p class="lead-title">{h(lead['title'])}</p>
          <p class="lead-summary">{h(lead['raw_content'])}</p>
          <div class="lead-foot">
            <span>{h(lead['source_id'])}</span>
            <span style="color:var(--gray-1)">&#9783; {lead.get('source_count') or 1} 个来源</span>
          </div>
        </a>
        """
    row_html = "\n".join(render_home_row(index + 2, item) for index, item in enumerate(rows))
    return page(
        "AI HOT · 精选",
        "home",
        f"""
        <div class="section-head">
          <div>
            <p class="section-title">今日精选</p>
            <p class="section-sub">{display_day(day)} · {len(items)} 个聚合故事</p>
          </div>
          <div class="chips">
            <span class="chip on">全部</span><span class="chip">模型</span><span class="chip">产品</span><span class="chip">论文</span><span class="chip">行业</span>
          </div>
        </div>
        {lead_html}
        <div class="list">{row_html}</div>
        """,
    )


def render_story(story: dict[str, Any], items: list[dict[str, Any]]) -> str:
    source_rows = "\n".join(
        f"""
        <a class="src" href="{h(item['url'])}">
          <span class="src-icon">{source_icon(item['source_type'])}</span>
          <div class="src-body">
            <p class="src-title">{h(item['title'])}</p>
            <p class="src-meta">{h(item['source_id'])} · {time_text(item['published_at'])}</p>
          </div>
          <span class="src-ext">&#8599;</span>
        </a>
        """
        for item in items
    )
    return page(
        "AI HOT · 故事详情",
        "",
        f"""
        <a class="back" href="/">&#8592; 返回精选</a>
        <div class="detail">
          <div class="detail-meta">
            <span class="top-badge">TOP</span>
            <span>{h(story['day'])}</span>
            <span style="margin-left:auto" class="flame-score">&#128293; 热度 {score_text(story)}</span>
          </div>
          <h1 class="detail-title">{h(story['canonical_title'])}</h1>
          <div class="ai-summary">
            <p class="ai-label">&#10024; AI 编辑摘要</p>
            <p class="ai-text">{h(story['summary'])}</p>
          </div>
          <div class="sources-head">
            <span class="t">全部来源 · {len(items)}</span>
            <span class="muted" style="font-size:12px">按时间排序</span>
          </div>
          {source_rows}
        </div>
        """,
    )


def render_all_news(items: list[dict[str, Any]], sources: list[dict[str, Any]]) -> str:
    type_counts: dict[str, int] = {}
    for source in sources:
        source_type = str(source["source_type"])
        type_counts[source_type] = type_counts.get(source_type, 0) + 1
    source_filters = "\n".join(
        f'<span><span>{h(kind)}</span><span>{count}</span></span>' for kind, count in sorted(type_counts.items())
    )
    source_health = "\n".join(
        f'<span><span>{h(source["name"])}</span><span>{h(str(source.get("last_status")))}</span></span>'
        for source in sources
    )
    entries = render_news_entries_by_day(items)
    return page(
        "AI HOT · 全部资讯",
        "all",
        f"""
        <div class="feed-head">
          <div><p class="t">全部资讯</p><p class="s">{len(sources)} 个来源 · 本地聚合</p></div>
          <span class="muted" style="font-size:12.5px">&#8635; 本地数据</span>
        </div>
        <div class="feed-body">
          <div class="sidebar">
            <p class="h">来源类型</p>
            <div class="filter"><span class="on"><span>全部</span><span>{len(sources)}</span></span>{source_filters}</div>
            <p class="h" style="margin-top:18px">源状态</p>
            <div class="filter">{source_health}</div>
          </div>
          <div class="stream">{entries}</div>
        </div>
        """,
    )


def render_digest(day: str, daily: dict[str, Any], items: list[dict[str, Any]]) -> str:
    top_score = max((float(item.get("hotness") or 0) for item in items), default=0)
    must_read = "\n".join(
        f"""
        <a class="mr" href="/story/{h(item['story_id'])}">
          <span class="{ 'top-badge' if index == 1 else 'rk' }">{'TOP 1' if index == 1 else index}</span>
          <span class="tx">{h(item['title'])}</span>
          <span class="sc flame-score">&#128293; {score_text(item)}</span>
        </a>
        """
        for index, item in enumerate(items, start=1)
    )
    return page(
        "AI HOT · 每日摘要",
        "digest",
        f"""
        <div class="digest-head">
          <p class="digest-label">&#10024; AI 生成 · 每日摘要</p>
          <h1 class="digest-title">{h(day)} AI 速报</h1>
        </div>
        <div class="stats">
          <div class="stat"><p class="l">今日条目</p><p class="v">{len(items)}</p></div>
          <div class="stat"><p class="l">聚合故事</p><p class="v">{daily['story_count']}</p></div>
          <div class="stat"><p class="l">最高热度</p><p class="v" style="color:var(--amber)">{int(top_score)}</p></div>
        </div>
        <div class="narrative"><p>{h(daily['narrative']).replace(chr(10), '<br>')}</p></div>
        <div class="must-read"><p class="h">今日必读</p><div class="mr-list">{must_read}</div></div>
        """,
    )


def render_home_row(rank: int, item: dict[str, Any]) -> str:
    return f"""
    <a class="row" href="/story/{h(item['story_id'])}">
      <span class="rank">{rank}</span>
      <div class="row-body">
        <p class="row-title">{h(item['title'])}</p>
        <p class="row-meta">{h(item['source_id'])} · {item.get('source_count') or 1} 个来源</p>
      </div>
      <span class="flame-score">&#128293; {score_text(item)}</span>
    </a>
    """


def render_news_entries_by_day(items: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(day_text(item.get("published_at")), []).append(item)

    chunks: list[str] = []
    for day, day_items in grouped.items():
        entries = "\n".join(
            f"""
        <a class="entry" href="{h(item['url'])}">
          <span class="ts">{time_text(item['published_at'])}</span>
          <div class="eb">
            <p class="et">{h(item['title'])}</p>
            <p class="em">{h(item['source_type'])} · {h(item['source_id'])}</p>
          </div>
        </a>
        """
            for item in day_items
        )
        chunks.append(f'<div class="time-group">{h(day)}</div>{entries}')
    return "\n".join(chunks)


def page(title: str, active: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="page">
  <div class="topbar">
    <a class="brand" href="/"><span class="flame">&#128293;</span> AI HOT</a>
    <nav class="nav">
      <a class="{active_class(active, 'home')}" href="/">精选</a>
      <a class="{active_class(active, 'all')}" href="/all-news">全部资讯</a>
      <a class="{active_class(active, 'digest')}" href="/digest">每日摘要</a>
      <a href="/sources">来源</a>
    </nav>
    <a class="subscribe" href="/docs">API</a>
  </div>
  {body}
</div>
</body>
</html>"""


def active_class(active: str, name: str) -> str:
    return "active" if active == name else ""


def score_text(row: dict[str, Any]) -> str:
    return str(int(round(float(row.get("hotness") or 0))))


def time_text(value: Any) -> str:
    text = str(value)
    if "T" in text:
        return text.split("T", 1)[1][:5]
    return text[:10]


def day_text(value: Any) -> str:
    return str(value)[:10]


def display_day(value: str | None) -> str:
    if not value:
        return "最新日期"
    parts = value.split("-")
    if len(parts) == 3:
        return f"{parts[0]}年{int(parts[1])}月{int(parts[2])}日"
    return value


def source_icon(source_type: str) -> str:
    if source_type == "rss":
        return "RSS"
    if source_type == "wechat":
        return "&#9993;"
    if source_type == "x":
        return "X"
    return "&#127760;"


def h(value: Any) -> str:
    return escape(str(value), quote=True)
