## Why

`postclose_review` 现在只有入口和 placeholder hand-off，距离可用的复盘链路还差一层真正可消费的 evidence、review 输出和最小 graph 实现。这个缺口会直接阻塞后续的 nightly improvement，因为系统还没有稳定的“计划 vs 执行 vs 复盘”结构化产物。

## What Changes

- 为 `postclose_review` 定义可执行的 baseline capability，而不是只保留 placeholder graph。
- 约束 execution evidence 的最小字段和来源信息，使 review 可以基于真实记录运行。
- 定义 review 输出 contract，使结果可持久化、可归档、可供后续 improvement 消费。
- 将 `review_graph` 升级为最小可运行节点链，支持从 trading plan 和 execution records 生成 review 结果。

## Capabilities

### New Capabilities
- `postclose-review-baseline`: 定义 postclose review 的输入、处理和输出基线。
- `execution-evidence`: 定义可供 review 消费的 execution evidence 最小约束。
- `review-output-contract`: 定义结构化 review 结果的标准输出。

### Modified Capabilities

None.

## Impact

受影响范围包括 `apps/api_service` 的 review/execution 入口、`apps/agent_core` 的 `review_graph`、`libs/contracts` 的 trading/review contract、`libs/db` 的 review 相关模型与持久化路径，以及 `workflows/langgraph/review_graph` 的实现说明。
