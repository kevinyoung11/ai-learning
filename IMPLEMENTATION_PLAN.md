# AI HOT 复刻 · 实现规划文档

> 目标定位:**个人自用**
> 难点源策略:**自托管 RSSHub**
> 评分/摘要:**LLM 生成**
> 技术栈:**见下文推荐**
> 参考站点:https://aihot.virxact.com
> 信息源清单:`news-source.md`(141 个源)

---

## 1. 一句话定义这个系统

> 把 141 个异构 AI 信息源,定时抓取 → 归一化 → 去重聚类 → LLM 打分写摘要 → 存库 → 前端按"热度 + 来源数"展示。

**网站(四个页面)是简单的 20%,数据管线是难的 80%。** 本文档把重心放在管线。

---

## 2. 最重要的认知:难点不在前端,在抓取

把 141 个源按获取难度分类(对照 `news-source.md`):

| 源类型 | 数量(约) | 获取方式 | 难度 |
|---|---|---|---|
| RSS 直供 | ~22 | 标准 RSS 解析 | ★ 容易 |
| 网页(无 RSS) | ~15 | RSSHub 路由 / 自写爬虫 | ★★★ 中高 |
| API(Qwen/HF) | ~2 | 各自 API | ★★ 中 |
| 公众号 | ~17 | RSSHub `wechat` 路由(依赖中转) | ★★★★ 高 |
| **X / Twitter** | **~85** | **RSSHub `twitter` 路由 / 付费 API** | ★★★★★ 最高 |

**结论:>70% 的源(X + 公众号)没有干净的官方 feed。** 这是整个项目成败的关键。

### 既定策略:自托管 RSSHub 收敛复杂度

