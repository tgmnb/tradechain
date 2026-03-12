# AI投研Agent系统项目说明书（n8n + LangGraph）

## 1. 项目概述

本项目拟构建一套面向**期货全品种 + 股票全市场**的 AI Agent 投研与执行监督系统。系统目标不是替代用户做最终投资决策，而是作为一个具有组织分工、流程治理、持续学习和执行监督能力的“智能投研中枢”，持续完成以下任务：

- 全市场、多资产、多频率的信息监控
- 机会发现、预期差识别、交易计划辅助
- 盘前计划、盘中跟踪、盘后复盘、长期评价
- 策略归档、知识沉淀、案例复用
- Agent 的效果评估、Skill 迭代、自我优化
- 用户执行力反馈与能力训练

项目采用**类中国政治体制的治理结构**作为组织抽象，但在技术实现上严格转译为工程可执行的角色、权限、流程、审计与状态机，避免流于概念化。

系统底座采用：

- **n8n**：负责编排、调度、定时任务、事件总线、审批流、通知与对外系统连接
- **LangGraph**：负责复杂 Agent 状态机、长链路决策、多角色协作、记忆、复盘、自我改进闭环

---

## 2. 项目目标

### 2.1 核心业务目标

1. 建立统一的“国策库”（投资知识与策略库）
2. 支持盘前、盘中、盘后、夜间评估四大主流程
3. 实现机会从“发现 → 论证 → 审议 → 计划 → 执行监督 → 复盘归档”的闭环
4. 支持按资产类别、行业、主题、时间尺度扩展新的部委 Agent 与 Skill
5. 支持 Agent 的绩效评估与版本迭代
6. 支持用户执行行为的监督、反馈与训练

### 2.2 技术架构目标

1. 先搭稳定框架，再逐步填充 Skill 和 Agent
2. 所有高风险节点必须可审计、可中断、可人工插手
3. 所有策略、结论、审议意见必须入库留档
4. 所有 Agent 输出必须结构化，禁止纯自然语言漂浮输出
5. 自我优化必须通过“评估 → 提案 → 测试 → 审批 → 上线”闭环完成，禁止直接自改生产

---

## 3. 设计原则

### 3.1 总体原则

- **人类最终负责**：总书记（用户）拥有最终拍板权
- **职责分离**：提出建议、审议、执行监督、培训改进互相独立
- **状态持久化**：所有关键任务有状态、有版本、有日志
- **结构化输出**：所有结论必须可存储、可排序、可评分
- **可演进**：先有骨架，再有器官，最后训练肌肉
- **先治理后自动化**：先把流程跑顺，再放大自动化程度

### 3.2 风险控制原则

- 自动化不等于自动下单
- 决策建议与执行监督必须隔离
- Skill 迭代必须通过测试集与沙盒环境验证
- 关键高风险动作必须经过人工审批
- 任何自我提升行为都必须留痕

---

## 4. 组织结构映射

### 4.1 顶层角色

#### 4.1.1 总书记（用户）

职责：
- 定方向
- 定红线
- 审批重大方案
- 选择最终投资动作
- 决定是否采纳改进建议

#### 4.1.2 中央政治局

职责：
- 接收总书记任务
- 明确问题定义、目标、约束条件、优先级
- 形成可执行任务说明

工程映射：
- 战略任务澄清 Agent
- 目标定义器
- 任务模板系统

#### 4.1.3 人民代表大会

职责：
- 审核目标是否合理
- 审核国务院方案是否符合目标
- 审核阶段性结果是否达标

工程映射：
- 目标审查 Agent
- 方案一致性审查 Agent
- 结果验收 Agent

#### 4.1.4 国务院

职责：
- 将目标转化为计划
- 拆解任务
- 分派部委执行
- 汇总成果
- 维护国策库

工程映射：
- 中枢总控 Graph
- 任务分解器
- 汇总编审器
- 策略排序器
- 国策库维护器

---

## 5. 具体职能部门设计

### 5.1 国务院下属部委（功能 Agent 群）

每个部委都是一个 LangGraph 子图或一组 Skill 编排，不要求初期全部实现。先建立统一接口，再逐步补全能力。

建议首批部委如下：

1. **国家统计局**
   - 新闻、公告、事件、数据快讯抓取
   - 结构化整理成“议案草稿”
   - 定时更新市场动态、宏观事件、产业链事件

2. **发改委 / 宏观委**
   - 机会池跟踪、排序、整理
   - 暴露、相关性、风险预算、时间分层管理


3. **农业农村部**
   - 期货相关品种基本面、天气、产区、库存、贸易流
   - 维护商品级逻辑库
   

4. **证监会**
   - 股票全市场扫描
   - 行业、风格、主题、异动、公告、财报线索

5. **气象局**
   - 货币、利率、汇率、信用、资金面
   - 宏观逻辑、政策预期、产业政策、流动性判断
   - 形成大级别宏观背景

6. **央行**
   - 仓位管理
   - 资金管理
   - 风险管理

7. **公安部**
   - 盘中按计划检查是否触发交易条件
   - 跟踪是否发生偏离
   - 生成督办提醒

### 5.2 中央书记处

