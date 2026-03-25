## Context

当前仓库已经为 `intraday_watch` 预留了 specialist、skill 和 workflow 入口，但入口仍直接返回 blocked。这个链路的主要难点不在 LLM，而在输入源、触发逻辑和输出对象。如果这些对象没有先收敛，后续实现容易变成把任意行情轮询和任意文本提醒拼在一起。

## Goals / Non-Goals

**Goals:**
- 明确 intraday watch baseline 的输入源约束。
- 明确触发规则、节流、去重的最小要求。
- 明确 watch observation / alert 的标准输出。

**Non-Goals:**
- 本 change 不接入真实 broker。
- 本 change 不实现自动交易。
- 本 change 不解决所有市场数据接入方案。

## Decisions

### 1. Baseline 优先支持 mock-replay 或单一真实源
先把 watch 做成可控输入驱动的链路，而不是一开始支持多源行情聚合。

Rationale:
- 真实多源行情会放大接入、授权、时间戳、去重复杂度。
- baseline 目标是先验证 watch contract 和触发规则。

Baseline implementation choice:
- 第一版只执行 `mock_replay` 输入模式。
- 请求方必须显式传入受控的 market snapshots；真实单源行情保留为后续扩展能力，而不是 baseline 依赖。

Minimum required market fields:
- `asset`
- `observed_at`
- `last_price`
- `prev_close`
- `session_high`
- `session_low`
- `volume`
- `average_volume`

### 2. 触发规则必须包含节流与去重
watch 不仅要定义“何时触发”，也要定义“多久不重复报同类触发”。

Rationale:
- 没有节流的 watch 很容易把 Discord / n8n 或研究链打爆。
- 去重是把日内观察变成可用信号的前提。

Baseline trigger rules:
- `price_breakout`: `abs((last_price - prev_close) / prev_close) * 100 >= 2.0`
- `volatility_expansion`: `((session_high - session_low) / prev_close) * 100 >= 3.0`
- `volume_spike`: `volume / average_volume >= 2.0`

Throttle and dedup baseline:
- suppression window 默认 `15` 分钟
- dedup key 由 `asset + trigger_type + direction_or_bucket` 组成
- 同一 suppression window 内重复命中同类 trigger 时，返回 suppressed 记录而不是再次发 observation

### 3. 输出先做 observation / alert，不直接推进交易
watch 输出应当先成为可复用观察结果，再决定是否触发下游研究或策略。

Rationale:
- 当前平台还没有足够强的 execution 风控闭环。
- observation contract 比“自动下一步动作”更稳定、更适合后续组合使用。

Observation contract baseline fields:
- object identity: `id`, `chain_type`, `schema_version`, `created_at`
- market scope: `asset_scope`, `source`, `observed_at`
- trigger semantics: `trigger_type`, `severity`, `summary`, `dedup_key`
- evidence: percentage change, range, volume ratio, threshold snapshot
- routing: `follow_up_action`, `routing_targets`
- extensibility: `task_id`, `metadata`

## Risks / Trade-offs

- [mock-replay 与真实市场差异大] -> Mitigation: baseline 只验证接口与触发行为，不把 mock 成功等同于生产 readiness。
- [触发规则过少导致价值有限] -> Mitigation: baseline 先覆盖价格/波动/成交量三类典型触发。
- [输出过宽泛难以下游消费] -> Mitigation: 输出 contract 只保留 observation / alert 必需字段。

## Migration Plan

1. 定义 intraday watch 的 specs 与 contract。
2. 实现 mock-replay 或单一真实源输入适配。
3. 实现 watch graph baseline。
4. 再把结果接到 Discord、n8n 或研究链路。

## Open Questions

- 第一真实行情源应选哪一个，HTTP 轮询还是 websocket？
- 触发配置应存于 registry、数据库，还是 workflow metadata？
