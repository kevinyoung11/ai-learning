社区里最稳的路线不是“先啃数学再做项目”，而是 应用先行、逐层下钻：

推荐路线：AI 应用工程 → LLM 应用系统 → 深度学习基础 → Transformer/LLM 从零实现 → 训练/评测/对齐 → GPU/推理/分布式底层。

1. 应用层：先会用 AI 做东西
    - 学 Prompt、RAG、Agent、函数调用、评测、监控、权限、安全。
    - 项目：做一个企业知识库问答、代码助手、数据分析 Agent。
    - 资源：Full Stack LLM Bootcamp，覆盖 Prompt、RAG、LLMOps、Agent、UX、部署等，很适合作为应用层入口。
        https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/

2. 工程层：把 AI 应用做成可靠系统
    - 学：数据管道、向量库、检索评测、缓存、队列、日志、A/B、成本控制、失败兜底。
    - 关键心法：不要只调 prompt，要建立 eval set。
    - 项目：同一个 RAG 系统做 3 版检索策略，对比准确率、延迟、成本。

3. ML / DL 基础：理解模型为什么能学
    - 学：监督学习、损失函数、梯度下降、过拟合、正则化、CNN、RNN、Transformer 基础。
    - 资源：fast.ai 很适合“先实践再下钻”，它明确是给有编程经验的人学实际深度学习，并且从可用模型逐步深入到原理。
        https://course.fast.ai/

    - 补理论：Stanford CS229，机器学习传统基础。
        https://cs229.stanford.edu/

4. 模型层：从零实现神经网络和 GPT
    - 学：反向传播、embedding、attention、tokenizer、Transformer block、训练 loop。
    - 资源：Karpathy 的 Neural Networks: Zero to Hero，路线就是从 backprop 一直写到 GPT 和 tokenizer。
        https://karpathy.ai/zero-to-hero.html

    - 项目：自己实现一个小 GPT，训练字符级/小语料语言模型。

5. LLM 训练层：数据、扩展、评测、对齐
    - 学：预训练数据清洗、tokenization、scaling law、SFT、DPO/RLHF、reasoning eval。
    - 资源：Stanford CS336: Language Modeling from Scratch，内容覆盖 tokenizer、Transformer、训练、GPU 优化、数据、对齐，属于从应用往底层走的核心课。
        https://stanford-cs336.github.io/spring2025/

6. 系统底层：推理、GPU、Kernel、分布式
    - 学：CUDA/Triton、FlashAttention、KV cache、量化、speculative decoding、tensor/pipeline/data parallel。
    - 项目：写一个 attention kernel；把一个小模型从 PyTorch eager 优化到 torch.compile/Triton；部署 vLLM/TensorRT-LLM 对比吞吐。
    - 资源：GPU Mode lectures。
        https://github.com/gpu-mode/lectures

我会这样排 6-12 个月：

- 第 1 个月：LLM API、Prompt、RAG、Agent，做 2 个可用应用。
- 第 2-3 个月：LLMOps、评测、部署、成本控制，把应用做可靠。
- 第 3-5 个月：fast.ai + CS229，补 ML/DL 基础。
- 第 5-7 个月：Karpathy，从零写 micrograd、makemore、小 GPT、tokenizer。
- 第 7-10 个月：Stanford CS336，系统性理解 LLM 训练全流程。
- 第 10 个月以后：GPU/Triton/推理优化/分布式训练，进入真正底层。

一句话：先成为能交付 AI 应用的人，再成为懂模型的人，最后再下到训练系统和 GPU kernel。 这条路线最不容易半路放弃，也最贴近现在社区和工业界的需求。



---



要同时做到两件事：

1. 追上 AI 应用层最新技术
2. 具备底层不可替代的核心竞争力

你不能只学“工具”，也不能一上来只啃 CUDA。最优解是建立一个 T 型能力结构：

横向追应用层，纵向扎到底层系统和模型机制。

一、应用层最新技术要追什么

现在 AI 应用层的主线已经从“会调 API”变成了：

- Agentic Workflow：多步任务、工具调用、计划执行、反思、状态管理。
- Context Engineering：不只是 prompt，而是设计模型看到什么、什么时候看、怎么看、如何隔离上下文、如何控制成本。近期论文也把它描述为从 prompt engineering 升级到企业多 Agent
架构的关键能力。

- RAG 2.0 / GraphRAG / Hybrid Search：向量检索只是基础，真正难点是 query rewriting、rerank、权限过滤、引用溯源、评测。
- MCP / 工具协议化：AI 应用会越来越像“模型 + 工具 + 上下文 + 权限系统”，MCP 这类协议让 Agent 能标准化连接外部系统。
- Eval / Observability：应用层竞争力不在 demo，而在能不能量化幻觉率、任务完成率、成本、延迟、失败原因。
- Inference-first 架构：行业重点正从训练转向大规模推理，成本、吞吐、缓存、KV cache、路由、模型选择都会变成核心工程问题。
- Agent 安全与治理：权限边界、人类审批、审计、prompt injection 防护、数据泄露防护。

参考趋势：企业 AI 正从实验进入真实流程，重点变成上下文、控制、治理、成本和可靠性，而不是单纯模型能力。相关资料可看 TechRadar 对 enterprise AI/agents 的 2026 趋势总结，以及
近期 agent serving 和 context engineering 论文。
https://www.techradar.com/pro/2026-the-year-enterprise-ai-finally-gets-to-work
https://arxiv.org/abs/2603.16104
https://arxiv.org/abs/2603.09619

二、应用层怎么追最新

不要靠刷新闻。建立固定输入源：

- 每周看一次：LangChain、LlamaIndex、OpenAI、Anthropic、Google AI、Hugging Face、vLLM、SGLang、llama.cpp、MCP 生态更新。
- 每周读 2-3 篇论文摘要：重点看 Agent、RAG、Inference、Evaluation、Alignment。
- 每月复现一个新技术：比如 MCP server、GraphRAG、agent memory、workflow cache、structured output eval。
- 保持一个自己的 AI 应用模板：认证、日志、RAG、工具调用、eval、trace、成本统计都内置。每次新技术都往这个模板里接。

应用层高手不是“知道很多框架”，而是能判断：这个技术能不能让任务完成率更高、成本更低、延迟更稳、风险更可控。

三、底层核心竞争力是什么

底层最核心的竞争力不是“知道 Transformer”，而是这几类能力：

1. 模型机制
    - Transformer、attention、tokenizer、embedding、loss、sampling、RLHF/DPO、long context。
    - 能从零写一个小 GPT，知道每一层张量形状和计算成本。

2. 训练能力
    - 数据清洗、预训练、SFT、偏好优化、评测集构建。
    - 明白模型能力来自数据、架构、训练目标和算力的组合。

3. 推理系统能力
    - KV cache、batching、PagedAttention、speculative decoding、quantization、LoRA serving。
    - 熟悉 vLLM、SGLang、TensorRT-LLM、llama.cpp。
    - 这是未来非常重要，因为 AI 应用规模化后，推理成本就是利润空间。

4. GPU / 系统能力
    - CUDA / Triton、显存模型、kernel fusion、通信开销、分布式并行。
    - 不一定人人都要成为 CUDA 专家，但如果你能优化推理吞吐和显存，占位会很硬。

5. 数据系统能力
    - 检索、索引、缓存、调度、流式处理、权限过滤、数据血缘。
    - Agent workflow 本质上越来越像数据系统，近期论文也在从 query planning 和 caching 角度优化 agent serving。

6. 评测能力
    - 会设计 benchmark、golden set、自动打分、人审闭环、线上回归。
    - 这点非常稀缺。很多人会做 demo，少数人能证明系统真的变好。

