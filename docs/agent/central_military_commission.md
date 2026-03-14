# 中央军委

定位：
- 吸收宏观、行业、个股/品种逻辑
- 形成最终投资提案出口
- 在复盘会/盘前会中形成候选交易清单

工程映射：
- 决策合成 Graph
- 提案生成器
- 风险对冲与优先级整形器

当前实现映射：
- 对应目录 [central_military_commission](/home/tgm/project/tradechain/configs/departments/central_military_commission)
- 已有 `plan_officer`、`watch_officer`、`review_officer`
- 已挂载 `strategy_synthesis_skill`、`plan_generation_skill`

当前代码状态：
- 已支撑 `daily_preopen`
- 已为 `intraday_watch` / `postclose_review` 准备好角色和 skill 资产
