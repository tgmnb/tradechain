## Context

当前平台已经有 `agent_scores`、`improvement_tickets` 等数据库对象雏形，也有 improvement specialist 与 graph 占位入口，但 nightly improvement 仍没有可以真正运行的闭环。问题不在入口，而在缺少统一评分输入、标准 ticket 产物，以及避免自动错误放大所需的审批流。

## Goals / Non-Goals

**Goals:**
- 明确 nightly improvement baseline 所需输入。
- 明确 improvement ticket 的标准输出。
- 明确审批流和状态边界。

**Non-Goals:**
- 本 change 不直接调整生产中的 soul / skill。
- 本 change 不自动发布 prompt 或配置变更。
- 本 change 不实现完整绩效分析系统。

## Decisions

### 1. Baseline 先从 nightly aggregation 开始
nightly improvement 先消费 proposal / strategy / review 的历史结果，而不是实时流式评分。

Rationale:
- 现有平台更接近批处理 than streaming evaluation。
- nightly aggregation 更容易和现有 n8n / scheduler 结合。

### 2. Ticket 是核心产物，不直接自动修复
nightly improvement 的首要产物应是结构化 improvement ticket。

Rationale:
- 没有 ticket 与审批层，自动修复风险过高。
- ticket 能沉淀问题类别、影响范围和拟议修复。

### 3. 审批流必须显式保留人工闸门
baseline improvement 只能生成建议和待审批状态，不能直接修改运行时配置。

Rationale:
- 当前系统还没有足够强的离线验证与回滚机制。
- 人工闸门可以防止误评分导致的连锁改动。

## Risks / Trade-offs

- [评分输入太弱导致 ticket 价值有限] -> Mitigation: baseline 先聚焦复盘、偏差和失败模式，不追求完整绩效指标。
- [审批流程过重导致无人使用] -> Mitigation: baseline 只保留最小状态机与责任人字段。
- [ticket 粒度过粗难以执行] -> Mitigation: contract 要求包含目标对象、问题摘要和拟议修复。

## Migration Plan

1. 定义 nightly improvement specs 与 contracts。
2. 明确 score aggregation 与 ticket generation 的输入来源。
3. 实现 baseline nightly graph。
4. 将 nightly 结果接到审批或人工处理入口。

## Open Questions

- 哪些评分应作为 nightly baseline 的必需输入？
- approval 责任主体是固定角色、部门负责人，还是 workflow metadata 指定？
- ticket 是否需要直接关联某个 soul / skill version？
