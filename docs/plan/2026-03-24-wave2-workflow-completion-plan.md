# 2026-03-24 Wave 2 工作流补全计划

这份文档只覆盖 Wave 2，即把当前仍处于 `partial / blocked` 状态的三条链路补成“有真实输入、有真实输出、能稳定复用”的工作流。

## 目标范围

本轮只处理：

- `intraday_watch`
- `postclose_review`
- `nightly_improvement`

本轮不处理：

- 生产部署
- 大规模性能优化
- 新增 broker / execution 执行能力

## 当前状态

### intraday_watch

- 当前状态：`partial`
- 已有基础：部门 / specialist / skill 结构已经预留，工作流位置已经预留
- 主要缺口：
  - 缺实时或准实时行情输入
  - 缺事件触发条件和节流规则
  - 缺告警/观察结果的标准输出对象

### postclose_review

- 当前状态：`partial`
- 已有基础：
  - `trading_plan` 已存在
  - `execution_records` API 已存在
  - 无计划时已有 `no_trading_plan` 占位返回
  - 有记录时可 hand-off 到 `review_graph` placeholder
- 主要缺口：
  - execution record 仍主要依赖手工写入
  - `review_graph` 还没有真实节点
  - 缺标准化 review 输出和归档策略

### nightly_improvement

- 当前状态：`blocked`
- 已有基础：improvement specialist / skill 已预留，graph 接口已占位
- 主要缺口：
  - 缺评分输入
  - 缺 improvement ticket 数据模型或标准产物
  - 缺审批流和状态流转

## 推荐补全顺序

建议按以下顺序推进，而不是并行硬铺：

1. `postclose_review`
2. `intraday_watch`
3. `nightly_improvement`

原因：

- `postclose_review` 离现有数据结构最近，已经有 `trading_plan` 和 `execution_records`
- `intraday_watch` 的关键问题是外部数据和触发机制，不依赖 improvement 体系
- `nightly_improvement` 天然依赖 review / execution / strategy 的历史结果，应该最后补

## 每条链的最小落地定义

### 1. postclose_review

最小可交付版本应满足：

- 输入：
  - 一个已存在的 `trading_plan`
  - 至少一条 `execution_record`
- 处理：
  - 汇总计划目标与实际执行动作
  - 识别偏差、遗漏、提前/延后执行、主观备注
  - 输出结构化 review 结果
- 输出：
  - review 记录写回数据库
  - 可归档的 review payload
  - 对后续 improvement 可复用的标准字段

建议拆分：

- 第一步：把 `execution_record` 从“手工补录接口”提升成“有明确来源标记的运行时证据”
- 第二步：实现 `review_graph` 的最小节点链
- 第三步：定义 review contract 与 archive payload

### 2. intraday_watch

最小可交付版本应满足：

- 输入：
  - 一个受控的行情源或 mock-replay 源
  - 一组可配置触发条件
- 处理：
  - 周期性拉取或事件驱动检查
  - 识别价格/成交量/波动等触发条件
  - 生成 watch observation 或 alert
- 输出：
  - 标准化观察结果
  - 可选地触发研究/策略链或发出通知

建议拆分：

- 第一步：确定行情输入方案，优先支持 mock-replay + 单一真实源二选一
- 第二步：定义触发规则和节流策略
- 第三步：定义 `watch` 输出 contract 与下游 hand-off

### 3. nightly_improvement

最小可交付版本应满足：

- 输入：
  - proposal / strategy / trading plan / execution review 的历史样本
  - 一套评分规则
- 处理：
  - 识别失败模式或重复偏差
  - 生成 improvement ticket
  - 进入待审批状态
- 输出：
  - ticket 记录
  - 优先级和影响范围
  - 审批结果或人工待处理状态

建议拆分：

- 第一步：先定义 improvement ticket contract
- 第二步：补评分来源与 nightly aggregation
- 第三步：再实现 approval flow

## 数据与接口优先级

Wave 2 最先需要稳定下来的不是 prompt，而是输入输出对象。

优先级建议：

1. review / watch / improvement 的 contract
2. review / improvement 所需的数据库对象
3. graph 节点最小实现
4. Discord / n8n / API 的入口补齐
5. specialist soul / skill 的进一步细化

## 交付门槛

只有满足以下条件，才能认为 Wave 2 某条链真正完成：

- 不是只有 endpoint 或 placeholder
- 能在本地重复运行
- 有至少一个真实或受控的输入源
- 有可持久化的标准输出
- 能被后续链路消费，而不是只返回一段自由文本

## 下一步建议

下一笔实现工作建议从 `postclose_review` 开始，优先做三件事：

- 明确 execution evidence 的来源字段和最小约束
- 设计 review 输出 contract
- 把 `review_graph` 从 placeholder 升级为最小可运行节点链