职责：
- 全流程记录
- 文档归档
- 版本留存
- 议案、决策、驳回意见、复盘结论统一编号

工程映射：
- 归档总线
- 文档/数据库落盘服务
- 检索接口

### 5.3 中纪委

职责：
- 评估 Agent 运行效果
- 寻找长期最影响系统收益/稳定性的薄弱环节
- 输出整改清单

工程映射：
- 绩效评分器
- 失败归因器
- 瓶颈分析器

### 5.4 中组部

职责：
- 根据中纪委意见改进 Agent
- 维护 Skill 版本
- 训练、重构、替换低绩效模块

工程映射：
- Skill 注册表
- Prompt/策略版本管理
- 回归测试流
- 灰度上线流程

### 5.5 中央军委

职责：
- 吸收宏观、行业、个股/品种逻辑
- 形成最终投资提案出口
- 在复盘会/盘前会中形成候选交易清单

工程映射：
- 决策合成 Graph
- 提案生成器
- 风险对冲与优先级整形器

### 5.6 政治局常委

职责：
- 盘中实时检验关键方案与市场演化是否一致
- 负责高频状态巡检

工程映射：
- 盘中巡检 Agent
- 实时触发器
- 偏离提醒器

### 5.7 人民法院

职责：
- 检验总书记（用户）的真实执行情况
- 分析“知道但没做”“计划外冲动”“风控失守”等问题

工程映射：
- 行为比对器
- 计划-执行偏差分析器
- 用户执行评分器

### 5.8 中央警卫团

职责：
- 根据人民法院结论，进行用户心理辅导与执行训练
- 提供科学、行为化、可量化的改善建议

工程映射：
- 行为教练 Agent
- 情绪/执行问题辅导器
- 日常训练计划生成器

---

## 6. 五类主链路设计

### 链路 1：重大任务链

流程：
1. 总书记提出目标
2. 中央政治局明确任务定义与效果目标
3. 人民代表大会审议目标合理性
4. 国务院生成实施方案
5. 人民代表大会再次审议方案
6. 驳回则回国务院修改
7. 通过则国务院分派部委执行
8. 部委按规划完成任务
9. 回交国务院验收
10. 不通过则返工
11. 通过则形成完整成果
12. 上报总书记
13. 归档进入国策库
14. 全流程由书记处记录

### 链路 2：定时情报更新链

流程：
1. 国家统计局定时抓取新闻、公告、数据、事件
2. 结构化为议案草稿
3. 分发给相关部委研究
4. 各部委形成分析与意见
5. 国务院汇总后纳入国策库
6. 中央书记处统一留档

### 链路 3：策略维护与提案链

流程：
1. 国务院定时梳理国策库中现有议案
2. 对议案进行维护、更新、排序
3. 宏观、行业、主题逻辑传送中央军委
4. 军委形成最终投资提案
5. 在每日复盘会研究
6. 用户确定次日计划

### 链路 4：盘中执行监督链

流程：
1. 按计划定时检查市场状态
2. 检查是否满足交易计划触发条件
3. 提示总书记
4. 总书记执行后报备
5. 书记处归档
6. 盘后人民法院检查执行质量
7. 中央警卫团进行行为训练安排

### 链路 5：夜间评估与自我进化链

流程：
1. 夜间中纪委审阅阶段运行效果
2. 评价历史策略表现与 Agent 运行质量
3. 找出影响系统效果最显著的几个 Agent / Skill
4. 交由中组部进行重构与改进
5. 改进方案进入测试、验证、审批
6. 通过后进入正式版本

---

## 7. 技术架构设计

### 7.1 总体架构

采用“n8n 编排中枢 + LangGraph 智能子图 + 数据/知识底座 + 审计与版本控制”架构。

### 7.2 n8n 的职责

n8n 负责：
- 定时任务
- Webhook 触发
- API 调用与外部系统对接
- 消息通知
- 审批流
- 轻量 ETL
- 事件总线
- 执行日志汇聚
- 将任务发送给 LangGraph 服务
- 接收 LangGraph 结果并继续流程

### 7.3 LangGraph 的职责

LangGraph 负责：
- 复杂 Agent 决策图
- 多角色协作
- 长链路任务状态管理
- 暂停/恢复
- 人工审核插入点
- 反思与复盘
- 自我改进提案生成
- 记忆与经验复用

### 7.4 数据底座

建议数据层最小可用集合：
- PostgreSQL：任务、议案、结论、评分、日志、版本
- 对象存储：报告、图表、附件、原始快照
- 向量库：研究资料、历史案例、复盘文本、文档检索
- Redis：缓存、队列、短时状态

### 7.5 Skill 注册表

Skill 需统一注册，至少包括：
- Skill 名称
- 所属部委
- 输入规范
- 输出规范
- 依赖工具
- 使用场景
- 评估指标
- 当前版本
- 上线状态
- 最近一次评估结果

---

## 8. 数据对象设计

建议统一以下核心对象：

### 8.1 Task（任务）
- 任务编号
- 来源
- 所属链路
- 当前状态
- 优先级
- 发起时间
- 截止时间
- 目标描述

### 8.2 Proposal（议案）
- 议案编号
- 主题
- 资产范围
- 核心结论
- 驱动因子
- 风险点
- 状态
- 所属策略主题