四、最建议你形成的能力组合

如果目标是“应用层跟得上，底层有核心竞争力”，我建议主线定成：

> AI 应用架构师 + LLM 推理系统工程能力

这是比“纯 prompt 工程师”硬得多，也比“纯算法研究”更容易落地的组合。

你要能做到：

- 能设计一个生产级 Agent/RAG 系统。
- 能给系统建立 eval 和 observability。
- 能判断用 GPT-5、Claude、本地模型、SLM、微调模型还是 RAG。
- 能看懂 Transformer 和训练流程。
- 能理解 vLLM/SGLang 为什么快。
- 能优化一次推理链路的成本和延迟。
- 能把业务问题翻译成数据、上下文、工具、模型、评测的问题。

五、具体学习路线

短期 1-2 个月：

- 做 2 个真实 AI 应用：RAG 知识库、Agent 工作流。
- 接入 tracing、eval、rerank、权限过滤、成本统计。
- 学 MCP、function calling、structured output。

中期 3-6 个月：

- 读 fast.ai 或 CS229 补 ML/DL。
- 跟 Karpathy 从零写 micrograd、makemore、小 GPT。
- 学 Hugging Face Transformers、datasets、PEFT。
- 训练/微调一个小模型，做评测对比。

长期 6-12 个月：

- 学 Stanford CS336 这类 LLM from scratch 课程。
- 深入 vLLM / SGLang / llama.cpp。
- 学 CUDA 或 Triton，至少写 attention、matmul、layernorm 的简化 kernel。
- 做一个推理优化项目：同一模型在不同 serving 框架下比较吞吐、延迟、显存、成本。

六、判断你有没有核心竞争力的标准

你可以用这几个问题自测：

- 一个 RAG 回答错了，你能定位是检索、rerank、上下文、prompt、模型还是评测问题吗？
- 一个 Agent 成本太高，你能从模型路由、缓存、并发、上下文压缩、工具调用上优化吗？
- 一个模型推理慢，你能解释瓶颈在 prefill、decode、KV cache、显存还是网络通信吗？
- 一个新论文/新框架出来，你能判断它解决的是 toy problem 还是真实生产瓶颈吗？
- 你能从零写一个小 Transformer，并能把它部署成服务吗？

如果这些能做到，你就不是“会用 AI 工具的人”，而是能构建 AI 系统的人。



---


我看了 /Users/yangyang03/Desktop/apzone/script-killer。这个项目的定位比普通 AI 应用更好：它表面是 中文短视频创意工作流 App，但真正有价值的第二层是 AI 自我评测、自我诊断、自
  我派单、自我开发 PR 的闭环系统。

  你应该围绕这个项目，把能力做成这条主线：

  > AI 创作应用层能力 + Agent 开发闭环系统 + Eval/质量治理能力

  这比单纯做一个“AI 生成文案工具”更有底层竞争力。

  你项目现在已经有的基础

  - 产品工作流：src/features/script-workflow/，负责 setting candidates、format candidates、final seed。
  - Prompt/LLM 层：prompts.ts、llm-workflow.ts、normalize/provider。
  - 质量评测：evals/、scripts/run-eval.mjs、evals/rubric.md。
  - 自动质量闭环：/Users/yangyang03/Desktop/apzone/script-killer/docs/auto-dev/automation-loop.md。
  - AI 开发自动化：scripts/run-ai-dev-autopilot.mjs，已经有 issue -> branch -> Codex -> verification -> commit -> PR 的雏形。
  - 人审机制：/Users/yangyang03/Desktop/apzone/script-killer/docs/auto-dev/review-checklist.md。

  所以你的项目不是从 0 开始追 AI 应用层，而是已经站在 AI workflow + eval + autonomous dev loop 这个方向上。

  应用层最新技术，你应该这样追
  不要泛泛追 LangChain、Agent、RAG。结合这个项目，重点追这 5 类：

  1. Context Engineering
      - 把用户 idea、平台、风格、拍摄条件、历史偏好、失败案例、rubric 组织成高质量上下文。
      - 你的项目可以做成：每次生成不只是 prompt，而是一个 context pack，包含用户输入、创作约束、历史好样本、坏样本、评测维度。

  2. Agentic Workflow
      - 现在是线性 workflow：生成 setting -> 选 setting -> 生成 format -> final seed。
      - 下一步可以变成多 Agent：创意发散 Agent、可拍性审查 Agent、平台适配 Agent、反套路 Agent、最终仲裁 Agent。

  3. Eval-Driven Product Development
      - 你已经有 evals/rubric.md 和 run-eval.mjs，这是最重要的资产。
      - 应用层高手的核心不是“生成更长”，而是能证明“这版 prompt/流程真的更好”。

  4. Human Preference Loop
      - 你的 evals/human-preferences.md、feedback 目录已经在这个方向。
      - 下一步要把用户选择、放弃、修改、复制、导出都变成训练/评测信号。

  5. AI Dev Autopilot
      - 你的 auto-dev.md 和 scripts/run-ai-dev-autopilot.mjs 方向非常值得继续。
      - 这会让项目从“AI 应用”升级成“AI 参与开发 AI 应用”的系统。

  底层核心竞争力，结合你项目不是先卷 CUDA
  你的项目现阶段最应该沉淀的底层能力不是 GPU kernel，而是这几种更贴近落地的底层能力：

  1. Workflow State Machine 能力
      - 把 AI 创作过程建模成清晰状态机。
      - 每一步输入、输出、失败、重试、回滚、人工介入都可追踪。
      - 这是 Agent 系统的底层骨架。

  2. Eval System 能力
      - 你要能设计 golden samples、rubric、judge calibration、regression report。
      - 能判断一次 prompt 改动是“单样本变好”还是“整体退化”。
      - 这类能力非常稀缺，比会调 prompt 硬很多。

  3. Context / Memory 能力
      - 用户偏好、历史反馈、优秀样本、失败样本如何进入上下文。
      - 哪些进 prompt，哪些进检索，哪些进 profile，哪些只做 eval。
      - 这是未来 AI 应用层的核心竞争力。

  4. Agent Safety / Automation Guardrail
      - 你的 auto-dev loop 已经有“不改 secrets、不弱化测试、不自动 merge”等规则。
      - 继续强化：scope validation、risk labels、CODEOWNERS、人审 gate、失败分类、自动回滚。

  5. Model Abstraction / Routing 能力
      - 不要把项目绑死在一个 provider。
      - 建议形成能力：便宜模型做草稿，强模型做审查，结构化模型做 normalize，judge 模型做 eval。
      - 后面再加 latency、cost、success rate 的模型路由。

  你接下来最值得做的 4 个升级

  1. 把 run-eval.mjs 从单一总分升级成多维度报告：specificity、conflict、shootability、platform fit、premature script risk。
  2. 给每次 workflow 生成 trace：输入、prompt version、model、输出、normalize 结果、eval 分数、用户选择。
  3. 把 human feedback 变成稳定闭环：用户选择/编辑/丢弃 -> feedback event -> candidate eval sample -> human approve -> golden set。
  4. 把 AI dev autopilot 做成真正可观测：任务成功率、失败类型、平均修复轮次、最常失败模块、PR review 通过率。

  我还顺手看到一个小质量信号：scripts/run-ai-dev-autopilot.mjs 里 buildAutopilotPlan 返回对象中 prompt 字段写了两次，前一个会被后一个覆盖。功能上未必出错，但这是自动化核心脚
  本，值得清掉这类隐患。

  结论：你的路线不应该是“做一个 AI 创意工具”，而应该是：

  > 用 Script Killer 做载体，训练自己成为 AI 应用架构 + Eval 系统 + Agent 自动化工程 方向的人。

  这条路线既能追应用层最新技术，也能形成真正的底层竞争力。


