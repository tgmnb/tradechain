# 2026-03-13 进度核对与后续规划

## 当前进度

对照 [ai投研agent系统项目说明书_v_1.md](D:/experiment/tradechain/ai投研agent系统项目说明书_v_1.md) 看，当前仓库已经完成了阶段 1 的骨架搭建，并把阶段 2 的一部分闭环真正落到了代码里。

已完成：
- 基础基础设施：`docker-compose`、PostgreSQL、Redis、MinIO、Qdrant、n8n、6 个 Python 服务
- 第一条可运行主链：`intel_update`，即 `事件 -> proposal -> archive`
- Discord 到 API 的最小联通
- `MiniMax` provider 接入，保留 `heuristic` 作为离线 fallback
- `soul + skill` 的文件源框架、registry loader、DB projection、只读 registry API
- 第二条可运行主链：`daily_preopen`，即 `proposal -> research_report -> strategy -> trading_plan`
- `major_task` 复用同一套 proposal/planning 管线

仍未实装：
- `intraday_watch` 需要实时行情和触发逻辑
- `nightly_improvement` 需要评分、工单、审批链
- Discord / n8n 在部署环境中的真实联调

已补到 baseline：
- `postclose_review` 已具备最小可运行复盘链，能够基于 `trading_plan + execution_records` 生成结构化 review 并归档

## 当前交付波次

基于当前仓库状态，后续不再适合继续沿用最早的 Sprint 1 / Sprint 2 说法，更准确的划分是三段交付波次：

- Wave 1 `基线已跑通`
  - 包含：`intel_update`、`daily_preopen`、`major_task`、`policy_watch`、politburo direct reply
  - 判定标准：本地/开发环境能跑通最小链路，有明确 API 或 bot 入口
- Wave 2 `工作流补全`
  - 目标：补齐 `intraday_watch`、`postclose_review`、`nightly_improvement`
  - 判定标准：不是只有入口，而是具备真实输入、真实输出和可复用链路
- Wave 3 `平台加固`
  - 目标：为已可运行链路补齐 smoke / integration coverage、可观测性、部署校验和数据回流
  - 判定标准：可以在接近生产的环境下重复验证，而不是仅靠本地人工试跑

## Workflow Readiness 重新归类

按“是否真正可运行”而不是“是否已有 endpoint / placeholder”重新看，当前状态应当是：

- `intel_update`：runnable
- `daily_preopen`：runnable
- `major_task`：runnable baseline
- `policy_watch`：runnable baseline
- `intraday_watch`：partial
- `postclose_review`：runnable baseline
- `nightly_improvement`：blocked

对应缺口：

- `intraday_watch`
  - 缺实时行情源
  - 缺触发与节流逻辑
- `postclose_review`
  - 仍缺 execution record 的真实自动采集入口
  - 当前 review graph 仍是 baseline heuristic，总结与评分还不够深
- `nightly_improvement`
  - 缺评分数据
  - 缺工单生成链
  - 缺审批闭环

其中 `intraday_watch` 和 `nightly_improvement` 仍不能算作“已交付”；`postclose_review` 则已经进入可运行 baseline，但还没到生产级。

## 这轮新增内容

为支持你专注 `soul` 和 `skill` 内容建设，这轮优先补了框架层：

- `configs/departments/<department_id>/soul.yaml`
- `configs/departments/<department_id>/skills/<skill_name>/manifest.yaml`
- `configs/departments/<department_id>/specialists/<specialist_id>/soul.yaml`
- `configs/departments/<department_id>/specialists/<specialist_id>/skills/<skill_name>/manifest.yaml`
- `libs/contracts` 新增 registry / research / strategy / trading contracts
- `libs/registry` 实现两层 soul 继承与 skill 绑定解析
- `soul_versions`、`research_reports`、`strategies`、`trading_plans`、`execution_records` 数据对象与迁移
- `/v1/registry/*`、`/v1/research-reports/*`、`/v1/strategies/*`、`/v1/trading-plans/*`

## 你可以并行做的内容