### 8.3 Review（审议）
- 审议人/Agent
- 审议时间
- 审议结果
- 驳回原因
- 修改建议

### 8.4 Strategy（策略）
- 策略编号
- 适用场景
- 前提条件
- 触发条件
- 失效条件
- 风险控制
- 历史评分

### 8.5 Execution（执行）
- 用户计划动作
- 实际动作
- 时间差
- 偏差原因
- 执行评分

### 8.6 Improvement Ticket（改进工单）
- 工单编号
- 问题对象
- 影响描述
- 改进建议
- 测试结果
- 上线状态

---

## 9. 输出标准规范

所有 Agent 输出必须遵守结构化标准，建议统一格式：

- 结论
- 证据
- 核心驱动
- 反证/反方观点
- 置信度
- 触发条件
- 失效条件
- 风险点
- 推荐动作
- 是否需人工审批

禁止只输出“看多/看空”一类空洞结论。

---

## 10. 开发范围划分

### 10.1 第一阶段只做稳定骨架

第一阶段目标不是“功能全”，而是“治理结构能跑起来”。

优先实现：
- 顶层流程骨架
- 书记处留档
- 国策库
- 任务/议案/审议/策略/执行五大数据对象
- 链路 1~5 的最小可用版本
- 中纪委评估 + 中组部改进工单机制

暂不追求：
- 全品种全数据接入
- 高质量所有部委能力
- 自动下单
- 复杂多模态输入

### 10.2 第二阶段再逐步填充 Skill

按优先级逐步补：
1. 新闻抽取类 Skill
2. 议案归纳类 Skill
3. 宏观背景类 Skill
4. 行业催化扫描类 Skill
5. 执行监督类 Skill
6. 行为训练类 Skill
7. Agent 自我评价类 Skill

---

## 11. 开发流程

### 阶段 0：需求冻结与术语统一

目标：
- 固化组织结构
- 定义术语
- 明确哪些角色是治理角色，哪些角色是功能角色

产出物：
- 角色清单
- 链路清单
- 数据对象字典
- 输出格式规范

### 阶段 1：项目骨架搭建

目标：
- 跑通最小主流程
- 搭好底层基础设施

技术任务：
- 搭建 n8n
- 搭建 LangGraph 服务
- 建 PostgreSQL / Redis / 对象存储 / 向量库
- 设计数据库 schema
- 完成统一任务编号与日志体系
- 完成中央书记处归档服务

产出物：
- 基础部署环境
- 核心数据库表
- 日志/归档流水线

### 阶段 2：五条主链路的最小闭环

目标：
- 五条链路都能跑通，但每条只做最小版本

技术任务：
- 用 n8n 建立五条主流程的主编排
- 用 LangGraph 建立国务院总控图、人大审议图、中纪委评估图、中组部整改图
- 打通总书记输入与最终归档

产出物：
- 五条链路的端到端 Demo
- 可查看的国策库与归档界面

### 阶段 3：首批核心部委上线

建议首批只做 4 个：
- 国家统计局
- 气象局
- 农业农村部
- 证监会/股票市场部

技术任务：
- 为每个部委定义统一接口
- 每个部委先实现 2~3 个 Skill
- 将部委结果接入国务院汇总与人大审议

产出物：
- 初版部委 Agent 群
- 初版机会池与议案池

### 阶段 4：中央军委与盘中监督链打通

目标：
- 形成真正能支持盘前计划和盘中提醒的系统

技术任务：
- 实现策略排序器
- 实现中央军委提案合成器
- 实现政治局常委盘中巡检器
- 实现计划触发与提醒机制
- 实现用户报备接口

产出物：
- 每日计划清单
- 盘中提醒清单
- 执行记录流水

### 阶段 5：人民法院 + 警卫团上线

目标：
- 让系统开始管理用户行为与执行质量

技术任务：
- 对比计划动作与实际动作
- 识别拖延、冲动、漏做、过量交易等问题
- 输出针对性的行为改善建议与训练安排

产出物：
- 用户执行评分体系
- 行为训练工单

### 阶段 6：中纪委 + 中组部自我进化闭环

目标：
- 让系统开始真正“自我提升”

技术任务：
- 对 Agent / Skill 建立评分维度
- 构建失败案例回放与归因流程
- 输出改进工单
- 构建测试集/回归测试/灰度上线机制
- 版本发布审批流程

产出物：
- Agent/Skill 评分面板
- 改进工单池
- 版本迭代机制

---

## 12. 版本策略

### v0.1 骨架版
- 五大链路跑通
- 只有少量部委
- 只有少量 Skill
- 有归档、有审议、有评估

### v0.2 实用版
- 支持日常盘前/盘中/盘后流程
- 有机会池和策略池
- 有执行监督

### v0.3 进化版
- 有中纪委评分
- 有中组部改进
- 有测试和版本迭代

### v1.0 体系版
- 多市场、多部委、多 Skill 协同
- 稳定运转
- 可持续自我升级

---

## 13. 项目实施建议

