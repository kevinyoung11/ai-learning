from __future__ import annotations

from html import escape
from typing import Any


STYLE_CSS = """
:root {
  --ink: #18181B;
  --bg: #060814;
  --panel: #0D111D;
  --panel-2: #111827;
  --card: #101624;
  --card-soft: #151D2D;
  --line: rgba(148, 163, 184, .18);
  --line-strong: rgba(148, 163, 184, .28);
  --text: #E5E7EB;
  --muted: #94A3B8;
  --subtle: #64748B;
  --accent: #F59E0B;
  --accent-2: #38BDF8;
  --green: #22C55E;
  --red: #F43F5E;
  --white: #FFFFFF;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", Roboto, Helvetica, Arial, sans-serif;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
.app-shell { display: grid; grid-template-columns: 212px minmax(0, 1fr); min-height: 100vh; }
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 22px 16px;
  border-right: 1px solid var(--line);
  background: rgba(8, 11, 20, .96);
}
.brand { display: flex; align-items: center; gap: 8px; height: 36px; margin: 0 4px 22px; font-weight: 750; letter-spacing: .04em; }
.brand-ai { color: var(--white); }
.brand-hot { color: var(--accent); }
.side-group { margin: 20px 8px 8px; font-size: 11px; color: var(--subtle); letter-spacing: .12em; }
.side-link {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 38px;
  padding: 0 10px;
  border-radius: 10px;
  color: var(--muted);
  font-size: 14px;
}
.side-link:hover, .side-link-active { color: var(--white); background: rgba(148, 163, 184, .12); }
.side-icon { width: 18px; text-align: center; color: var(--accent-2); }
.sidebar-footer {
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 18px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 12px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.6;
  background: rgba(255, 255, 255, .03);
}
.app-main { min-width: 0; padding: 22px 28px 56px; }
.page-grid { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 22px; max-width: 1180px; margin: 0 auto; }
.page-grid-single { max-width: 920px; margin: 0 auto; }
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 0 16px;
}
.eyebrow { margin: 0 0 7px; color: var(--accent); font-size: 12px; letter-spacing: .12em; text-transform: uppercase; }
.page-title { margin: 0; font-size: 28px; line-height: 1.15; font-weight: 760; letter-spacing: 0; }
.page-subtitle { margin: 7px 0 0; color: var(--muted); font-size: 13px; }
.toolbar { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 7px 10px;
  color: var(--muted);
  background: rgba(255, 255, 255, .04);
  font-size: 12px;
}
.chip-active { color: var(--bg); background: var(--accent); border-color: var(--accent); font-weight: 700; }
.timeline { position: relative; display: flex; flex-direction: column; gap: 14px; }
.timeline-item { display: grid; grid-template-columns: 48px 18px minmax(0, 1fr); gap: 12px; }
.timeline-time { color: var(--muted); font-size: 12px; padding-top: 22px; text-align: right; font-variant-numeric: tabular-nums; }
.timeline-rail { position: relative; display: flex; justify-content: center; }
.timeline-rail::before { content: ""; position: absolute; top: 0; bottom: -14px; width: 1px; background: var(--line); }
.timeline-dot { z-index: 1; margin-top: 25px; width: 9px; height: 9px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 4px rgba(245, 158, 11, .12); }
.timeline-card {
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(16, 22, 36, .88);
  padding: 16px 18px;
  box-shadow: 0 18px 60px rgba(0, 0, 0, .22);
}
.timeline-card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.timeline-head-left, .timeline-head-right { display: flex; align-items: center; gap: 8px; min-width: 0; }
.timeline-source { color: var(--muted); font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.timeline-selected-badge { color: var(--bg); background: var(--green); border-radius: 999px; padding: 3px 7px; font-size: 11px; font-weight: 750; }
.timeline-score { color: var(--accent); font-size: 12px; font-weight: 780; font-variant-numeric: tabular-nums; }
.timeline-title { display: block; margin: 0 0 8px; color: var(--white); font-size: 17px; line-height: 1.42; font-weight: 720; }
.timeline-summary { margin: 0; color: #CBD5E1; font-size: 14px; line-height: 1.72; }
.timeline-tags { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 12px; }
.tag { color: #BAE6FD; background: rgba(56, 189, 248, .12); border: 1px solid rgba(56, 189, 248, .22); border-radius: 999px; padding: 4px 8px; font-size: 11px; }
.timeline-divider { border: 0; border-top: 1px solid var(--line); margin: 13px 0 10px; }
.timeline-reason { color: var(--muted); font-size: 13px; line-height: 1.7; }
.timeline-reason-label { color: var(--accent); font-weight: 700; }
.right-rail { display: flex; flex-direction: column; gap: 14px; position: sticky; top: 22px; align-self: start; }
.metric-card, .source-panel, .daily-brief, .story-panel {
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(13, 17, 29, .86);
  padding: 16px;
}
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.metric { padding: 12px; border-radius: 12px; background: rgba(255, 255, 255, .04); }
.metric-label { margin: 0; color: var(--muted); font-size: 12px; }
.metric-value { margin: 4px 0 0; font-size: 24px; font-weight: 760; color: var(--white); }
.panel-title { margin: 0 0 12px; font-size: 14px; color: var(--white); }
.source-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 8px 0; border-top: 1px solid var(--line); font-size: 12px; }
.source-row:first-of-type { border-top: 0; }
.source-name { color: var(--muted); min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.status { color: var(--subtle); font-variant-numeric: tabular-nums; }
.status-success { color: var(--green); }
.status-failed { color: var(--red); }
.stream { display: flex; flex-direction: column; gap: 14px; }
.time-group { margin: 12px 0 2px 78px; color: var(--subtle); font-size: 12px; letter-spacing: .08em; }
.daily-brief { margin-top: 10px; }
.daily-brief-text { margin: 0; color: #CBD5E1; font-size: 14px; line-height: 1.8; }
.story-panel { margin-top: 12px; }
.back-link { color: var(--muted); font-size: 13px; }
.source-list { margin-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.source-card { display: flex; gap: 12px; align-items: flex-start; padding: 12px; border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,.03); }
.source-icon { flex: 0 0 auto; width: 34px; height: 34px; display: grid; place-items: center; border-radius: 9px; color: var(--accent-2); background: rgba(56,189,248,.12); font-size: 12px; }
.source-body { min-width: 0; }
.source-title { margin: 0 0 4px; color: var(--white); font-size: 14px; line-height: 1.45; }
.source-meta { margin: 0; color: var(--muted); font-size: 12px; }
.m-tabbar { display: none; }
@media (max-width: 920px) {
  .app-shell { display: block; }
  .sidebar { display: none; }
  .app-main { padding: 14px 14px 80px; }
  .page-grid { grid-template-columns: 1fr; }
  .right-rail { position: static; }
  .timeline-item { grid-template-columns: 42px 14px minmax(0, 1fr); gap: 9px; }
  .timeline-time { font-size: 11px; }
  .page-header { align-items: flex-start; flex-direction: column; }
  .toolbar { justify-content: flex-start; }
  .m-tabbar {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 20;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid var(--line);
    background: rgba(8, 11, 20, .94);
    backdrop-filter: blur(16px);
  }
  .m-tab { display: grid; gap: 3px; place-items: center; padding: 9px 4px 10px; color: var(--muted); font-size: 11px; }
  .m-tab-active { color: var(--accent); }
}
"""


