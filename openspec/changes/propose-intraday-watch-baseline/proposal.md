## Why

`intraday_watch` 仍停留在 blocked 状态，核心原因不是没有入口，而是缺少可控的行情输入、触发规则和标准化观察输出。继续拖下去会让日内监控长期停留在“概念已存在、运行能力缺失”的状态。

## What Changes

- 定义 `intraday_watch` baseline 所需的行情输入形态，优先支持 mock-replay 或单一真实源。
- 定义日内触发规则和节流要求，避免把 watch 逻辑做成无约束轮询。
- 定义标准化的 watch observation / alert 输出 contract，便于后续接 Discord、n8n 或研究链路。
- 为后续实现准备 OpenSpec specs、design 和 tasks。

## Capabilities

### New Capabilities
- `intraday-watch-baseline`: 定义日内观察链路的输入、处理和输出基线。
- `market-watch-triggering`: 定义触发条件、节流和去重要求。
- `watch-observation-contract`: 定义标准化观察结果和 alert 输出。

### Modified Capabilities

None.

## Impact

受影响范围包括 `apps/api_service` 的 workflow 入口、`apps/agent_core` 的 future watch graph、`libs/contracts` 的 watch 相关 contract、`configs/departments` 中 watch specialist 的角色约束，以及 `workflows/langgraph` / `workflows/n8n` 的调度接入方式。
