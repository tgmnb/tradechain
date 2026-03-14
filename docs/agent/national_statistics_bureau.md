# 国家统计局

定位：
- 新闻、公告、事件、数据快讯抓取
- 结构化整理成议案草稿
- 定时更新市场动态、宏观事件、产业链事件

工程映射：
- 新闻理解 Agent
- 情报抓取器
- 结构化议案输入层

当前实现映射：
- 对应目录 [national_statistics_bureau](/home/tgm/project/tradechain/configs/departments/national_statistics_bureau)
- 已有 `intel_officer`
- 已挂载 `news_parse_skill`
- 通过跨层级显式绑定复用 `proposal_draft_skill`

当前代码状态：
- 已支撑 `intel_update`
- 是当前最完整的上游研究入口部门