def render_home(items: list[dict[str, Any]], day: str | None = None) -> str:
    body = f"""
    <div class="page-grid">
      <section>
        {page_header("精选", "今天值得看的 AI 动态", f"{display_day(day)} · {len(items)} 个聚合故事")}
        <div class="timeline">{render_timeline(items, selected=True)}</div>
      </section>
      <aside class="right-rail">
        {metrics_card(len(items), count_sources(items), top_score(items))}
        <section class="source-panel">
          <h2 class="panel-title">最新精选</h2>
          <div class="toolbar">
            <span class="chip chip-active">全部</span><span class="chip">模型发布</span><span class="chip">产品更新</span><span class="chip">论文研究</span>
          </div>
        </section>
      </aside>
    </div>
    """
    return page("AI HOT · 精选", "home", body)


def render_story(story: dict[str, Any], items: list[dict[str, Any]]) -> str:
    source_rows = "\n".join(
        f"""
        <a class="source-card" href="{h(item['url'])}">
          <span class="source-icon">{source_icon(item['source_type'])}</span>
          <span class="source-body">
            <p class="source-title">{h(item['title'])}</p>
            <p class="source-meta">{h(item['source_id'])} · {time_text(item['published_at'])}</p>
          </span>
        </a>
        """
        for item in items
    )
    body = f"""
    <div class="page-grid-single">
      <a class="back-link" href="/">← 返回精选</a>
      <article class="story-panel">
        <div class="timeline-card-head">
          <div class="timeline-head-left">
            <span class="timeline-selected-badge">精选</span>
            <span class="timeline-source">{h(story['day'])}</span>
          </div>
          <span class="timeline-score">AI 推荐分 {score_text(story)}</span>
        </div>
        <h1 class="page-title">{h(story['canonical_title'])}</h1>
        <p class="timeline-summary">{h(story['summary'])}</p>
        <hr class="timeline-divider"/>
        <div class="timeline-reason"><span class="timeline-reason-label">推荐理由：</span>{recommendation_text(story)}</div>
      </article>
      <section class="story-panel">
        <h2 class="panel-title">全部来源 · {len(items)}</h2>
        <div class="source-list">{source_rows}</div>
      </section>
    </div>
    """
    return page("AI HOT · 故事详情", "", body)