1. 先从“治理结构可运行”开始，而不是先追求分析能力强
2. 先做最小闭环，再增加部委和 Skill
3. 每个新增 Agent 必须先定义输入/输出/评估标准
4. 任何“自我改进”都必须经过审批和测试
5. 国策库与留档系统要尽早建设，它是后续自我进化的基础
6. 不要一开始追求自动执行，先把建议、审议、复盘做好

---

## 14. 一句话总结

本项目不是在堆一堆会说话的 Agent，而是在构建一套具备**治理结构、任务状态、审议流程、执行监督、知识沉淀与持续进化能力**的 AI 投研操作系统。n8n 负责把全系统串起来，LangGraph 负责让复杂智能流程真正跑起来；先建国家机器，再慢慢给它装上越来越强的器官与技能。


---

# 15. 产品需求文档（PRD）

## 15.1 产品定位

本系统是一套 **AI 投研操作系统（AI Investment Operating System）**，目标不是生成零散分析，而是建立一套具有治理结构、任务流程、知识沉淀与持续优化能力的投研体系。

系统主要解决以下问题：

1. 信息过载
2. 投资逻辑难以沉淀
3. 策略缺乏持续评估
4. 执行纪律难以监督
5. 投研经验难以复用

系统通过 Agent 组织体系解决：

信息 → 议案 → 审议 → 策略 → 执行 → 复盘 → 迭代

---

## 15.2 核心功能模块

### 模块 1：情报中心

职责：

收集所有市场信息并结构化。

输入：

- 新闻
- 公告
- 宏观数据
- 商品供需数据
- 气象数据
- 市场行情

输出：

事件对象 Event

结构：

Event

- id
- 时间
- 类型
- 资产
- 影响方向
- 置信度

---

### 模块 2：议案生成

将 Event 转化为可研究的议案。

Proposal

- id
- 主题
- 涉及资产
- 初始逻辑
- 触发条件
- 风险因素

---

### 模块 3：多部委研究

各部委从不同角度研究议案。

输出：

ResearchReport

字段：

- 结论
- 证据
- 驱动
- 反证
- 置信度

---

### 模块 4：策略形成

国务院汇总研究报告，形成策略。

Strategy

- id
- 资产
- 方向
- 触发条件
- 止损条件
- 风险级别

---

### 模块 5：交易计划

中央军委将策略转为执行计划。

TradingPlan

- 标的
- 方向
- 触发价
- 仓位
- 风控

---

### 模块 6：盘中监控

实时监控市场。

若满足条件：

→ 提醒用户执行。

---

### 模块 7：执行监督

对比计划与实际执行。

ExecutionRecord

- 计划动作
- 实际动作
- 偏差
- 评分

---

### 模块 8：复盘系统

评估策略表现。

StrategyReview

- 盈亏
- 是否符合预期
- 偏差原因

---

### 模块 9：Agent 绩效系统

评估每个 Agent 的效果。

AgentScore

- 命中率
- 提前量
- 收益贡献

---

### 模块 10：Skill 迭代系统

中纪委 → 中组部。

输出：

ImprovementTicket

- 问题
- 影响
- 改进方案

---

# 16. 技术架构图

```

                用户（总书记）
                       │

                n8n 中央编排
                       │

         ┌─────────────┴─────────────┐
         │                           │

   LangGraph 决策系统         数据与知识系统

         │                           │

   多角色 Agent 图            PostgreSQL

         │                    向量数据库

   Skill 执行层                对象存储

         │

      工具层

(API / 数据源 / 市场接口 / 模型)

```

---

# 17. 数据库设计（核心表）

## 表：tasks

字段

- id
- title
- type
- status
- created_at

---

## 表：events

字段

- id
- source
- asset
- description
- timestamp

---

## 表：proposals

字段

- id
- theme
- asset
- logic
- status

---

## 表：research_reports

字段

- id
- proposal_id
- department
- conclusion
- confidence

---

## 表：strategies

字段

- id
- asset
- direction
- trigger
- stop

---

## 表：trading_plans

字段

- id
- strategy_id
- asset
- trigger_price
- position

---

## 表：execution_records

字段

- id
- plan_id
- actual_action
- deviation

---

## 表：agent_scores

字段

- agent
- score
- win_rate

---

## 表：skill_versions

字段

- skill_name
- version
- status

---

# 18. LangGraph Agent 架构（第一批）

建议第一批只做 6 个核心 Agent：

1 宏观分析 Agent

负责宏观逻辑。

2 市场扫描 Agent

负责全市场扫描。

3 商品供需 Agent

负责期货逻辑。

4 新闻理解 Agent

负责新闻事件。

5 策略合成 Agent

负责整合策略。

6 复盘评估 Agent

负责复盘。

---

## LangGraph 节点结构示例

```

Start

 ↓

Event Parser

 ↓

Proposal Generator

 ↓

Department Research

 ↓

Strategy Synthesizer

 ↓

Trading Plan Generator

 ↓

Archive

```

---

# 19. n8n 工作流（第一批）

建议先做 5 个 workflow：

1

新闻抓取 workflow

2

每日盘前 workflow

3

盘中监控 workflow

4

盘后复盘 workflow

5

夜间评估 workflow

---

# 20. 第一阶段开发任务清单

阶段目标：

构建可运行骨架。

任务：

1

部署 n8n

2

部署 LangGraph 服务

3

搭建数据库

4