[RSSHub](https://github.com/DIYgod/RSSHub) 已内置 Twitter、微信公众号、以及绝大多数源的路由,能把约 130/141 个源**统一成 RSS**。这样最难的问题(每个源各写爬虫)塌缩成最容易的问题(统一 RSS 解析)。

```
[ 141 异构源 ]
       │
       ▼
┌──────────────────┐
│  自托管 RSSHub    │  ← 把 X / 公众号 / 网页 统一成 RSS
│  (Docker)         │
└──────────────────┘
       │  统一 RSS / JSON Feed
       ▼
┌──────────────────┐
│  抓取调度器        │  ← 定时拉取所有 feed
└──────────────────┘
```

> ⚠️ RSSHub 的 Twitter / 微信路由依赖第三方中转或 Cookie,**会不稳定、会偶尔失效**。个人自用可接受(单源挂掉不影响整体),但必须把"单源失败"做成不阻塞管线的设计(见 §6 容错)。

---

## 3. 推荐技术栈

个人自用 + Python 抓取生态成熟 + 前端要好看,推荐**前后端分离**:

| 层 | 选型 | 理由 |
|---|---|---|
| 抓取/管道 | **Python**(`feedparser` + `httpx` + `APScheduler`) | RSS/爬虫/LLM 生态最成熟 |
| LLM | **Claude**(`claude-haiku-4-5` 打分 + `claude-sonnet-4-6` 写摘要) | 中文质量好,Haiku 便宜适合批量打分 |
| 存储 | **SQLite**(个人自用足够) | 零运维,单文件,后期可换 Postgres |
| 后端 API | **FastAPI** | 轻量,自动文档,和 Python 管道同语言 |
| 前端 | **Next.js + Tailwind**(静态/SSG) | 复刻已有的 Slate 设计稿 |
| 部署 | 一台小 VPS / 家用 NAS + Docker Compose | RSSHub + 管道 + API 一起跑 |
| 调度 | **APScheduler**(进程内)或系统 cron | 个人自用无需 Celery 等重型队列 |

> 个人自用阶段**刻意避免**:Kafka、Celery、Redis 队列、K8s。SQLite + 单进程定时任务就够,复杂度留到真要扩规模时再加。

---

## 4. 数据模型(整个系统的地基)

**四个页面其实是同一份数据的不同切片。先把 schema 定死,前端就是四个视图。**

```sql
-- 单条原始来源记录(全部资讯页的最小单位)
CREATE TABLE items (
  id            INTEGER PRIMARY KEY,
  source_id     TEXT NOT NULL,        -- 对应 sources.id
  source_type   TEXT NOT NULL,        -- x | wechat | rss | web | api
  title         TEXT NOT NULL,
  url           TEXT NOT NULL UNIQUE,  -- 去重第一道防线(URL 唯一)
  raw_content   TEXT,                  -- 正文/摘要原文
  published_at  TIMESTAMP NOT NULL,
  fetched_at    TIMESTAMP NOT NULL,
  content_hash  TEXT,                  -- 标题+正文归一化后的哈希,辅助去重
  story_id      INTEGER,               -- 聚类后归属的故事(NULL=未聚类)
  FOREIGN KEY (story_id) REFERENCES stories(id)
);

-- 聚合故事(精选页/详情页的单位,一个故事聚合多条 item)
CREATE TABLE stories (
  id            INTEGER PRIMARY KEY,
  canonical_title TEXT NOT NULL,       -- 代表性标题(取首发或最权威源)
  summary       TEXT,                  -- LLM 生成的编辑摘要
  category      TEXT,                  -- model | product | paper | industry | tutorial
  hotness       REAL DEFAULT 0,        -- 热度分(见 §5.3)
  source_count  INTEGER DEFAULT 1,     -- "N 个来源"
  first_seen_at TIMESTAMP NOT NULL,
  day           DATE NOT NULL,         -- 归属日期(按日分组)
  is_top        INTEGER DEFAULT 0      -- 是否当日 TOP
);

-- 源清单(141 个源的注册表)
CREATE TABLE sources (
  id            TEXT PRIMARY KEY,      -- 如 "x_openai"
  name          TEXT NOT NULL,         -- "X：OpenAI (@OpenAI)"
  type          TEXT NOT NULL,         -- x | wechat | rss | web | api
  feed_url      TEXT NOT NULL,         -- RSSHub 生成的 RSS 地址
  weight        REAL DEFAULT 1.0,      -- 源权威度(影响热度)
  enabled       INTEGER DEFAULT 1,
  last_ok_at    TIMESTAMP,             -- 上次成功抓取(监控失效源)
  fail_count    INTEGER DEFAULT 0
);

-- 每日摘要(摘要页)
CREATE TABLE digests (
  day           DATE PRIMARY KEY,
  narrative     TEXT,                  -- LLM 生成的当日综述
  stat_items    INTEGER, stat_stories INTEGER, stat_top_hotness REAL
);
```

每页对应的查询:
- **精选** = `stories WHERE day=today ORDER BY hotness DESC`
- **详情** = 一条 `story` + 其 `items`(按 `published_at`)
- **全部资讯** = `items ORDER BY published_at DESC`(可按 `source_type` 过滤)
- **每日摘要** = `digests WHERE day=?` + 当日 top stories

---

## 5. 核心管线(难点全在这)

```
拉取 → 归一化 → 去重 → 聚类 → LLM 打分 → LLM 摘要 → 写库
```

### 5.1 拉取(Fetch)
- 遍历 `sources` 表所有 `enabled=1` 的源,从其 `feed_url` 拉 RSS。
- 并发拉取(`httpx.AsyncClient`),单源超时 + 重试。
- **单源失败只记 `fail_count`,不中断整体。** 连续失败 N 次自动 `enabled=0` 并告警。

### 5.2 归一化 + 去重(两道防线)
1. **URL 唯一**:`items.url UNIQUE`,同一链接直接跳过。
2. **内容哈希**:标题去除表情/空白/标点后做 `content_hash`,近似重复也能挡。
3. **跨源聚类**(同一新闻多个源报道 → 一个 story):
   - 入门方案:标题 embedding(用 `voyage` / 本地 `bge` 模型)→ 余弦相似度 > 阈值即归为同一 story。
   - 简化方案(MVP):标题关键词重叠 + 时间窗(24h 内)+ 实体匹配。
   - **这一步直接决定"N 个来源"是否准确**,是产品信噪比的核心。

### 5.3 热度打分(LLM)
- 输入:story 的标题 + 各源摘要 + `source_count` + 源权威度 + 时间。
- 用 `claude-haiku-4-5` 批量给 0–100 分(便宜,适合每天几十条)。
- Prompt 要求模型综合:**话题重要性、多源覆盖度、时效性**,输出结构化 JSON 分数。
- 兜底:LLM 不可用时退化为规则分 = `f(source_count, source_weight, 时间衰减)`。

### 5.4 编辑摘要(LLM)
- 只对当日 **Top N**(如前 20)用 `claude-sonnet-4-6` 写 50–100 字中文点评。
- Prompt 强调:面向开发者/PM/研究者的**实践含义**,不是复述标题。
- **控成本**:只给 Top N 写、结果缓存、同一 story 不重复生成。

### 5.5 每日综述(LLM)
- 每天定时一次,把当日 top stories 喂给 Sonnet,生成 2–3 段叙事综述 → 写 `digests`。

---

## 6. 容错与成本控制(个人自用的关键)

| 关注点 | 做法 |
|---|---|
| 单源失效 | 失败不阻塞;连续失败自动禁用 + 记录,定期人工巡检 |
| RSSHub 不稳 | 抓取层和 RSSHub 解耦,RSSHub 挂了管线照常处理已有数据 |
| LLM 成本 | Haiku 打分(便宜)+ Sonnet 只写 Top N 摘要;结果全缓存;按 story 去重避免重复调用 |
| 抓取频率 | 个人自用每 1–2 小时一轮即可,不必实时 |
| 数据库 | SQLite 单文件,定期备份;增长后再迁 Postgres |

预估 LLM 成本(个人自用):每天 ~50 条打分 + ~20 条摘要 + 1 条综述,**月成本通常在几美元量级**(取决于内容长度)。

---

## 7. 分阶段路线图

### 阶段 0 · 地基(0.5 天)
- [ ] 建库:`items / stories / sources / digests` 四表
- [ ] 把 `news-source.md` 的 141 个源导入 `sources` 表(先填能确定的 `feed_url`)

### 阶段 1 · 跑通最容易的源(1 天)
- [ ] Python 抓取器:拉 ~22 个 RSS 源 → 归一化 → 写 `items`
- [ ] URL + 哈希去重
- [ ] FastAPI 出一个 `/items` 接口
- [ ] 前端套用 Slate 设计稿,先把"全部资讯"页跑起来

### 阶段 2 · 自托管 RSSHub,接入难点源(1–2 天)
- [ ] Docker 起 RSSHub
- [ ] 逐个映射 X / 公众号 / 网页源的 RSSHub 路由,回填 `feed_url`
- [ ] 容错:单源失败计数 + 自动禁用
- [ ] 标注哪些源拿不到(需付费 API 的留作二期)

### 阶段 3 · 聚类 + LLM(2 天)
- [ ] 跨源聚类 → 生成 `stories` + `source_count`
- [ ] Haiku 打分 → `hotness`
- [ ] Sonnet 给 Top N 写摘要
- [ ] 精选页 + 详情页跑起来

### 阶段 4 · 摘要 + 调度 + 收尾(1 天)
- [ ] 每日综述 → `digests` → 摘要页
- [ ] APScheduler 定时跑整条管线(每 1–2h)
- [ ] 失效源巡检脚本

> 个人自用总工期约 **5–7 个有效工作日**,可分多个周末推进。

---

## 8. 关键风险清单

1. **RSSHub 的 X/公众号路由失效** — 最大风险。缓解:容错设计 + 必要时对核心源改用付费 API。
2. **聚类质量** — 聚类不准会让"N 个来源"失真。先用简单方案,不行再上 embedding。
3. **LLM 成本失控** — 缓解:Haiku 打分 + 只给 Top N 写摘要 + 全缓存。
4. **法律/ToS** — 抓取 X/公众号处于灰色地带;**个人自用、不公开、不商用**风险最低,务必保持此边界。

---

## 9. 下一步建议

建议从**阶段 0 + 阶段 1** 开始:把四表建好、导入源、跑通 RSS 源 + "全部资讯"页。这能在 1–2 天内得到一个**真实能用、有数据**的雏形,验证整条链路,再逐步啃 RSSHub 和 LLM。

要我直接开始阶段 0(建库 + 导入 141 个源)吗?
