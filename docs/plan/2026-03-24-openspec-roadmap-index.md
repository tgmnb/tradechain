# 2026-03-24 OpenSpec 路线图索引

这份索引文档用于快速查看当前仓库里的 OpenSpec 活跃 change，以及建议的推进顺序。

## 当前活跃 changes

### 1. replan-project-roadmap

- 作用：把项目从旧 Sprint 视角切换为 Wave 视角
- 状态：规划基线已建立
- 重点：交付波次、workflow readiness、platform hardening

### 2. implement-postclose-review-baseline

- 作用：把 `postclose_review` 从 placeholder 补到 runnable baseline
- 状态：核心代码与文档已落地，tasks 已全部勾选
- 重点：execution evidence、review output、review graph、review read API

### 3. propose-intraday-watch-baseline

- 作用：定义 `intraday_watch` 的 baseline 输入、触发规则和观察输出
- 状态：提案已建立，待实现
- 重点：market input、trigger throttle/dedup、watch observation contract

### 4. propose-nightly-improvement-baseline

- 作用：定义 `nightly_improvement` 的 baseline 输入、ticket 和审批流
- 状态：提案已建立，待实现
- 重点：historical evidence、improvement ticket、approval flow

## 推荐推进顺序

建议继续按下面顺序推进，而不是并行分散改：

1. 收尾 `implement-postclose-review-baseline`
2. 落地 `propose-intraday-watch-baseline`
3. 落地 `propose-nightly-improvement-baseline`
4. 再进入 Wave 3 平台加固

## 当前结论

- `postclose_review` 已经进入 runnable baseline，可作为 nightly improvement 的前置输入
- `intraday_watch` 仍是 Wave 2 最直接的功能缺口
- `nightly_improvement` 现在已经有了 proposal/spec/design/tasks 骨架，可以在 watch 之后推进

## 常用命令

```bash
./scripts/openspec.sh list
./scripts/openspec.sh show replan-project-roadmap
./scripts/openspec.sh show implement-postclose-review-baseline
./scripts/openspec.sh validate propose-intraday-watch-baseline
./scripts/openspec.sh validate propose-nightly-improvement-baseline
```