实现事件抓取

5

实现 Proposal 生成

6

实现 Research Agent

7

实现 Strategy 生成

8

实现 Archive 系统

9

实现简单盘中提醒

10

实现复盘评分

---

# 21. 开发顺序建议

推荐顺序：

1

数据层

2

事件系统

3

议案系统

4

研究系统

5

策略系统

6

执行监督

7

复盘系统

8

Agent 评分

9

Skill 迭代

---

# 22. 最小可用版本目标（MVP）

MVP 目标：

系统可以完成以下流程：

新闻 → 议案 → 研究 → 策略 → 交易计划 → 提醒 → 复盘 → 评分 → 改进

只要这个循环跑通，系统就已经具备“自进化能力”。

之后只需要不断增加：

- 新 Agent
- 新 Skill
- 新数据源

系统能力就会持续增强。

---

# 23. 项目一句话定义

这不是一个 AI 工具，而是一套 **AI 投研国家机器**。

n8n 是行政体系。

LangGraph 是大脑。

数据系统是记忆。

Skill 是能力。

Agent 是干部。

用户是最终决策者。

系统目标只有一个：

**让正确的投资逻辑被不断发现、审议、执行、复盘、强化。**


---

# 24. v0.1 工程级架构设计

## 24.1 v0.1 目标范围

v0.1 不追求“全市场、全功能、全自动”，只追求以下四件事：

1. 有统一任务入口与归档出口
2. 有事件 → 议案 → 研究 → 策略 → 计划 → 复盘的完整闭环
3. 有最小化的 Agent 评分与改进工单机制
4. 有足够稳定的底座，便于后续不断增加部委 Agent 和 Skill

v0.1 不包含：

- 自动下单
- 高频交易
- 复杂图像/语音多模态
- 全部部委一次性落地
- 完整用户心理训练体系

---

## 24.2 v0.1 系统总架构图（工程视角）

```text

                         ┌────────────────────┐
                         │      用户界面层      │
                         │ Web / 飞书 / Telegram │
                         └─────────┬──────────┘
                                   │
                                   ▼
                      ┌──────────────────────────┐
                      │      API Gateway 层       │
                      │   FastAPI / Auth / RBAC   │
                      └───────┬──────────┬───────┘
                              │          │
                              │          │
                              ▼          ▼
                 ┌────────────────┐   ┌────────────────┐
                 │  n8n 编排中枢   │   │ LangGraph 服务  │
                 │ 调度/审批/通知  │   │ 状态机/Agent图  │
                 └──────┬─────────┘   └──────┬─────────┘
                        │                    │
                        │                    │
          ┌─────────────┼─────────────┐      │
          │             │             │      │
          ▼             ▼             ▼      ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐ ┌────────────────┐
   │ 数据接入层 │   │ 归档记录层 │  │ 通知提醒层 │ │ Skill / Tool层 │
   │ News/API  │   │ DB/Object │  │ Bot/Email │ │ Weather/Market │
   └────┬─────┘   └────┬─────┘  └────┬─────┘ └───────┬────────┘
        │              │              │               │
        └──────────────┴──────┬───────┴───────────────┘
                               ▼
                    ┌──────────────────────────┐
                    │     数据与知识底座        │
                    │ PostgreSQL / Redis /      │
                    │ Vector DB / MinIO         │
                    └──────────────────────────┘

```

---

## 24.3 服务拆分建议

### 服务 1：api-service

职责：
- 用户请求入口
- 鉴权
- RBAC 权限控制
- 汇总查询接口
- 向前端提供统一 API

建议技术：
- FastAPI
- Pydantic
- SQLAlchemy

### 服务 2：workflow-orchestrator（n8n）

职责：
- 定时调度
- 事件触发
- 审批流
- 调用 LangGraph
- 通知用户
- 记录流程状态

### 服务 3：agent-core（LangGraph）

职责：
- 运行国务院总控图
- 运行人大审议图
- 运行部委研究图
- 运行复盘图
- 运行中纪委评分图
- 运行中组部改进图

### 服务 4：ingestion-service

职责：
- 新闻抓取
- 公告抓取
- 市场数据接入
- 外部数据标准化

### 服务 5：archive-service

职责：
- 所有关键对象入库
- 所有报告、快照、附件入对象存储
- 维护编号和版本

### 服务 6：evaluation-service

职责：
- 计算 Agent 评分
- 计算策略评分
- 生成改进工单

---

# 25. LangGraph 主图设计

## 25.1 State 设计

建议定义统一的 GraphState：

```python
class GraphState(TypedDict):
    task_id: str
    chain_type: str
    user_goal: dict
    events: list
    proposals: list
    reviews: list
    research_reports: list
    strategies: list
    trading_plans: list
    execution_records: list
    archive_refs: list
    scores: dict
    improvement_tickets: list
    current_stage: str
    status: str
    requires_human: bool
    messages: list
```

---

## 25.2 国务院总控图（Master Graph）