---




- 一个 RAG 回答错了，你能定位是检索、rerank、上下文、prompt、模型还是评测问题吗？
- 一个 Agent 成本太高，你能从模型路由、缓存、并发、上下文压缩、工具调用上优化吗？
- 一个模型推理慢，你能解释瓶颈在 prefill、decode、KV cache、显存还是网络通信吗？
- 一个新论文/新框架出来，你能判断它解决的是 toy problem 还是真实生产瓶颈吗？
- 你能从零写一个小 Transformer，并能把它部署成服务吗？ 以上这几个问题，我一个都回答不出来


• 这很正常，而且这其实是好消息：你现在已经知道“不会的核心问题”是什么了。接下来不要补一堆散课，而是把这 5 个问题变成你的学习主线。

我建议你分三层补，不要一口吃到底层。

第一层：先补 AI 应用诊断能力

目标：能回答这两个问题：

- RAG 错了，问题在哪？
- Agent 成本高，怎么优化？

你先学这些：

- RAG 基本链路：query rewrite、embedding、retrieval、rerank、context packing、generation、citation。
- Agent 基本链路：planner、tool call、memory、state、retry、guardrail、eval。
- Eval 基础：golden set、pass/fail case、LLM judge、人类偏好、回归测试。

结合你的 script-killer，可以这样练：

- 把一次创意生成失败拆成：输入问题、prompt 问题、候选生成问题、评测问题、用户偏好问题。
- 给 evals/rubric.md 每个维度加失败案例。
- 每次 prompt 改动都问：它改善了哪个维度？有没有让别的维度退化？

你不用先懂 Transformer，也能先具备 AI 应用层的判断力。

第二层：补 LLM 系统能力

目标：能回答：

- 为什么 Agent 成本高？
- 为什么模型慢？
- 什么时候该换模型、缓存、压缩上下文、拆任务？

你要理解这些概念：

- token 成本：input token、output token、context window。
- latency：首 token 延迟、总生成时间。
- prefill：模型读 prompt 的阶段。
- decode：模型一个 token 一个 token 生成的阶段。
- KV cache：避免重复计算历史上下文。
- batch：多请求合并推理。
- quantization：降低显存和成本。
- model routing：简单任务用便宜模型，复杂任务用强模型。

这层不要求你写 CUDA，但要能做工程判断。

比如你的项目里可以练：

- 哪些步骤必须用强模型？
- 哪些步骤可以用便宜模型？
- 哪些结果可以缓存？
- 哪些上下文可以压缩？
- 哪些评测可以离线跑，不要每次用户请求都跑？

第三层：补模型底层

目标：能回答：

- Transformer 怎么工作？
- 小模型怎么训练？
- 推理为什么慢？

学习顺序不要反：

1. Python / PyTorch 基础。
2. 手写一个小神经网络。
3. 理解反向传播。
4. 理解 embedding。
5. 理解 attention。
6. 手写一个 mini Transformer。
7. 训练一个字符级 GPT。
8. 把它包成 API 服务。

这一步推荐跟 Karpathy 的路线走：
https://karpathy.ai/zero-to-hero.html

给你一个最现实的 90 天路线

第 1-2 周：RAG / Agent 诊断
做一张表：问题现象、可能原因、验证方法、修复动作。比如“回答错了”不能直接怪模型，要检查 retrieval 命中、上下文是否污染、prompt 是否约束不清、eval 是否错判。

第 3-4 周：把 script-killer 的 eval 做扎实
围绕 specificity、conflict、shootability、platform fit 做失败样本库。你的目标不是“生成更好看”，而是能解释为什么好/坏。

第 5-6 周：成本和延迟优化
给每次 AI 调用记录：model、input tokens、output tokens、耗时、失败原因、用户是否采用。你会开始自然理解为什么上下文、缓存、模型路由重要。

第 7-10 周：PyTorch + mini GPT
照 Karpathy 写 micrograd、makemore、mini GPT。不求大模型，只求每一层你都知道张量怎么流动。

第 11-12 周：部署一个小模型服务
用 FastAPI 或 Node 包一个本地模型/小模型推理服务，做一次完整链路：输入 -> tokenizer -> model -> decode -> API 返回。

你现在最不应该做的事

- 不要一上来学 CUDA。
- 不要同时追 20 个框架。
- 不要把“看论文”当主线。
- 不要只做 demo，不做 eval。
- 不要只问模型“为什么错”，要让系统记录证据。

你当前项目最适合练的不是“底层训练大模型”，而是：

> 用 script-killer 练成 AI 应用诊断、评测闭环、Agent 工程化能力；同时用 Karpathy 路线补模型底层。

这两条线并行，3 个月后你至少能回答前两个问题，6 个月后能回答前四个问题，9-12 个月后再认真碰第五个问题。




---



以上问题一个都回答不出来


---



这很正常，而且这其实是好消息：你现在已经知道“不会的核心问题”是什么了。接下来不要补一堆散课，而是把这 5 个问题变成你的学习主线。

我建议你分三层补，不要一口吃到底层。

第一层：先补 AI 应用诊断能力

目标：能回答这两个问题：

- RAG 错了，问题在哪？
- Agent 成本高，怎么优化？

你先学这些：

- RAG 基本链路：query rewrite、embedding、retrieval、rerank、context packing、generation、citation。
- Agent 基本链路：planner、tool call、memory、state、retry、guardrail、eval。
- Eval 基础：golden set、pass/fail case、LLM judge、人类偏好、回归测试。

结合你的 script-killer，可以这样练：

- 把一次创意生成失败拆成：输入问题、prompt 问题、候选生成问题、评测问题、用户偏好问题。
- 给 evals/rubric.md 每个维度加失败案例。
- 每次 prompt 改动都问：它改善了哪个维度？有没有让别的维度退化？

你不用先懂 Transformer，也能先具备 AI 应用层的判断力。

第二层：补 LLM 系统能力

目标：能回答：

- 为什么 Agent 成本高？
- 为什么模型慢？
- 什么时候该换模型、缓存、压缩上下文、拆任务？

你要理解这些概念：

- token 成本：input token、output token、context window。
- latency：首 token 延迟、总生成时间。
- prefill：模型读 prompt 的阶段。
- decode：模型一个 token 一个 token 生成的阶段。
- KV cache：避免重复计算历史上下文。
- batch：多请求合并推理。
- quantization：降低显存和成本。
- model routing：简单任务用便宜模型，复杂任务用强模型。

这层不要求你写 CUDA，但要能做工程判断。

比如你的项目里可以练：

- 哪些步骤必须用强模型？
- 哪些步骤可以用便宜模型？
- 哪些结果可以缓存？
- 哪些上下文可以压缩？
- 哪些评测可以离线跑，不要每次用户请求都跑？

第三层：补模型底层

目标：能回答：

- Transformer 怎么工作？
- 小模型怎么训练？
- 推理为什么慢？

学习顺序不要反：

1. Python / PyTorch 基础。
2. 手写一个小神经网络。
3. 理解反向传播。
4. 理解 embedding。
5. 理解 attention。
6. 手写一个 mini Transformer。
7. 训练一个字符级 GPT。
8. 把它包成 API 服务。

这一步推荐跟 Karpathy 的路线走：
https://karpathy.ai/zero-to-hero.html

给你一个最现实的 90 天路线

