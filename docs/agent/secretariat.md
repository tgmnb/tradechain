# 中央书记处

定位：
- 全流程记录
- 文档归档
- 版本留存
- 议案、决策、驳回意见、复盘结论统一编号

工程映射：
- 归档总线
- 文档/数据库落盘服务
- 检索接口

当前实现映射：
- `archive-service`
- PostgreSQL / MinIO 落盘
- execution / proposal / plan 等结构化对象

当前代码状态：
- 已进入 registry 目录体系，对应 [configs/departments/secretariat](/home/tgm/project/tradechain/configs/departments/secretariat)
- 已预置 `archive_registry_skill`
- 已有可运行归档底座
- 后续还需要进一步覆盖复盘、评分、改进工单全链归档