def render_all_news(items: list[dict[str, Any]], sources: list[dict[str, Any]]) -> str:
    body = f"""
    <div class="page-grid">
      <section>
        {page_header("全部资讯", "按发布时间聚合的本地信息流", f"{len(items)} 条动态 · {len(sources)} 个来源")}
        <div class="stream">{render_news_entries_by_day(items)}</div>
      </section>
      <aside class="right-rail">
        <section class="source-panel">
          <h2 class="panel-title">来源状态</h2>
          {render_source_health(sources)}
        </section>
      </aside>
    </div>
    """
    return page("AI HOT · 全部资讯", "all", body)


def render_digest(day: str, daily: dict[str, Any], items: list[dict[str, Any]]) -> str:
    body = f"""
    <div class="page-grid">
      <section>
        {page_header("AI 日报", "每日摘要与必读条目", f"{h(day)} AI 速报")}
        <section class="daily-brief">
          <p class="daily-brief-text">{h(daily['narrative']).replace(chr(10), '<br>')}</p>
        </section>
        <h2 class="panel-title" style="margin-top:22px">今日必读</h2>
        <div class="timeline">{render_timeline(items, selected=True)}</div>
      </section>
      <aside class="right-rail">
        {metrics_card(len(items), int(daily['story_count']), top_score(items))}
      </aside>
    </div>
    """
    return page("AI HOT · 每日摘要", "digest", body)


def page_header(label: str, title: str, subtitle: str) -> str:
    return f"""
    <header class="page-header">
      <div>
        <p class="eyebrow">{h(label)}</p>
        <h1 class="page-title">{h(title)}</h1>
        <p class="page-subtitle">{h(subtitle)}</p>
      </div>
      <div class="toolbar">
        <span class="chip chip-active">精选</span>
        <span class="chip">模型</span>
        <span class="chip">产品</span>
        <span class="chip">研究</span>
      </div>
    </header>
    """


def render_timeline(items: list[dict[str, Any]], *, selected: bool = False) -> str:
    return "\n".join(render_timeline_item(item, selected=selected) for item in items)


def render_timeline_item(item: dict[str, Any], *, selected: bool = False) -> str:
    href = f"/story/{h(item['story_id'])}" if item.get("story_id") else h(item["url"])
    badge = '<span class="timeline-selected-badge">精选</span>' if selected else ""
    return f"""
    <div class="timeline-item">
      <div class="timeline-time">{time_text(item['published_at'])}</div>
      <div class="timeline-rail" aria-hidden="true"><span class="timeline-dot"></span></div>
      <article class="timeline-card">
        <div class="timeline-card-head">
          <div class="timeline-head-left">
            <span class="timeline-source">{h(item['source_id'])}</span>
          </div>
          <div class="timeline-head-right">{badge}<span class="timeline-score">{score_text(item)}</span></div>
        </div>
        <a class="timeline-title" href="{href}">{h(item['title'])}</a>
        <p class="timeline-summary">{h(item['raw_content'])}</p>
        <div class="timeline-tags">{render_tags(item)}</div>
        <hr class="timeline-divider"/>
        <div class="timeline-reason"><span class="timeline-reason-label">推荐理由：</span>{recommendation_text(item)}</div>
      </article>
    </div>
    """