第 1-2 周：RAG / Agent 诊断
做一张表：问题现象、可能原因、验证方法、修复动作。比如“回答错了”不能直接怪模型，要检查 retrieval 命中、上下文是否污染、prompt 是否约束不清、eval 是否错判。

第 3-4 周：把 script-killer 的 eval 做扎实
围绕 specificity、conflict、shootability、platform fit 做失败样本库。你的目标不是“生成更好看”，而是能解释为什么好/坏。

第 5-6 周：成本和延迟优化
给每次 AI 调用记录：model、input tokens、output tokens、耗时、失败原因、用户是否采用。你会开始自然理解为什么上下文、缓存、模型路由重要。

第 7-10 周：PyTorch + mini GPT
照 Karpathy 写 micrograd、makemore、mini GPT。不求大模型，只求每一层你都知道张量怎么流动。

第 11-12 周：部署一个小模型服务
用 FastAPI 或 Node 包一个本地模型/小模型推理服务，做一次完整链路：输入 -> tokenizer -> model -> decode -> API 返回。

你现在最不应该做的事

- 不要一上来学 CUDA。
- 不要同时追 20 个框架。
- 不要把“看论文”当主线。
- 不要只做 demo，不做 eval。
- 不要只问模型“为什么错”，要让系统记录证据。

你当前项目最适合练的不是“底层训练大模型”，而是：

> 用 script-killer 练成 AI 应用诊断、评测闭环、Agent 工程化能力；同时用 Karpathy 路线补模型底层。

这两条线并行，3 个月后你至少能回答前两个问题，6 个月后能回答前四个问题，9-12 个月后再认真碰第五个问题。


---


结合社区里，分别把每一层如何学习或者路线最高效，推荐课程给我，如何由浅入深的学习，如何通过输出倒逼输入的方式进行学习，我有知乎，B站，抖音，youtube账号

可以。结合社区主流路线，我建议你不要按“课程目录”学，而是按 问题能力层级 学。你的目标不是“看完课”，而是逐步能回答那些核心问题。

总路线
第 0 层：会用 AI 做东西
第 1 层：会诊断 RAG / Agent 为什么错
第 2 层：会做 Eval、观测、质量闭环
第 3 层：懂 LLM 应用系统性能和成本
第 4 层：懂 Transformer / 训练 / 推理底层
第 5 层：能判断论文和框架是不是解决真实问题

对你来说，主线项目就用 script-killer，不要另开太多坑。所有学习都回到这个项目里验证。

第 0 层：AI 应用入门
目标：能做出一个可用 AI App，而不是只会聊天。

学什么：

- Prompt 基础
- Structured Output
- Function Calling / Tool Calling
- 简单 RAG
- 简单 Agent
- UI + API + 模型调用

推荐课程：

- DeepLearning.AI 的 AI Prompting for Everyone
- DeepLearning.AI 的 Build with Andrew
- Full Stack Deep Learning 的 LLM Bootcamp

Full Stack LLM Bootcamp 很适合从应用层入门，内容包括 prompt、LLMOps、外部知识增强、工具调用、LLM app 发布等。
https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/

输出倒逼输入：

- 知乎：写《我用 AI 做了一个短视频创意生成器，第一版踩了哪些坑》
- B站 / YouTube：录 5 分钟 demo，展示 script-killer 从 idea 到 final seed
- 抖音：发 30 秒产品使用片段，标题用“AI 帮我把一个粗糙想法变成短视频选题”

第 1 层：RAG / Agent 诊断能力
目标：能回答“错在哪里”，而不是只说“模型不行”。

学什么：

- RAG 链路：query rewrite、embedding、retrieval、rerank、context packing、generation
- Agent 链路：plan、tool、memory、state、observation、retry
- 常见错误归因：检索没命中、上下文污染、prompt 约束不清、模型能力不足、eval 错判

推荐课程：

- DeepLearning.AI 的 Retrieval Augmented Generation (RAG)
- Hugging Face AI Agents Course
- DeepLearning.AI / Arize AI 的 Evaluating AI Agents
- LlamaIndex / LangChain 官方教程，按需看，不要从头刷文档

Hugging Face Agents Course 的结构很适合入门 Agent：先讲 Tools、Thoughts、Actions、Observations，再讲 smolagents、LangGraph、LlamaIndex，并且有作业和 leaderboard。
https://huggingface.co/learn/agents-course/unit0/introduction

结合你的项目练：

- 把 script-killer 每次生成失败拆成 6 类：输入问题、prompt 问题、模型问题、候选生成问题、评测问题、用户偏好问题。
- 给每个失败样本写一条 diagnosis。
- 做一个 evals/diagnostics 报告：失败原因 top 5。

输出倒逼输入：

- 知乎系列：《AI 应用出错，不要先怪模型：RAG/Agent 诊断清单》
- B站 / YouTube：录一次“我如何定位 AI 生成结果太泛的问题”
- 抖音：做短内容，“AI 回答错了，可能不是模型差，而是这 5 个环节错了”

第 2 层：Eval / 质量闭环能力
目标：能证明一次改动真的变好。

这是你最应该优先建立护城河的一层，因为你的项目已经有 evals/rubric.md、run-eval.mjs、auto-quality-loop。

学什么：

- Golden Samples
- Rubric
- LLM Judge
- Human Preference
- Regression Eval
- Prompt Versioning
- Failure Taxonomy

推荐课程：

- Full Stack Deep Learning 的 LLMOps 部分
- DeepLearning.AI 的 Evaluation and Monitoring 相关短课
- Arize / LangSmith / LangFuse 的 eval、trace、observability 文档

DeepLearning.AI 的课程目录里，RAG、Agents、LLMOps、Evaluation and Monitoring、LLM Serving 都已经是独立热门方向，说明社区也在从“会调模型”转向“会评测和上线”。
https://www.deeplearning.ai/courses

结合你的项目练：

- 把 evals/rubric.md 里的维度变成机器可读评分。
- 每次 prompt 改动必须生成 before/after report。
- 建一个 human preference event：用户选了哪个 setting、改了哪里、丢弃了哪个。
- 把用户反馈沉淀成新的 eval sample，但必须人工 approve。

输出倒逼输入：

- 知乎：写《AI 产品真正的壁垒不是 Prompt，而是 Eval》
- B站 / YouTube：讲解你的 script-killer eval 报告
- 抖音：发“我让 AI 自己给创意打分，结果发现 prompt 改坏了”

第 3 层：LLM 系统成本与性能
目标：能回答“Agent 成本为什么高，模型为什么慢”。

学什么：

- input tokens / output tokens
- prefill / decode
- KV cache
- batching
- streaming
- semantic cache
- model routing
- quantization
- vLLM / SGLang / llama.cpp 基础

推荐课程：

- DeepLearning.AI Fast & Efficient LLM Inference with vLLM
- DeepLearning.AI Efficient Inference with SGLang
- vLLM 官方文档
- SGLang 官方文档

vLLM 文档里已经把在线 serving、batching、prefix caching、speculative decoding、LoRA、metrics、Prometheus/Grafana 等列成核心功能，这正是生产级推理系统要关注的东西。
https://docs.vllm.ai/en/latest/getting_started/quickstart/

结合你的项目练：

- 记录每次模型调用：model、input tokens、output tokens、latency、cost、是否被用户采用。
- 把低价值步骤换成便宜模型。
- 给相同输入加缓存。
- 把长上下文压缩成 brief。
- 把离线 eval 和在线生成分开，不要所有东西都实时跑。

输出倒逼输入：