从现在开始，你可以主要在这些目录里迭代内容，不需要再等框架代码：

- `configs/departments/`

建议优先顺序：
- 把三个部门 soul 写厚：国务院、国家统计局、中央军委
- 把三个专员 soul 写细：情报专员、议案专员、计划专员
- 先把 4 个核心 skill prompt 打磨到可用：`news_parse_skill`、`proposal_draft_skill`、`strategy_synthesis_skill`、`plan_generation_skill`

## 2026-03-14 内容层补强

这一轮已经把上述优先项推进到第一版“可用于运行时提示”的水平：

- 三个部门 soul 已补齐更具体的 `mission / responsibilities / focus / guardrails / style_notes`
- 三个专员 soul 已补齐链路内角色边界、输入输出偏好和更细的约束
- 另外新增了 `watch_officer / review_officer / improvement_officer`，把 `intraday_watch / postclose_review / nightly_improvement` 预留链路挂到明确 specialist
- 4 个核心 skill prompt 已从短模板升级为结构化指导，包含建议输出结构和保守退让策略
- 另外补入了 `market_scan_skill`、`commodity_logic_skill`、`execution_compare_skill`、`improvement_ticket_skill` 这 4 个后续链路所需的预备 skill
- registry 目录结构已改成“每个部门一个文件夹，部门内含 soul/skills/specialists，专员默认继承部门 skill，再叠加自己的 skill”
- registry 回归测试已补，确保这些 richer prompt 能实际进入 resolved runtime profile

下一步更适合继续推进的方向：

- 针对 `intraday_watch` 设计新的部门/专员组合或扩充现有 soul 的实时监控职责
- 为 `postclose_review` 与 `nightly_improvement` 补充复盘型 skill
- 在真实样本上校准 4 个核心 skill 的输出长度、字段稳定性和中文风格

## 下次到部署环境要做的事

- 验证 `MiniMax` 真实联网与代理
- 导入 n8n workflow 并跑一次 `intel_update` / `daily_preopen`
- 用 Discord 验证 slash command 联通和频道限制
- 决定 `intraday_watch` 的实时数据接入方式
- 决定 execution record 的采集入口，为 `postclose_review` 铺路

## 2026-03-14 本地联调补充

这轮又补了几项“真正能跑”的东西，重点不是新框架，而是把现有链路在当前机器上打通：

- 新增一键脚本：`scripts/install_local.sh`、`scripts/start_local.sh`
- `start_local.sh` 会自动起 compose、跑迁移、在配置了 token 时拉起 Discord bot，并执行最小 smoke check
- Discord bot 不再只有 slash command，普通频道消息也会进顶层 politburo agent
- 顶层 politburo agent 现在有两类稳定行为：
  - 直接回复：`help`、`你是谁`、`你能做什么`、健康查询、最新提案查询
  - 任务分拣：研究/分析/提案类请求会升级到 `intel_update`
- `MiniMax` 结构化解析补了 `<think>` 清洗和首个合法 JSON 提取，避免模型前置思考文本把结果打坏
- API 内部调用超时补成了兼容配置，避免 planning 链在 `daily_preopen` 上提前超时

当前本地可视为已验证或已补到 baseline 的内容：

- `intel_update`
- `daily_preopen`
- `politburo direct reply`
- `Discord plain message -> politburo -> direct reply / intel_update`
- `execution_record intake -> postclose_review baseline review`

## 2026-03-24 postclose review baseline 补口

为继续推进 `postclose_review`，这轮把占位链路补到了 baseline 可运行状态：

- `execution_records` 现在带最小 `evidence_source` 字段，可区分手工录入和未来自动回流
- `review_graph` 已从 placeholder 升级为最小可运行节点链
- `postclose_review` 现在会产出结构化 review payload，写入 review 记录，并归档 review payload
- 测试已补到“无 evidence 阻塞”和“有 evidence 生成 review”的路径

这意味着当前真正还缺的不是“有没有入口”，而是：

- execution record 的真实自动采集来源
- 更深入的 review 比较逻辑和评分标准
- nightly evaluation / approval 数据链
