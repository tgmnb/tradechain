## Why

当前仓库已经完成了 baseline workflow 与基础设施的可运行性验证，但用户实际感知最强的主入口仍然停留在“关键词分流 + 粗糙检索 + workflow 回显”层面，这与 [AI投研Agent系统项目说明书](/home/tgm/project/tradechain-codex-0314/docs/ai投研agent系统项目说明书_v_1.md) 中要求的治理结构、结构化输出、审议流程、归档追溯和持续评估相差很远。下一阶段不应该继续横向铺更多 placeholder，而应该先把一个最核心、最常用、最容易被用户直接评价的链路做深、做稳、做像设计书要求的“智能投研中枢”。

## What Changes

- 把“总书记输入 -> 中央政治局澄清 -> 国务院研究/汇总 -> 书记处留档 -> 对用户回复”定义为下一阶段的核心单链路，而不是继续以 `web_research` 风格的临时链路承接自然语言请求。
- 定义该链路所需的 runtime 基建，包括结构化任务/证据/结论对象、trace 与版本留痕、来源治理、失败回退和可复盘记录。
- 定义面向对话质量的评测基线，使路由正确性、检索相关性、结构化输出完整性和最终回复可用性成为可验证门槛，而不是人工凭感觉判断。
- 明确后续扩展策略：先把这条核心链路做成模板，再将同样的治理/评测/归档机制复制到盘前、盘中、盘后与夜间链路。

## Capabilities

### New Capabilities
- `governed-dialogue-chain`: 定义面向用户的正式对话主链，覆盖意图澄清、研究分派、结构化结论与最终答复。
- `dialogue-runtime-foundation`: 定义支撑主链的运行时基建，包括 trace、版本、证据、归档、失败回退和结构化对象。
- `dialogue-quality-evaluation`: 定义对话主链的评测数据、评分维度和回归门槛。

### Modified Capabilities
- `workflow-readiness`: 增加“正式对话主链”作为下一阶段 readiness 的关键判定对象，而不是仅按 workflow route 存在与否判断。
- `platform-hardening`: 增加对话链的来源治理、回放复盘和质量评测要求。

## Impact

受影响范围将包括 `apps/api_service` 的 politburo / agent 入口与 workflow hand-off、`apps/agent_core` 的主控图与部门子图接口、`apps/archive_service` 的书记处式归档落点、`libs/contracts` 与 `libs/db` 的结构化对象、Discord 与 n8n 的入口与审批/通知方式、`configs/departments` 中政治局/国务院/书记处/中纪委/中组部相关 soul 与 skill，以及回归测试与评测样本体系。
