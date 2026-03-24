## Context

当前仓库已经有 `trading_plan`、`execution_records` API，以及 `postclose_review` 的占位调用路径，但 review graph 本身没有节点实现，也没有稳定的 review 输出对象。这意味着系统可以“进入复盘流程”，却无法产出对人和后续流程都真正有用的复盘结果。

## Goals / Non-Goals

**Goals:**
- 让 `postclose_review` 从 placeholder 升级为最小可运行链路。
- 明确 execution evidence 的最小约束，避免 review 直接消费松散自由文本。
- 输出结构化 review 结果，供 archive 和 improvement 复用。

**Non-Goals:**
- 接入真实 broker 或 OMS。
- 构建完整评分/审批体系。
- 在本 change 中实现 nightly improvement。

## Decisions

### 1. 先做 baseline review，不直接做完整复盘系统
本 change 只交付单计划级别、单次或小批量 execution evidence 的 review 结果。

Rationale:
- 当前最缺的是稳定的数据闭环，不是复杂评估逻辑。
- 先有结构化 review，后续 improvement 才有可靠输入。

Alternatives considered:
- 直接做 review + improvement 全链。拒绝，范围过大且依赖更多未稳定对象。

### 2. 将 execution evidence 视为 review 的前置约束
review graph 只消费满足最小约束的 execution evidence，而不是任意备注。

Rationale:
- 没有来源、动作类型、结果字段的记录无法稳定比较计划与执行。
- 这能让 review graph 的节点逻辑保持简单可测。

Alternatives considered:
- 让 graph 自己清洗任意输入。拒绝，会让 graph 变成脆弱的容错层。

### 3. review 输出先以结构化 contract 为核心
最小输出应覆盖结论摘要、主要偏差、风险/问题、后续建议和元数据。

Rationale:
- 复盘结果需要可入库、可归档、可被 improvement 消费。
- 比起一段自然语言，contract 更能稳定驱动后续流程。

Alternatives considered:
- 先只输出 markdown 文本。拒绝，因为后续链路无法稳定消费。

## Risks / Trade-offs

- [execution evidence 约束过严导致难以上线] -> Mitigation: 先定义最小必填字段，只卡住 review 必需信息。
- [review 输出设计过早冻结] -> Mitigation: baseline contract 保持紧凑，扩展字段通过 metadata 增量演进。
- [graph 逻辑过于简单] -> Mitigation: 接受 baseline 版本只做最小比较和总结，把复杂评分留到 nightly improvement。

## Migration Plan

1. 定义 execution evidence 和 review output contract。
2. 更新 API / DB 持久化路径以支持最小 review 结果。
3. 实现 `review_graph` 最小节点链。
4. 验证 `postclose_review` 在“有计划 + 有 execution record”的条件下能产生稳定输出。

Rollback 方案是保留现有 placeholder 路径，并让新 contract/model 不被入口引用。

## Open Questions

- `execution_records` 是否需要补充价格、数量、时间戳精度等更细字段才能满足后续评分？
- review 结果是直接写入现有 `reviews` 表，还是需要独立对象后再投影？
- baseline graph 是纯规则总结，还是允许接入现有 LLM provider 做最终总结润色？
