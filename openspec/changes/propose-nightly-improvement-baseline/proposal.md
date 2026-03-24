## Why

`nightly_improvement` 目前仍然是 blocked，因为系统还没有稳定的评分输入、ticket 产物和审批流。没有这一层，前面已经跑起来的 proposal、planning、review 链路就无法形成真正的自我改进闭环。

## What Changes

- 定义 nightly improvement baseline 所需的评分输入与聚合范围。
- 定义 improvement ticket 的标准 contract 和状态流转。
- 定义最小审批流程，让 nightly improvement 结果不会直接未经治理地影响运行时行为。
- 为后续实现准备 OpenSpec specs、design 和 tasks。

## Capabilities

### New Capabilities
- `nightly-improvement-baseline`: 定义 nightly improvement 的输入、处理和输出基线。
- `improvement-ticket-contract`: 定义标准化 improvement ticket。
- `improvement-approval-flow`: 定义 baseline 审批与状态流转。

### Modified Capabilities

None.

## Impact

受影响范围包括 `apps/evaluation_service` 与 `apps/agent_core` 的后续 nightly flow、`libs/contracts` 与 `libs/db` 的 score/ticket 对象、`configs/departments` 中 improvement specialist 的职责，以及 future scheduler / n8n nightly orchestration。
