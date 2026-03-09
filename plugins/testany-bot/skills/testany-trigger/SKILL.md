---
name: testany-trigger
description: Testany 触发入口配置 - 为 pipeline 配置 Plan、Manual Trigger、Gatekeeper
---

# Testany Trigger

配置 Testany 平台上的 **trigger**。

用户输入: $ARGUMENTS

---

## 先统一心智模型

在开始之前，先按 [automation-model.md](../testany-guide/references/automation-model.md) 理解边界：

- `pipeline` 是执行与编排单元
- `trigger` 是执行入口
- trigger 作用于 pipeline，不负责 pipeline 内部的依赖和 relay

当前 Testany 的三类 trigger：
- `Plan`：定时执行
- `Manual Trigger`：按需执行
- `Gatekeeper`：Webhook / 外部事件触发

---

## 职责范围

- 创建/查询/更新/删除 Plan（定时计划）
- 创建/查询/更新/删除 Gatekeeper（Webhook 触发器）
- 覆盖 Manual Trigger 的平台概念、适用场景和当前支持路径
- 为已有 pipeline 提供合适的触发入口建议
- 提供可复制的 Webhook / CI 集成示例

---

## MCP 支持现状

| Trigger 类型 | 平台能力 | 当前 MCP 支持 | 本 skill 的处理方式 |
|-------------|---------|--------------|--------------------|
| Plan | 完整 | 有 | 直接通过 MCP CRUD |
| Gatekeeper | 完整 | 有，但 pipeline 绑定可能仍需 UI fallback | 直接通过 MCP CRUD，必要时补 UI fallback |
| Manual Trigger | 平台已支持 | 当前未看到对应 MCP tools | 明确纳入 trigger 体系；若当前宿主/MCP 无工具，则指导用户走 UI fallback |

---

## 操作速查

### Plan / Gatekeeper（MCP 可直连）

| 用户意图 | 操作类型 | MCP 工具 |
|---------|---------|---------|
| 列出 Gatekeepers | Read | `testany_list_gatekeepers` |
| 查看 Gatekeeper 详情 | Read | `testany_get_gatekeeper` |
| 创建 Gatekeeper | Create | `testany_create_gatekeeper` |
| 更新 Gatekeeper 字段 | Update | `testany_update_gatekeeper` |
| 删除 Gatekeeper | Delete | `testany_delete_gatekeeper` |
| 列出 Plans | Read | `testany_list_plans` |
| 查看 Plan 详情 | Read | `testany_get_plan` |
| 创建 Plan | Create | `testany_create_plan` |
| 更新 Plan | Update | `testany_update_plan` |
| 删除 Plan | Delete | `testany_delete_plan` |
| 转移 Plan Owner | Update | `testany_assign_plan` |

常用辅助：
- `testany_get_my_workspaces`
- `testany_list_pipelines`

### Manual Trigger（当前按平台概念纳入）

当前未看到对应 MCP tools 时：
- 先帮助用户确定要绑定的 pipelines
- 帮助用户准备名称、描述、目标 workspace
- 指导用户去 Testany UI 创建 Manual Trigger

---

## Trigger 选择原则

| Trigger | 适用场景 |
|--------|---------|
| Plan | 固定时间自动执行，如夜间回归、定时巡检 |
| Manual Trigger | 人工按需执行，如修复后复测、发布前验收 |
| Gatekeeper | 外部事件驱动执行，如 CI/CD、告警、Webhook |

---

## Plan（定时计划）

### 定义

Plan 用于按固定 schedule 自动触发一个或多个 pipeline。

### 创建流程

1. `testany_get_my_workspaces` → 选择 workspace
2. `testany_list_pipelines` → 选择要定时执行的 pipelines
3. `testany_create_plan` → 创建计划

建议同时填写：
- `schedule_expr`
- `timezone`
- `schedule_str`
- `watchers`

### 更新注意事项

Plan 更新应视为高风险“覆盖式更新”：
1. `testany_get_plan` 先读取现有配置
2. 基于现有配置构造完整 payload
3. 再调用 `testany_update_plan`

---

## Manual Trigger（按需执行）

### 定义

Manual Trigger 用于按需执行一个或多个 pipeline，不依赖定时调度，也不依赖外部 webhook。

### 典型场景

- 热修复上线前快速回归
- 环境恢复后立即复测关键链路
- 人工发起标准化多 pipeline 验收

### 当前 skill 的处理方式

如果当前 MCP/宿主没有 Manual Trigger 工具：
1. 先帮助用户确定 workspace 和 pipelines
2. 给出建议的 Manual Trigger 名称、描述和 pipeline 列表
3. 提示用户到 Testany UI 创建
4. 如用户需要，再继续帮助解释执行入口和结果查看方式

---

## Gatekeeper（Webhook / 事件驱动）

### 定义

Gatekeeper 通过 Webhook 触发一个 pipeline group 的执行。

### 重要澄清

- Gatekeeper 不是 pipeline 编排工具
- Gatekeeper 也不是“通过率阈值”配置中心
- “是否放行部署”属于外部 CI/CD 逻辑，应在调用 Gatekeeper 之后依据执行结果自行决定

### 创建流程

1. `testany_get_my_workspaces` → 选择 workspace
2. `testany_list_pipelines` → 选择要触发的 pipelines
3. `testany_create_gatekeeper` → 创建 Gatekeeper
4. 绑定 pipelines 到 Gatekeeper
   - 优先使用 MCP 的 pipeline-group 绑定工具（如果已提供）
   - 如果 MCP 暂不支持绑定：提示用户去 UI 绑定
5. `testany_update_gatekeeper` → 配置 trigger_method / trigger_name / trigger_condition / watchers / owned_by

### Webhook URL 获取

如果 MCP 返回了 `hook_url`，直接使用。  
如果当前返回为空或仅有局部信息，则提示用户从 UI 复制完整 Webhook URL。

---

## CI/CD 集成示例

### GitHub Actions

```yaml
- name: Trigger Testany Gatekeeper
  run: |
    curl -X POST "${{ secrets.TESTANY_GATEKEEPER_WEBHOOK_URL }}" \
      -H "Content-Type: application/json" \
      -d '{"source":"github-actions"}'
```

### Jenkins

```groovy
stage('Quality Gate') {
    steps {
        sh '''
          curl -X POST "${TESTANY_GATEKEEPER_WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d '{"source":"jenkins"}'
        '''
    }
}
```

### GitLab CI

```yaml
quality_gate:
  stage: test
  script:
    - |
      curl -X POST "$TESTANY_GATEKEEPER_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d '{"source":"gitlab-ci"}'
```

---

## 返回格式

任务完成后，向用户汇报：
- Trigger 类型：`Plan / Manual Trigger / Gatekeeper`
- 目标 pipelines 列表
- MCP 直连还是 UI fallback
- 关键配置（schedule_expr、timezone、watchers、trigger_name 等）
- Webhook URL（如可获取）
- 下一步如何执行或查看结果

---

## 参考文档

- [Testany 自动化对象模型](../testany-guide/references/automation-model.md)
- [核心概念](../testany-guide/references/concepts.md)
