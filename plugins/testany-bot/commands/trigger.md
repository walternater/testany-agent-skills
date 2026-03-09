---
description: Testany Trigger，为 pipeline 配置 Plan、Manual Trigger、Gatekeeper
argument-hint: <操作> <描述>，如：创建手动触发、设置定时执行、创建 Gatekeeper
---

# Testany Trigger

为已有 pipeline 配置执行入口。Trigger 是执行入口，不是编排层。

## 使用方式

$ARGUMENTS

## 支持的操作

- **定时计划**：创建 Plan，配置 cron 表达式
- **手动触发**：配置 Manual Trigger（当前若 MCP 未提供 tools，则走 UI fallback）
- **事件触发**：创建 Gatekeeper，接入 Jenkins/GitHub Actions 等外部系统
- **管理配置**：更新或删除已有 trigger

## 示例

```
/trigger 给 Y2K-0601 创建 Gatekeeper
/trigger 每天凌晨 2 点执行回归测试
/trigger 给验收流水线创建一个 Manual Trigger
/trigger 接入 GitHub Actions
```
