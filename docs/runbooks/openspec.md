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
```

校验某个 change：

```bash
./scripts/openspec.sh validate implement-postclose-review-baseline
./scripts/openspec.sh validate propose-intraday-watch-baseline
```

创建新的 change：

```bash
./scripts/openspec.sh new change my-change-name
```

## 当前建议顺序

按当前仓库状态，建议优先顺序是：

1. `implement-postclose-review-baseline` 收尾与细化
2. `propose-intraday-watch-baseline` 落地
3. `propose-nightly-improvement-baseline` 落地
4. 进入 Wave 3 平台加固

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
2. 语法级 `python3 -c "compile(...)"` 检查
3. 在具备依赖的容器或完整开发环境中再跑 pytest / schema export