- 知乎：《一个 Agent 为什么贵？从 token、缓存、模型路由说起》
- B站 / YouTube：做一次成本优化实录：优化前多少钱，优化后多少钱
- 抖音：做“AI 应用省钱的 3 个办法：缓存、路由、压缩上下文”

第 4 层：深度学习 / Transformer 底层
目标：能从零写一个小 Transformer，并知道模型为什么这样工作。

学什么：

- Python / PyTorch
- tensor shape
- loss
- gradient descent
- backprop
- embedding
- attention
- Transformer block
- tokenizer
- training loop

推荐课程顺序：

1. fast.ai Practical Deep Learning for Coders
    适合先动手。它强调先用实际例子，再逐步下钻到神经网络、NLP、从零模型、部署。
    https://course.fast.ai/

2. Karpathy Neural Networks: Zero to Hero
    这是底层入门最强路线之一，从 micrograd、makemore 到 GPT 和 tokenizer。
    https://karpathy.ai/zero-to-hero.html

3. 3Blue1Brown 神经网络 / 线代系列
    用来补直觉，不要当主线。

结合你的项目练：

- 不要一开始训练大模型。
- 写一个字符级 mini GPT。
- 用中文短视频标题训练一个小模型。
- 把它包成 API，让 script-killer 可以调用一个本地 toy model。
- 目标不是效果好，而是打通 tokenizer -> model -> decode -> API。

输出倒逼输入：

- 知乎：《我从零写 mini GPT，终于理解了 attention》
- B站 / YouTube：录屏讲 tensor shape 怎么流
- 抖音：做“Transformer 不是魔法，它每一步都在算什么”

第 5 层：LLM from Scratch / 训练系统 / 论文判断
目标：能判断一个框架或论文解决的是 toy problem 还是真实生产瓶颈。

学什么：

- tokenizer
- pretraining data
- Transformer architecture
- optimizer
- GPU memory
- distributed training
- scaling law
- evaluation
- SFT / DPO / RLHF
- inference optimization

推荐课程：

- Stanford CS336: Language Modeling from Scratch
- Full Stack Deep Learning 深度学习工程课
- GPU Mode lectures，等你过了前面几层再看

CS336 是很硬的路线：它要求 Python、PyTorch、系统优化、数学基础，并且作业覆盖 tokenizer、Transformer、训练、Triton/FlashAttention、分布式、数据清洗、对齐和推理。不要太早上，
6 个月后再啃更合适。
https://stanford-cs336.github.io/spring2025/

输出倒逼输入：

- 知乎：《读一篇 LLM 论文，我会问这 7 个问题》
- B站 / YouTube：每月讲一篇论文，只讲它解决了哪个真实瓶颈
- 抖音：做“这个新 Agent 框架到底有没有用？看 3 个指标”

你的最高效学习节奏
每周固定节奏：

- 2 小时：看课程
- 4 小时：改 script-killer
- 2 小时：写文章/脚本
- 1 小时：复盘本周学到的判断框架

不要追太多课。每一层只选 1-2 个主课。

3 个月执行版
第 1 个月：AI 应用 + Agent/RAG 诊断
主课：Full Stack LLM Bootcamp + Hugging Face Agents Course
项目输出：给 script-killer 加 trace、失败分类、prompt version
内容输出：4 篇知乎，4 个 B站/YouTube 短视频，8 条抖音

第 2 个月：Eval / 质量闭环
主课：DeepLearning.AI RAG、Agent Evaluation、LLMOps 相关短课
项目输出：before/after eval report、human preference loop、golden samples
内容输出：一个“AI 产品质量闭环”系列

第 3 个月：成本 / 性能 / 基础模型
主课：vLLM / SGLang 入门 + fast.ai 前几课
项目输出：模型调用成本看板、缓存、模型路由、mini GPT 初版
内容输出：成本优化实录 + mini GPT 学习日志

你的账号怎么分工

- 知乎：写长文，沉淀方法论。适合“AI 应用诊断清单”“Eval 方法”“项目复盘”。
- B站：做 8-15 分钟实操视频。适合录屏讲 script-killer 怎么改、怎么评测。
- YouTube：同 B站内容，可以标题更英文/技术化，积累全球技术受众。
- 抖音：做认知钩子和短案例。不要讲太深，讲一个问题、一个结论、一个画面。

最重要的输出模板
每学一个东西，都按这个模板输出：

我遇到的问题：
我原来以为：
课程/论文/文档告诉我：
我在 script-killer 里怎么验证：
结果是什么：
这个东西适合什么场景：
不适合什么场景：
下一步要做什么：

这会逼你从“看懂”进入“能判断”。

你现在最该开始的第一步：
用 7 天做一个 script-killer AI 质量诊断周报，哪怕很粗糙。只要你开始记录失败样本、原因、修复动作、评测结果，你就已经在进入 AI 应用层最核心的训练方式了。


---


我建议你的最高效路线是：**只围绕一个主项目学习，用输出倒逼输入**。

你的主项目可以先定成 `script-killer / AI 创作工作流` 或你现在工作里的 `agent-runtime / 意图识别 / DAU 分析`。不要同时开太多新项目。路线主线是：

> AI 应用交付 → Agent/RAG 诊断 → Eval 质量闭环 → 成本性能 → Transformer/LLM 底层

**核心原则**
1. 每周只学一个主题。
2. 每周必须改一个真实项目点。
3. 每周必须输出一篇文章或一个视频。
4. 不以“看完课”为目标，以“能解释、能验证、能复盘”为目标。

**0-3 个月路线**
第 1 个月：AI 应用与 Agent/RAG 基础

目标：你要能做出一个可用 AI workflow，并能解释每一步为什么存在。

学：
- Prompt / structured output
- Tool calling / function calling
- 简单 RAG
- Agent 的 plan、tool、memory、state、retry

