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
- `postclose_review` 需要 execution records 的真实回流
- `nightly_improvement` 需要评分、工单、审批链
- Discord / n8n 在部署环境中的真实联调

## 这轮新增内容

为支持你专注 `soul` 和 `skill` 内容建设，这轮优先补了框架层：

- `configs/souls/departments/` 与 `configs/souls/specialists/`
- `skills/<skill_name>/manifest.yaml` 与 `prompt.md`
- `libs/contracts` 新增 registry / research / strategy / trading contracts
- `libs/registry` 实现两层 soul 继承与 skill 绑定解析
- `soul_versions`、`research_reports`、`strategies`、`trading_plans`、`execution_records` 数据对象与迁移
- `/v1/registry/*`、`/v1/research-reports/*`、`/v1/strategies/*`、`/v1/trading-plans/*`

## 你可以并行做的内容

从现在开始，你可以主要在这些目录里迭代内容，不需要再等框架代码：

- `configs/souls/departments/`
- `configs/souls/specialists/`
- `skills/*/manifest.yaml`
- `skills/*/prompt.md`

建议优先顺序：
- 把三个部门 soul 写厚：国务院、国家统计局、中央军委
- 把三个专员 soul 写细：情报专员、议案专员、计划专员
- 先把 4 个核心 skill prompt 打磨到可用：`news_parse_skill`、`proposal_draft_skill`、`strategy_synthesis_skill`、`plan_generation_skill`

## 下次到部署环境要做的事

- 验证 `MiniMax` 真实联网与代理
- 导入 n8n workflow 并跑一次 `intel_update` / `daily_preopen`
- 用 Discord 验证 slash command 联通和频道限制
- 决定 `intraday_watch` 的实时数据接入方式
- 决定 execution record 的采集入口，为 `postclose_review` 铺路
