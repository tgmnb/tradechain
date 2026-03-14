# 中组部

定位：
- 根据中纪委意见改进 Agent
- 维护 Skill 版本
- 训练、重构、替换低绩效模块

工程映射：
- Skill 注册表
- Prompt/策略版本管理
- 回归测试流
- 灰度上线流程

当前实现映射：
- registry loader
- skill/soul 目录与版本对象
- `improvement_ticket_skill`

当前代码状态：
- 尚未具备真正的“自动重构-测试-审批-发布”闭环
- 目前更多是结构底座和改进工单预备资产