```text

START
  ↓
Task Intake
  ↓
Goal Clarifier（政治局）
  ↓
Goal Review（人大第一次审议）
  ├── reject → Goal Revision
  └── pass
        ↓
Plan Generator（国务院）
        ↓
Plan Review（人大第二次审议）
  ├── reject → Plan Revision
  └── pass
        ↓
Department Dispatcher
        ↓
Department Research Aggregator
        ↓
Result Acceptance（国务院验收）
  ├── reject → Rework
  └── pass
        ↓
Archive To 国策库
        ↓
Report To User
        ↓
END

```

---

## 25.3 部委研究子图（Department Subgraph）

```text

START
  ↓
Receive Proposal
  ↓
Load Relevant Skills
  ↓
Call Tools / Query Data
  ↓
Draft Research Report
  ↓
Self Critique
  ↓
Output Structured Report
  ↓
END

```

---

## 25.4 人大审议子图

```text

START
  ↓
Receive Object (Goal / Plan / Result)
  ↓
Check Rationality
  ↓
Check Consistency
  ↓
Check Measurability
  ↓
Decision
  ├── pass
  └── reject + comments
  ↓
END

```

---

## 25.5 中纪委评估子图

```text

START
  ↓
Load Historical Results
  ↓
Rank Worst Performers
  ↓
Find High Impact Failures
  ↓
Generate Evaluation Report
  ↓
Create Improvement Tickets
  ↓
END

```

---

## 25.6 中组部改进子图

```text

START
  ↓
Receive Improvement Ticket
  ↓
Locate Skill / Agent Version
  ↓
Generate Improvement Proposal
  ↓
Run Regression Test
  ├── fail → mark rejected
  └── pass → ready for approval
  ↓
Human Approval
  ├── reject
  └── approve
  ↓
Publish New Version
  ↓
END

```

---

# 26. n8n Workflow 拓扑设计

## 26.1 Workflow 1：定时情报更新

触发：
- 每 15 分钟 / 每小时 / 每日定时

流程：
1. Cron Trigger
2. 调用 ingestion-service
3. 去重
4. 写入 events
5. 调用 LangGraph：新闻理解 / 议案草稿生成
6. 归档
7. 通知相关部委处理

---

## 26.2 Workflow 2：重大任务处理

触发：
- 用户发起任务

流程：
1. Webhook / API Trigger
2. 创建 task
3. 调用国务院主图
4. 若 requires_human = true，则进入审批节点
5. 通过后继续执行
6. 最终归档
7. 返回用户

---

## 26.3 Workflow 3：每日盘前策略生成

触发：
- 每日固定时间

流程：
1. 读取国策库中高优先级议案
2. 调用策略维护器
3. 调用中央军委提案图
4. 生成年内/日内交易计划
5. 发送盘前摘要
6. 写入 trading_plans

---

## 26.4 Workflow 4：盘中巡检与提醒

触发：
- 每 X 分钟定时

流程：
1. 读取 active trading plans
2. 获取市场实时数据
3. 检查是否满足触发条件
4. 满足则提醒用户
5. 用户反馈执行情况
6. 写入 execution_records

---

## 26.5 Workflow 5：盘后复盘与法院判决

触发：
- 每日收盘后

流程：
1. 读取今日 plan 与 execution
2. 调用复盘 Agent
3. 调用人民法院执行分析 Agent
4. 生成用户执行报告
5. 生成警卫团训练建议
6. 归档

---

## 26.6 Workflow 6：夜间评估与改进

触发：
- 每日夜间 / 每周

流程：
1. 加载一段时间内的策略结果与 Agent 表现
2. 调用中纪委评估图
3. 生成 improvement tickets
4. 调用中组部改进图
5. 进入测试与审批流
6. 通过后更新 skill_versions

---

# 27. 数据库 Schema 设计（详细版）

## 27.1 tasks

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    source VARCHAR(50),
    status VARCHAR(30) NOT NULL,
    priority INTEGER DEFAULT 50,
    chain_type VARCHAR(50) NOT NULL,
    created_by VARCHAR(100),
    assigned_to VARCHAR(100),
    goal_json JSONB,
    context_json JSONB,
    requires_human BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.2 events

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    asset_scope JSONB,
    title TEXT,
    content TEXT,
    impact_direction VARCHAR(20),
    confidence NUMERIC(5,2),
    raw_payload JSONB,
    occurred_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.3 proposals