def render_news_entries_by_day(items: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(day_text(item.get("published_at")), []).append(item)

    chunks: list[str] = []
    for day, day_items in grouped.items():
        chunks.append(f'<div class="time-group">{h(day)}</div>{render_timeline(day_items)}')
    return "\n".join(chunks)


def render_tags(item: dict[str, Any]) -> str:
    source_type = str(item.get("source_type") or "source")
    tags = [source_type, source_category(source_type)]
    return "".join(f'<span class="tag">{h(tag)}</span>' for tag in dict.fromkeys(tags) if tag)


def render_source_health(sources: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"""
        <div class="source-row">
          <span class="source-name">{h(source['name'])}</span>
          <span class="status status-{h(str(source.get('last_status') or 'none'))}">{h(str(source.get('last_status')))}</span>
        </div>
        """
        for source in sources
    )


def metrics_card(first: int, second: int, score: float) -> str:
    return f"""
    <section class="metric-card">
      <h2 class="panel-title">今日概览</h2>
      <div class="metric-grid">
        <div class="metric"><p class="metric-label">今日条目</p><p class="metric-value">{first}</p></div>
        <div class="metric"><p class="metric-label">来源/故事</p><p class="metric-value">{second}</p></div>
        <div class="metric"><p class="metric-label">最高分</p><p class="metric-value">{int(score)}</p></div>
        <div class="metric"><p class="metric-label">刷新</p><p class="metric-value">1h</p></div>
      </div>
    </section>
    """


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
<div class="app-shell">
  <aside class="sidebar" aria-label="主导航">
    <a class="brand" href="/"><span class="brand-ai">AI</span><span class="brand-hot">HOT</span></a>
    <nav>
      <div class="side-group">内容</div>
      <a class="side-link {active_class(active, 'home')}" href="/"><span class="side-icon">⚡</span><span>精选</span></a>
      <a class="side-link {active_class(active, 'all')}" href="/all-news"><span class="side-icon">☷</span><span>全部 AI 动态</span></a>
      <a class="side-link {active_class(active, 'digest')}" href="/digest"><span class="side-icon">☰</span><span>AI 日报</span></a>
      <div class="side-group">接入</div>
      <a class="side-link" href="/sources"><span class="side-icon">◎</span><span>来源状态</span></a>
      <a class="side-link" href="/docs"><span class="side-icon">API</span><span>API</span></a>
    </nav>
    <div class="sidebar-footer">每小时扫描公开源。RSS/API 默认启用；公众号与 X 已登记，等待专用接入器。</div>
  </aside>
  <main class="app-main">{body}</main>
  <nav class="m-tabbar" aria-label="移动端主导航">
    <a class="m-tab {active_class(active, 'home', 'm-tab-active')}" href="/">精选</a>
    <a class="m-tab {active_class(active, 'all', 'm-tab-active')}" href="/all-news">全部</a>
    <a class="m-tab {active_class(active, 'digest', 'm-tab-active')}" href="/digest">日报</a>
  </nav>
</div>
</body>
</html>"""


def active_class(active: str, name: str, class_name: str = "side-link-active") -> str:
    return class_name if active == name else ""


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


def count_sources(items: list[dict[str, Any]]) -> int:
    return len({str(item.get("source_id")) for item in items})


def top_score(items: list[dict[str, Any]]) -> float:
    return max((float(item.get("hotness") or 0) for item in items), default=0)


def source_icon(source_type: str) -> str:
    if source_type == "rss":
        return "RSS"
    if source_type == "wechat":
        return "WX"
    if source_type == "x":
        return "X"
    return "WEB"


def source_category(source_type: str) -> str:
    return {
        "rss": "官方/RSS",
        "github": "GitHub",
        "model": "模型",
        "community": "社区讨论",
        "wechat": "公众号",
        "x": "X",
        "html": "网页",
    }.get(source_type, "")


def recommendation_text(row: dict[str, Any]) -> str:
    title = str(row.get("title") or row.get("canonical_title") or "这条动态")
    source_count = int(row.get("source_count") or 1)
    if source_count > 1:
        return f"多个来源同时指向「{h(title)}」，说明它不是孤立噪声，值得优先查看。"
    return f"「{h(title)}」来自已登记信源，按时间与热度进入本轮精选。"


def h(value: Any) -> str:
    return escape(str(value), quote=True)