课程：
- [Full Stack LLM Bootcamp](https://fullstackdeeplearning.com/llm-bootcamp/)
- [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction)

项目输出：
- 给你的 AI 工作流加 trace：输入、prompt、模型、输出、失败原因。
- 把一次生成失败拆成：输入问题、prompt 问题、模型问题、上下文问题、评测问题、用户偏好问题。

内容输出：
- 知乎：《AI 应用出错，为什么不能先怪模型》
- B站/YouTube：录一次“我如何拆解一个 Agent 工作流”
- 抖音：30 秒讲一个问题，比如“AI 结果太泛，通常是哪几层错了”

第 2 个月：Eval / 质量闭环

目标：你要能证明“这次改动真的变好了”。

学：
- golden set
- rubric
- LLM judge
- human preference
- regression eval
- prompt versioning
- failure taxonomy

项目输出：
- 做一个 `eval report`：每次 prompt 或流程改动前后对比。
- 建失败样本库：bad case、原因、修复动作、是否回归。
- 用户选择/编辑/丢弃都记录成 feedback event。

内容输出：
- 知乎：《AI 产品真正的壁垒不是 Prompt，而是 Eval》
- B站/YouTube：讲一次 before/after eval report
- 抖音：短视频讲“为什么 demo 好看不代表产品可用”

第 3 个月：成本、性能、模型路由

目标：你要能回答“为什么贵、为什么慢、怎么优化”。

学：
- input/output token
- prefill / decode
- KV cache
- batching
- streaming
- semantic cache
- model routing
- vLLM / SGLang 基础

课程/资料：
- vLLM 官方文档，重点看 serving、batching、prefix caching、metrics：[vLLM Docs](https://docs.vllm.ai/en/latest/getting_started/quickstart/)
- Hugging Face Learn 里也有 Agents、LLM、Context 等课程入口：[Hugging Face Learn](https://huggingface.co/learn)

项目输出：
- 记录每次模型调用：model、tokens、latency、cost、是否被采用。
- 简单任务用便宜模型，复杂任务用强模型。
- 相同输入加缓存。
- 长上下文压缩成 brief。

内容输出：
- 知乎：《一个 Agent 为什么贵？从 token、缓存、模型路由说起》
- B站/YouTube：做一次成本优化实录
- 抖音：讲“AI 应用省钱的 3 个办法”

**3-6 个月路线**
进入模型底层，但不要一上来 CS336。

目标：你要从“会用模型”变成“知道模型大概怎么学、怎么推理”。

学：
- Python / PyTorch
- tensor shape
- loss
- gradient descent
- backprop
- embedding
- attention
- tokenizer
- Transformer block

课程顺序：
1. [fast.ai Practical Deep Learning for Coders](https://course.fast.ai/)  
   适合先动手，不要求你先啃数学。
2. [Karpathy Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html)  
   从 micrograd、makemore 到 GPT，非常适合补底层直觉。
3. 3Blue1Brown 神经网络/线代系列  
   只做直觉补充，不当主线。

项目输出：
- 手写一个 mini GPT。
- 用短视频标题或业务 query 训练一个 toy model。
- 包成 API，让你的主项目可以调用它。
- 目标不是效果好，而是打通 tokenizer → model → decode → API。

内容输出：
- 知乎：《我从零写 mini GPT，终于理解 attention 在干嘛》
- B站/YouTube：录 tensor shape 流动过程
- 抖音：讲“Transformer 不是魔法，它每一步都在算什么”

**6-12 个月路线**
这时再碰硬核 LLM from scratch / 训练系统。

目标：你要能判断论文、框架、模型服务方案是不是解决真实问题。

学：
- tokenizer
- pretraining data
- optimizer
- distributed training
- GPU memory
- scaling law
- SFT / DPO / RLHF
- inference optimization

课程：
- [Stanford CS336: Language Modeling from Scratch](https://cs336.stanford.edu/)  
  这是硬课，官方 2026 页面已经有课程与作业资料。建议你 6 个月后再上，不要现在硬啃。

输出：
- 每月精读一篇论文/框架文档。
- 每篇只回答 5 个问题：解决什么问题、原瓶颈是什么、核心方法是什么、适合什么场景、不适合什么场景。

**每周节奏**
固定按这个来：

- 2 小时：看课
- 4 小时：改项目
- 1 小时：整理失败样本/评测结果
- 2 小时：写文章或录视频
- 30 分钟：复盘下周问题

**你的输出模板**
每次学习都按这个模板写：

```text
我遇到的问题：
我原来以为：
课程/文档告诉我：
我在项目里怎么验证：
结果是什么：
这个方法适合什么场景：
不适合什么场景：
下一步要做什么：
```

最关键的一句：**别把学习路线设计成“看课程”，要设计成“不断让项目变得更可诊断、更可评测、更可优化”。** 这样你会学得又深，又不会脱离真实工程。


---


可以，而且我觉得这件事应该和 AI 学习路线**绑死在一起**，不要单独开一个“英语学习计划”。最高效的方式是：

> 用英文输入学习 AI，用英文输出倒逼表达，再用中文做深度理解和复盘。

目标不是“学英语”，而是把英语变成你学习 AI、表达技术、做内容、参与全球社区的工作语言。

**总策略**
你每周学习 AI 的同时，固定做四件事：

1. **听**：听英文课程/技术视频。
2. **读**：读英文文档/论文/博客。
3. **说**：用英文复述你学到的东西。
4. **写**：把项目复盘写成英文短文。

不要追求一开始说得漂亮。先追求：**能准确表达技术判断**。

**每天 45-60 分钟英语嵌入法**
每天不用额外搞很重，按这个来：

```text
15 min 听：英文课程/YouTube，开英文字幕
15 min 读：官方文档/课程笔记/论文摘要
10 min 说：用英文复述今天学的内容
15 min 写：写 100-200 词英文学习日志
```

你的英文日志就用这个模板：

```text
Today I learned:
The problem I tried to solve:
My previous assumption was:
What I found:
How I tested it in my project:
What still confuses me:
Next step:
```

**和 AI 路线结合**
第 1 个月：Agent / RAG 英语表达

你要学会这些英文表达：
- retrieval
- reranking
- context window
- tool calling
- structured output
- hallucination
- failure mode
- trace
- fallback
- guardrail

输出任务：
- 每周写一篇英文短文：`Why my AI workflow failed`
- 每周录 3 分钟英文口播：解释一个 RAG/Agent 问题
- 中文再写一版深度复盘，保证理解不飘

第 2 个月：Eval 英语表达

重点词：
- evaluation
- golden set
- rubric
- regression
- LLM judge
- human preference
- false positive
- false negative
- quality loop
- benchmark

输出任务：
- 写英文 eval report。
- 录英文视频讲 before/after。
- 把中文技术文章改写成英文版，发 YouTube / X / Medium 都可以。

第 3 个月：成本性能英语表达

重点词：
- latency
- throughput
- input tokens
- output tokens
- prefill
- decode
- KV cache
- batching
- caching
- model routing
- cost reduction

输出任务：
- 英文讲一次：`Why this Agent is expensive`
- 写一篇：`How I reduced LLM cost in my AI workflow`
- 用英文解释一次你的项目架构图。

**每周固定输出**
建议你每周做一个“双语技术输出包”：

1. 中文长文：深度理解。
2. 英文短文：训练表达。
3. 英文 3-5 分钟视频：训练口语。
4. 英文术语卡片：训练词汇。
5. 中文复盘：记录哪里说不出来。

比如本周主题是 Eval，你的输出可以是：

```text
中文知乎：AI 产品真正的壁垒不是 Prompt，而是 Eval
英文短文：Why Evaluation Matters More Than Prompt Tweaking
英文视频：How I evaluate my AI workflow
术语卡：rubric / regression / golden set / failure mode
```

**口语怎么练**
最简单粗暴：

每天对着自己项目说 3 分钟英文。

不要背稿，按这个结构：

```text
I am working on...
The main problem is...
My current solution is...
The result is...
The next thing I want to improve is...
```

一开始卡很正常。卡住的地方就是你要补的表达能力。

你可以每次录音，然后让 AI 帮你改成更 native 的表达，但注意：不要只看修改结果，要总结自己的错误模式。比如：

- 中文直译太多
- 动词太弱
- 句子太长
- 技术名词不稳定
- 不会表达因果和权衡

**写作怎么练**
你不需要写雅思作文。你要练的是技术表达：

```text
Problem → Diagnosis → Experiment → Result → Lesson
```

英文技术写作最重要的是清楚，不是华丽。

推荐你每篇控制在 300-600 词。太长会拖垮节奏。

**输入材料怎么选**
只看英文一手资料，别过度看中文二创：

- 官方文档：OpenAI、Anthropic、Hugging Face、vLLM、LangChain、LlamaIndex
- 英文课程：Full Stack LLM Bootcamp、Hugging Face Agents Course、fast.ai、Karpathy
- YouTube：技术实操类，不要泛泛 AI 新闻
- 论文：先读 abstract、intro、figures、conclusion，不要硬啃全文

**最推荐你的组合**
你的路线可以变成：

> 白天/项目里用 AI 工程问题训练技术深度；晚上用英文复述这些问题训练 native-like 表达。

你最终要练成的不是“英语很好的人”，而是：

> 能用英文解释 AI 系统问题、讲清技术判断、写项目复盘、做英文技术内容的人。

第一步很简单：从今天开始，每天写一段英文：

```text
Today I worked on an AI learning roadmap.
The key idea is to learn through real projects instead of only watching courses.
I want to build the habit of learning, building, evaluating, and explaining in English.
```

这条线走 3 个月，你的英文会明显从“学科英语”变成“工作英语”。走 6-12 个月，就会开始接近技术创作者/工程师的自然表达。

---

下面这份按你的路线筛过：**少而精，长期跟，边学边输出**。

**一、核心课程**
按顺序来，不要同时开太多。

1. [Full Stack LLM Bootcamp](https://fullstackdeeplearning.com/llm-bootcamp/)  
   用来建立 LLM 应用全局观：Prompt、RAG、LLMOps、UX、部署。

2. [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction)  
   主攻 Agent：tools、actions、observations、workflow、benchmark。

3. [DeepLearning.AI - Retrieval Augmented Generation](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)  
   系统学 RAG：retriever、vector DB、evaluation。

4. [DeepLearning.AI - Building and Evaluating Advanced RAG](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag/)  
   学高级 RAG 和评测方法，适合接你的 Eval 路线。

5. [DeepLearning.AI - Evaluating AI Agents](https://www.deeplearning.ai/courses/evaluating-ai-agents/)  
   主攻 Agent eval，这是你要形成壁垒的一层。

6. [fast.ai Practical Deep Learning for Coders](https://course.fast.ai/)  
   补深度学习基础，适合先实践后理论。

7. [Karpathy Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html)  
   从 micrograd、makemore 到 GPT，补模型底层直觉。

8. [Stanford CS336: Language Modeling from Scratch](https://cs336.stanford.edu/)  
   6 个月后再啃。官方页面是 Spring 2026，覆盖从 tokenizer、Transformer、训练到系统优化。

**二、AI 最新资讯源**
每周固定看一次就够。

1. [OpenAI News](https://openai.com/news/)  
   看模型、产品、研究发布。

2. [OpenAI Developer Blog](https://developers.openai.com/blog)  
   更适合工程实践：API、Agents、Codex、Apps SDK、Realtime。

3. [Anthropic News](https://www.anthropic.com/news)  
   看 Claude、Agent、安全、企业应用方向。

4. [Google DeepMind Blog](https://deepmind.google/blog/)  
   看前沿模型、Agent safety、多模态、科学 AI。

5. [Google Research Blog](https://research.google/blog/)  
   偏研究和工程结合。

6. [Hugging Face Blog](https://huggingface.co/blog)  
   重点看开源模型、Agents、Evaluation、Transformers、PEFT、LoRA、推理实践。

7. [Hugging Face Learn](https://huggingface.co/learn)  
   课程和实践资料入口，适合持续补课。

8. [vLLM Blog / Docs](https://docs.vllm.ai/)  
   跟推理服务、batching、prefix caching、serving、metrics。

9. [SGLang Docs](https://docs.sglang.ai/)  
   跟高性能 serving、低延迟、高吞吐、RadixAttention、prefix caching。

**三、论文与论文源**
你的目标不是“每天读论文”，而是每周筛 2-3 篇，精读 1 篇。

1. [arXiv cs.CL recent](https://arxiv.org/list/cs.CL/recent)  
   NLP、LLM、RAG、Agent、Evaluation 主阵地。

2. [arXiv cs.AI recent](https://arxiv.org/list/cs.AI/recent)  
   Agent、规划、推理、AI 系统相关。

3. [arXiv cs.LG recent](https://arxiv.org/list/cs.LG/recent)  
   机器学习、训练、优化、模型方法。

4. [Hugging Face Daily Papers](https://huggingface.co/papers)  
   最适合你日常筛论文，有社区热度。

5. [Hugging Face Trending Papers](https://huggingface.co/papers/trending)  
   看近期社区关注什么。

6. [Papers with Code](https://paperswithcode.com/)  
   查论文是否有代码、benchmark、SOTA 对比。

7. [Stanford CS336 Lectures GitHub](https://github.com/stanford-cs336/lectures)  
   不是普通论文源，但很适合系统性补 LLM from scratch。

**四、你重点关注的论文方向**
别什么都看，先盯这 7 类：

1. Agent workflow：planning、tool use、memory、multi-agent。
2. RAG：query rewriting、reranking、hybrid search、GraphRAG、context packing。
3. Eval：LLM judge、golden set、agent benchmark、RAG evaluation。
4. Context engineering：context compression、long context、memory、state management。
5. Inference：KV cache、batching、speculative decoding、prefix caching、serving。
6. Small models / routing：SLM、distillation、model routing、cheap model + strong model。
7. AI coding agents：code generation agent、autonomous dev loop、PR automation。

**五、每周固定输入节奏**
建议你这样排：

```text
周一：看 OpenAI / Anthropic / DeepMind / HF 最新动态
周二：学一节课程
周三：读 1 篇论文摘要 + intro + conclusion
周四：把一个点接到项目里
周五：写中文复盘
周六：写英文短文或录英文讲解
周日：整理下周要验证的问题
```

**六、英文输出绑定**
每周至少产出一个英文小东西：

```text
This week I learned:
The problem I investigated:
The key idea from the paper/course:
How I tested it in my project:
What I still don't understand:
```

你真正要长期关注的不是“更多资源”，而是这条主线：**Agent/RAG → Eval → Observability → Inference Cost → Transformer 底层**。这条线和你的项目、工作、英文输出都能接起来。

---

合理，但要微调：你原来的列表方向是对的，问题是 **DeepLearning.AI 短课偏碎、偏入门；CS336 太硬；RAG/Agent 最好靠项目补深度**。社区里更公认的“硬通货”大概是下面这套。

**结论版**
你的主线建议定成：

1. **Full Stack LLM Bootcamp**：建立 AI 应用工程全局观  
2. **Hugging Face Agents Course + HF LLM Course**：补 Agent、Transformers、开源生态  
3. **fast.ai**：先把深度学习跑起来  
4. **Karpathy Zero to Hero**：补神经网络/Transformer 底层直觉  
5. **Sebastian Raschka《Build a Large Language Model From Scratch》**：作为 Karpathy 到 CS336 的桥  
6. **Stanford CS336**：6 个月后再啃，做作业才有价值  
7. **vLLM / SGLang 官方文档**：补推理系统和成本性能

**最推荐主线课程**
1. [Full Stack LLM Bootcamp](https://fullstackdeeplearning.com/llm-bootcamp/)  
   适合你第一阶段。它不是最底层，但很适合建立 LLM App、RAG、LLMOps、部署、UX 的工程全景。

2. [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction)  
   Agent 入门和实践路线不错，尤其适合你做 workflow、tool use、evaluation。

3. [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter1/1)  
   社区里一直有人推荐 HF 生态，因为它直接接 Transformers、Datasets、Tokenizers、Accelerate，适合从应用走向模型工程。

4. [fast.ai Practical Deep Learning for Coders](https://course.fast.ai/)  
   社区评价很稳定：适合“先做出来”。有人总结得很准：fast.ai 更适合 getting stuff done，Karpathy 更适合 deep understanding。

5. [Karpathy Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html)  
   非常推荐。社区里经常把它作为理解 backprop、makemore、GPT、tokenizer 的经典路线。你要补底层直觉，这个比直接啃论文友好很多。

6. [Build a Large Language Model From Scratch](https://www.manning.com/books/build-a-large-language-model-from-scratch)  
   Sebastian Raschka 这本书很适合作为 Karpathy 和 CS336 中间层。社区里也有人提到它是 CS336 的不错预备材料。

7. [Stanford CS336](https://cs336.stanford.edu/)  
   这是公认硬课。官方定位就是从数据清洗、Transformer、训练、评测到部署，完整走一遍语言模型构建流程。社区反馈也一致：很强，但不是纯新手课；真正价值在 assignments，不是只看视频。

**DeepLearning.AI 怎么看**
可以学，但我会把它降级成“补丁课”，不是主线。

适合用来快速补：
- RAG
- Agent evaluation
- LLMOps
- function calling
- prompt engineering

不适合作为你的主线，因为很多短课太短，容易让人“听懂了但做不深”。你可以在项目遇到具体问题时查一门短课，比如要做 RAG eval，就看 RAG/evaluation 相关短课。

**CS336 什么时候上**
不要现在上。

更合理顺序是：

```text
Full Stack LLM Bootcamp
→ Hugging Face Agents / LLM Course
→ fast.ai
→ Karpathy Zero to Hero
→ Raschka LLM from Scratch
→ Stanford CS336
```

社区里对 CS336 的典型反馈是：课很好，但 ramp up 很快；最好先有基础 LLM 知识、PyTorch、Transformer 直觉。还有人强调 CS336 的重点是作业，例如 tokenizer、LLM from scratch、FlashAttention、DDP 这些，光看课不够。

**你应该避开的坑**
1. 不要买一堆 Udemy “2026 AI Engineer Bootcamp”。质量参差，很多只是 LangChain demo。
2. 不要一开始就上 CS336，会被作业劝退。
3. 不要只看 DeepLearning.AI 短课，会缺少深度项目。
4. 不要追 20 个框架。LangChain、LlamaIndex、DSPy、CrewAI、AutoGen 都知道名字即可，先把一个 workflow 做深。
5. 不要把论文当主线。前 3 个月论文只读摘要和结论。

**我给你的最终课程表**
第 1 阶段，0-2 个月：AI 应用工程  
- Full Stack LLM Bootcamp  
- Hugging Face Agents Course  
- DeepLearning.AI RAG / Agent Eval 短课按需补

第 2 阶段，2-4 个月：Eval、RAG、Agent 诊断  
- HF Agents Course 做完作业  
- LlamaIndex / LangChain 官方文档只看 RAG eval、trace、tool calling 部分  
- 用你的项目做 failure taxonomy、eval report、trace

第 3 阶段，4-6 个月：深度学习和模型底层  
- fast.ai  
- Karpathy Zero to Hero  
- 3Blue1Brown 神经网络/线代做直觉辅助

第 4 阶段，6-9 个月：LLM from scratch  
- Raschka《Build a Large Language Model From Scratch》  
- nanoGPT / makemore 复现  
- 自己训练 toy GPT

第 5 阶段，9-12 个月：硬核系统  
- Stanford CS336  
- vLLM Docs  
- SGLang Docs  
- GPU Mode lectures 可选

这套是比较稳的：既符合社区公认质量，也贴合你的目标：**不是成为课程收藏家，而是成为能构建、诊断、评测、优化 AI 系统的人。**


---


你要把 AI 当成 **学习教练 + 陪练 + 质检员 + 输出编辑**，而不是当成“答案生成器”。最高效的用法是：让 AI 帮你把输入变成问题，把问题变成项目验证，把验证变成输出。

我建议你固定用这套闭环：

```text
输入资料 → AI 帮你拆解 → 你复述 → AI 追问 → 项目验证 → 双语输出 → AI 批改
```

**1. 学之前：让 AI 帮你建立地图**
看课程/论文/文档前，不要直接扎进去。先把标题、目录、摘要丢给 AI，让它帮你回答：

```text
请帮我用工程师视角预习这份内容：
1. 它解决什么问题？
2. 前置知识有哪些？
3. 我应该重点关注哪些概念？
4. 哪些内容可以先跳过？
5. 学完后我应该能做出什么小项目？
```

这样你不是“被动看课”，而是带着问题进去。

**2. 学的时候：让 AI 做逐段解释，但别让它替你总结**
每学一小节，就让 AI 用三层解释：

```text
请用三层方式解释这个概念：
1. 一句话直觉
2. 工程例子
3. 和我的 AI workflow / RAG / Agent / Eval 项目的关系
```

比如学 `KV cache`，不要只问“KV cache 是什么”，要问：

```text
KV cache 为什么会影响 Agent 成本和延迟？
如果我的 workflow 有多轮上下文，它可能在哪些地方浪费计算？
```

**3. 学完后：强制自己复述，让 AI 挑错**
这是最关键的。你不要让 AI 总结，而是你先写一版自己的理解，然后让 AI 挑错。

```text
下面是我对 RAG eval 的理解。请你像严格导师一样检查：
1. 哪些地方理解错了？
2. 哪些地方太模糊？
3. 哪些概念被我混在一起了？
4. 请用问题继续追问我，直到确认我真的懂了。
```

你会发现，真正学会不是“看懂”，而是“被追问还能说清楚”。

**4. 用 AI 生成练习题，而不是生成答案**
每学一个主题，让 AI 给你出题：

```text
围绕 Agent evaluation，给我 10 个从易到难的问题。
要求：
- 不能是定义题
- 必须结合真实 AI 应用场景
- 每题后面先不要给答案
- 等我回答后再批改
```

这会比刷课程有效很多。

**5. 把每个知识点绑定到项目验证**
你每学一个东西，都问 AI：

```text
我正在做一个 AI workflow 项目。
请把这个知识点转成一个最小可验证实验：
1. 要改哪里
2. 记录什么指标
3. 怎么判断有效
4. 可能出现什么反例
```

比如学 `model routing`，项目实验就是：

```text
简单任务用便宜模型，复杂任务用强模型。
记录 success rate、latency、cost、用户采纳率。
```

这样知识会落地，不会飘。

**6. 用 AI 帮你做英文陪练**
你想练 native English，这里非常适合。

每天学完后，用英文说 2-3 分钟，然后把文字稿给 AI：

```text
Please act as my native English technical communication coach.
Improve my explanation to sound natural but still like an engineer.
Do three things:
1. Correct grammar and awkward phrasing.
2. Rewrite it in natural technical English.
3. List 5 reusable phrases I should memorize.
```

你也可以让它追问你：

```text
Ask me 5 follow-up questions in English about this concept.
After I answer, correct my technical English and my reasoning.
```

**7. 固定一个“AI 学习笔记模板”**
每次学习都让 AI 帮你整理成这个结构：

```text
Topic:
Why it matters:
My previous misunderstanding:
Core idea:
Concrete example:
How I tested it:
Result:
Open questions:
English phrases:
Content idea:
```

这个模板特别适合你之后发知乎、B站、YouTube。

**8. 每周让 AI 做一次学习审计**
每周末，把你这周笔记、代码改动、输出内容丢给 AI：

```text
请审计我这一周的学习：
1. 我真正掌握了什么？
2. 哪些只是看过但没消化？
3. 哪些概念之间还没连起来？
4. 下周最应该补哪 3 个问题？
5. 给我设计一个项目实验和一个英文输出题目。
```

这一步能防止你“看了很多，但没有长进”。

**你最该避免的 AI 用法**
不要这样用：

```text
帮我总结这节课
帮我解释这篇论文
帮我列学习路线
```

这些太被动。

要改成：

```text
先问我 5 个问题，确认我理解到什么程度
基于我的项目，设计一个实验
检查我的理解哪里错了
把这个概念变成英文技术表达训练
```

一句话：**AI 不该替你学习，它应该逼你暴露理解漏洞。**

你真正要形成的习惯是：

```text
每学一个东西：
我先讲 → AI 挑错 → 我修改 → 项目验证 → 英文输出
```

这套跑起来，你会比单纯看课快很多，而且学得更深。