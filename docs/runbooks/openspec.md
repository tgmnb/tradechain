# OpenSpec Runbook

## 目的

这份 runbook 用于在当前仓库里查看、校验和推进 OpenSpec changes。

## 本地入口

优先使用仓库内脚本，而不是依赖系统全局安装：

```bash
./scripts/openspec.sh --version
./scripts/openspec.sh list
```

## 常用操作

查看当前活跃 changes：

```bash
./scripts/openspec.sh list
```

查看某个 change 的内容：

```bash
./scripts/openspec.sh show replan-project-roadmap
./scripts/openspec.sh show implement-postclose-review-baseline
./scripts/openspec.sh show propose-intraday-watch-baseline
./scripts/openspec.sh show propose-nightly-improvement-baseline
```

校验某个 change：

```bash
./scripts/openspec.sh validate implement-postclose-review-baseline
./scripts/openspec.sh validate propose-intraday-watch-baseline
./scripts/openspec.sh validate propose-nightly-improvement-baseline
./scripts/openspec.sh validate replan-project-roadmap
```

创建新的 change：

```bash
./scripts/openspec.sh new change my-change-name
```

## 当前建议顺序

按当前仓库状态，建议优先顺序是：

1. 用 `replan-project-roadmap` 作为后续 proposal 的规划基线
2. 在 follow-on changes 中分别补齐 workflow baseline
3. 完成 Wave 3 平台加固与部署就绪检查
4. 所有 follow-on work 落地后，再归档 roadmap change

## 使用约束

- 先改 `proposal / design / specs / tasks`，再进入实现
- 每完成一块独立内容就单独提交，便于后续统一 push
- 不把本地工具目录 `.local/` 纳入版本控制

## 环境限制

当前这台环境里：

- `make` 不可用
- `pytest` 不可用
- `pydantic` / `langgraph` 也不保证在宿主 Python 环境中可直接导入

因此本地验证优先顺序应当是：

1. `./scripts/openspec.sh validate <change>`
2. `.venv/bin/python scripts/export_contract_schemas.py`
3. `.venv/bin/pytest -q`
4. 在具备依赖和网络的完整开发环境中再跑 Docker/外部连通性检查