```sql
CREATE TABLE proposals (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    source_event_id UUID REFERENCES events(id),
    theme VARCHAR(200),
    asset_scope JSONB,
    initial_logic TEXT,
    trigger_conditions JSONB,
    invalidation_conditions JSONB,
    risks JSONB,
    status VARCHAR(30) NOT NULL,
    rank_score NUMERIC(8,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.4 reviews

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY,
    object_type VARCHAR(30) NOT NULL,
    object_id UUID NOT NULL,
    reviewer_type VARCHAR(30) NOT NULL,
    reviewer_name VARCHAR(100) NOT NULL,
    decision VARCHAR(20) NOT NULL,
    comments TEXT,
    score NUMERIC(6,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.5 research_reports

```sql
CREATE TABLE research_reports (
    id UUID PRIMARY KEY,
    proposal_id UUID REFERENCES proposals(id),
    department_name VARCHAR(100) NOT NULL,
    conclusion TEXT,
    evidence JSONB,
    drivers JSONB,
    counterpoints JSONB,
    confidence NUMERIC(5,2),
    recommended_action TEXT,
    structured_output JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.6 strategies

```sql
CREATE TABLE strategies (
    id UUID PRIMARY KEY,
    proposal_id UUID REFERENCES proposals(id),
    theme VARCHAR(200),
    asset VARCHAR(100),
    direction VARCHAR(20),
    setup_type VARCHAR(50),
    trigger_conditions JSONB,
    invalidation_conditions JSONB,
    risk_controls JSONB,
    priority_score NUMERIC(8,2),
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.7 trading_plans

```sql
CREATE TABLE trading_plans (
    id UUID PRIMARY KEY,
    strategy_id UUID REFERENCES strategies(id),
    plan_date DATE NOT NULL,
    asset VARCHAR(100) NOT NULL,
    direction VARCHAR(20),
    trigger_rule JSONB,
    entry_zone JSONB,
    stop_rule JSONB,
    target_rule JSONB,
    position_rule JSONB,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.8 execution_records

```sql
CREATE TABLE execution_records (
    id UUID PRIMARY KEY,
    trading_plan_id UUID REFERENCES trading_plans(id),
    user_action VARCHAR(50),
    action_time TIMESTAMPTZ,
    action_payload JSONB,
    deviation_type VARCHAR(50),
    deviation_reason TEXT,
    execution_score NUMERIC(6,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.9 archives

```sql
CREATE TABLE archives (
    id UUID PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL,
    object_id UUID NOT NULL,
    archive_key VARCHAR(255) NOT NULL,
    storage_type VARCHAR(30) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.10 agent_scores

```sql
CREATE TABLE agent_scores (
    id UUID PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    win_rate NUMERIC(6,2),
    precision_score NUMERIC(6,2),
    timeliness_score NUMERIC(6,2),
    contribution_score NUMERIC(6,2),
    stability_score NUMERIC(6,2),
    total_score NUMERIC(6,2),
    detail_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.11 skill_versions

```sql
CREATE TABLE skill_versions (
    id UUID PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    owner_department VARCHAR(100),
    status VARCHAR(30) NOT NULL,
    manifest JSONB,
    test_result JSONB,
    changelog TEXT,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 27.12 improvement_tickets

```sql
CREATE TABLE improvement_tickets (
    id UUID PRIMARY KEY,
    target_type VARCHAR(30) NOT NULL,
    target_name VARCHAR(100) NOT NULL,
    source_period_start DATE,
    source_period_end DATE,
    issue_summary TEXT,
    impact_description TEXT,
    root_cause JSONB,
    proposed_fix JSONB,
    status VARCHAR(30) NOT NULL,
    approved_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

# 28. 项目目录结构建议

```text
repo/
├─ apps/
│  ├─ api-service/
│  ├─ agent-core/
│  ├─ ingestion-service/
│  ├─ archive-service/
│  └─ evaluation-service/
├─ workflows/
│  ├─ n8n/
│  │  ├─ intel_update.json
│  │  ├─ daily_preopen.json
│  │  ├─ intraday_watch.json
│  │  ├─ postclose_review.json
│  │  └─ nightly_improvement.json
│  └─ langgraph/
│     ├─ master_graph/
│     ├─ proposal_graph/
│     ├─ department_graphs/
│     ├─ review_graph/
│     ├─ execution_review_graph/
│     └─ improvement_graph/
├─ skills/
│  ├─ news_understanding/
│  ├─ market_scan/
│  ├─ commodity_supply_demand/
│  ├─ weather_risk/
│  ├─ strategy_synthesis/
│  └─ execution_analysis/
├─ libs/
│  ├─ schemas/
│  ├─ db/
│  ├─ logging/
│  ├─ prompts/
│  └─ utils/
├─ infra/
│  ├─ docker/
│  ├─ k8s/
│  └─ terraform/
├─ sql/
│  ├─ migrations/
│  └─ seeds/
├─ docs/
│  ├─ architecture/
│  ├─ prd/
│  ├─ runbooks/
│  └─ adr/
└─ tests/
   ├─ unit/
   ├─ integration/
   ├─ regression/
   └─ evaluation/
```

---

# 29. 第一版代码骨架建议

## 29.1 agent-core 目录

```text
agent-core/
├─ app/
│  ├─ graphs/
│  │  ├─ master_graph.py
│  │  ├─ review_graph.py
│  │  ├─ improvement_graph.py
│  │  └─ departments/
│  │     ├─ news_department.py
│  │     ├─ market_department.py
│  │     ├─ commodity_department.py
│  │     └─ weather_department.py
│  ├─ nodes/
│  │  ├─ goal_clarifier.py
│  │  ├─ plan_generator.py
│  │  ├─ dispatcher.py
│  │  ├─ aggregator.py
│  │  ├─ archive_writer.py
│  │  └─ scorer.py
│  ├─ state/
│  │  └─ graph_state.py
│  ├─ skills/
│  ├─ tools/
│  ├─ services/
│  └─ main.py
└─ tests/
```

---

## 29.2 GraphState 示例

```python
from typing import TypedDict, List, Dict, Any

class GraphState(TypedDict, total=False):
    task_id: str
    chain_type: str
    current_stage: str
    status: str
    requires_human: bool
    user_goal: Dict[str, Any]
    events: List[Dict[str, Any]]
    proposals: List[Dict[str, Any]]
    reviews: List[Dict[str, Any]]
    research_reports: List[Dict[str, Any]]
    strategies: List[Dict[str, Any]]
    trading_plans: List[Dict[str, Any]]
    execution_records: List[Dict[str, Any]]
    archive_refs: List[Dict[str, Any]]
    scores: Dict[str, Any]
    improvement_tickets: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
```

---

## 29.3 主图伪代码

```python
from langgraph.graph import StateGraph, END
from app.state.graph_state import GraphState
from app.nodes.goal_clarifier import goal_clarifier
from app.nodes.plan_generator import plan_generator
from app.nodes.dispatcher import dispatcher
from app.nodes.aggregator import aggregator
from app.nodes.archive_writer import archive_writer


def build_master_graph():
    g = StateGraph(GraphState)

    g.add_node("goal_clarifier", goal_clarifier)
    g.add_node("plan_generator", plan_generator)
    g.add_node("dispatcher", dispatcher)
    g.add_node("aggregator", aggregator)
    g.add_node("archive_writer", archive_writer)

    g.set_entry_point("goal_clarifier")
    g.add_edge("goal_clarifier", "plan_generator")
    g.add_edge("plan_generator", "dispatcher")
    g.add_edge("dispatcher", "aggregator")
    g.add_edge("aggregator", "archive_writer")
    g.add_edge("archive_writer", END)

    return g.compile()
```

---

# 30. 首批 Skill 清单（v0.1）

建议只做 8 个 Skill：

1. news_parse_skill
   - 把新闻转成结构化事件

2. proposal_draft_skill
   - 由事件生成议案草稿

3. market_scan_skill
   - 扫描市场异动与主题线索

4. commodity_logic_skill
   - 商品供需与天气基础逻辑整理

5. strategy_synthesis_skill
   - 汇总研究形成策略

6. plan_generation_skill
   - 把策略转成交易计划

7. execution_compare_skill
   - 计划与执行对比

8. improvement_ticket_skill
   - 从失败案例中提取改进工单

每个 Skill 必须包含：
- manifest
- input schema
- output schema
- prompt
- eval cases

---

# 31. Sprint 规划建议

## Sprint 1（1~2 周）

目标：底座跑起来

内容：
- 部署 n8n
- 部署 LangGraph 服务
- 初始化数据库
- 跑通 task / event / archive 三表
- 搭好 API service

## Sprint 2（1~2 周）

目标：事件 → 议案闭环

内容：
- 完成新闻抓取
- 完成 news_parse_skill
- 完成 proposal_draft_skill
- 结果入 proposals

## Sprint 3（2 周）

目标：议案 → 研究 → 策略

内容：
- 完成首批部委研究子图
- 完成 strategy_synthesis_skill
- 存 strategies

## Sprint 4（1~2 周）

目标：计划 → 提醒 → 记录

内容：
- 完成 plan_generation_skill
- 完成盘中巡检 workflow
- 完成 execution_records

## Sprint 5（2 周）

目标：复盘 → 评分 → 改进

内容：
- 完成 execution_compare_skill
- 完成 agent_scores
- 完成 improvement_ticket_skill

---

# 32. 开发实施建议（现实版）

1. 所有对象统一 UUID
2. 先做 API 和 DB，再做花哨 Agent
3. 先用假数据和静态输入把流程跑通
4. 所有 LangGraph 节点都要能单测
5. 所有 n8n workflow 都要有失败补偿与重试机制
6. 先把书记处归档做好，否则后续无法复盘和自我进化
7. 不要在 v0.1 里碰自动下单
8. 先把“稳定记录 + 稳定评估 + 稳定改进工单”做出来，这三样比十个华丽 Agent 更值钱

---

# 33. 下一步直接开工清单

如果进入开发，建议按下面顺序直接执行：

第 1 步：建仓库与目录结构
第 2 步：起 PostgreSQL / Redis / MinIO / n8n / agent-core
第 3 步：建 SQL migrations
第 4 步：实现 tasks、events、archives 接口
第 5 步：实现第一个 n8n workflow（情报更新）
第 6 步：实现第一个 LangGraph（事件 → 议案）
第 7 步：实现国策库查询接口
第 8 步：实现每日盘前 workflow
第 9 步：实现复盘与评分
第 10 步：实现中纪委 → 中组部改进工单闭环

---

# 34. v0.1 完成标准

满足以下条件即视为 v0.1 完成：

1. 用户能发起任务
2. 系统能自动接收情报并生成议案
3. 系统能形成至少一类可用策略
4. 系统能生成盘前计划并在盘中提醒
5. 系统能记录执行与盘后复盘
6. 系统能对 Agent / Skill 输出评分
7. 系统能生成改进工单并保留版本记录
8. 所有中间结果可检索、可追溯、可归档

---

# 35. 一句话工程判断

这套系统的关键，不是先把“分析能力”卷到天上，而是先把“国家机器的骨架、账本、问责、改进闭环”搭起来。只要这些先立住，后面新增部委、Skill、数据源，就是往机器里加器官；如果这些没立住，后面加得越多，越像一台会说话但没人管账的蒸汽怪兽。

