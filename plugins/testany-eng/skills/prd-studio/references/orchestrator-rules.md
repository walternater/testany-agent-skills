# Orchestrator 规则

## 核心规则

### 1. 隔离执行规则

**每个阶段必须通过 Task tool 启动独立的 subagent**

```
正确：
Task → Writer subagent (隔离上下文)
Task → Reviewer subagent (隔离上下文)

错误：
直接在主线程执行写作/审查逻辑
```

**原因**：
- 避免上下文污染
- 每轮审查都是"新鲜"视角
- 防止 Writer 和 Reviewer 逻辑互相干扰

### 2. 状态传递规则

**所有状态必须通过文件传递，不能依赖对话上下文**

| 状态 | 文件 |
|------|------|
| PRD 内容 | workflow/prd.md |
| 审查结果 | workflow/review-report.md |
| 流程状态 | workflow/status.md |

**原因**：
- Subagent 之间无法共享上下文
- 文件是持久化的，可追溯
- 即使中断也能恢复

### 3. 迭代控制规则

**最多 3 轮迭代**

```
轮次 1: Writer(round=1) → Reviewer → (有问题)
轮次 2: Writer(round=2, 读取 review-report 修复) → Reviewer → (有问题)
轮次 3: Writer(round=3, 读取 review-report 修复) → Reviewer → (仍有问题) → 停止，输出遗留问题
```

> Writer 在 round > 1 时同时承担 Fixer 职责，不再单独派发 Fixer subagent。

**原因**：
- 防止无限循环
- 3 轮通常足够解决大部分问题
- 超过 3 轮说明需求本身可能有问题，需人工介入

### 4. 准出判定规则

| 条件 | 结果 |
|------|------|
| P0 = 0 且 P1 < 2 | 准出通过 |
| P0 > 0 | 阻塞，需修改 |
| P1 >= 2 | 阻塞，需修改 |
| 迭代 >= 3 且仍有问题 | 停止，输出遗留问题 |

### 5. 错误处理规则

**基于 AGENT-RESULT 的失败处理**（详见 `../../../references/subagent-result-contract.md`）：

| 场景 | AGENT-RESULT 信号 | Orchestrator 行为 |
|------|-------------------|------------------|
| Subagent 正常完成 | `status: success` | 进入下一阶段 |
| Subagent 需要用户输入 | `status: needs_input` | 暂停，通过 AskUserQuestion 转达 `blocking_issues` |
| Subagent 执行失败 | `status: failed`, `needs_retry: true` | 重试一次（最多 1 次重试） |
| Subagent 执行失败 | `status: failed`, `needs_retry: false` | 记录到 `workflow/status.md`，报告用户 |
| AGENT-RESULT 块缺失 | 无块 | 视为 failed + needs_retry，重试一次并在 prompt 中强调输出要求 |
| AGENT-RESULT 二次缺失 | 无块 | 不可恢复，报告用户 |
| Context 超限 / 超时 | `status: partial` 或无输出 | 检查 `needs_retry`，最多重试 1 次 |

**所有错误都记录到 `workflow/status.md`**，包括时间戳、subagent 角色、错误类型和处理结果。

---

## Subagent Prompt 模板

Subagent prompt 模板独立存放在 `subagents/` 目录下：

| 角色 | 模板文件 | 职责 |
|------|---------|------|
| Writer | `subagents/writer.md` | 撰写 PRD 初稿；修订轮次时同时承担 Fixer 职责 |
| Reviewer | `subagents/reviewer.md` | 独立审查，输出结构化审查报告 |

**调度模板时**：读取对应的 `subagents/*.md` 文件，将 `{requirement}`、`{prd_type}`、`{round}` 等占位符替换为实际值，作为 Task tool 的 prompt 传入。

> 注意：原来的 Fixer 角色已合并到 Writer（round > 1）。Writer 在修订轮次会同时读取 `workflow/review-report.md` 并修复问题，不再需要单独的 Fixer subagent。

### 结果解析（AGENT-RESULT 契约）

所有 subagent 输出末尾必须包含 `AGENT-RESULT` 块（格式见 `../../../references/subagent-result-contract.md`）。

**Orchestrator 解析流程**：

1. 在 subagent 输出中搜索 `<!-- AGENT-RESULT:BEGIN -->` ... `<!-- AGENT-RESULT:END -->` 之间的 YAML
2. 提取 `status`、`verdict`（reviewer）、`p0_count`/`p1_count`（reviewer）
3. 基于 `status` 和 `verdict` 做流转判定（见下方准出判定规则）

**AGENT-RESULT 缺失处理**：

| 场景 | 处理 |
|------|------|
| 输出中无 AGENT-RESULT 块 | 视为 `status: failed`，重试一次（在重试 prompt 中强调必须输出 AGENT-RESULT） |
| 二次缺失 | 标记为不可恢复失败，报告用户 |
| YAML 解析失败 | 同上 |
| 必填字段缺失 | 同上 |

> 不再使用 `[WRITER-COMPLETE]`、`[REVIEWER-COMPLETE]`、`[FIXER-COMPLETE]` 等字符串哨兵。

---

## 进度输出格式

每个阶段开始和结束时输出：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PRD Studio] Phase 2: Writer Subagent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正在启动 Writer subagent...
- 需求：用户积分系统
- 类型：新功能（有 UI）

[等待 subagent 完成...]

✓ Writer 完成
  - PRD 已保存：workflow/prd.md
  - 进入下一阶段：Reviewer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 完成输出格式

### 准出通过

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PRD Studio 完成 - 准出通过
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRD 文件：workflow/prd.md
迭代轮次：2 轮
最终评审：P0=0, P1=1, P2=3

PRD 已准出，可进入 HLD 阶段。
建议使用 /hld-writer 继续。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 有遗留问题

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ PRD Studio 完成 - 有遗留问题
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRD 文件：workflow/prd.md
迭代轮次：3 轮（已达上限）
最终评审：P0=1, P1=2, P2=3

遗留问题：
- [P0] 成功指标缺少数据来源
- [P1] 验收标准不够具体
- [P1] 边界情况未覆盖

建议人工处理后使用 /prd-reviewer 单独审查。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
