# Testany 核心概念

## 实体定义

### Case（测试用例）

**定义**：Testany 平台上的可复用原子自动化步骤包

**属性**：
- `case_key`: 8 位大写十六进制标识符（如 `A1B2C3D4`）
- `name`: 用例名称
- `runtime_uuid`: 执行环境 UUID（推荐 cloudprime）
- `case_meta`: 执行配置（trigger_method, environment_variables）
- `is_private`: 可见性控制
- `workspace_keys`: 私有 case 可见的工作空间列表

**说明**：
- Case 是平台资产，不等同于传统测试设计里的完整测试场景。
- Case 应尽量保持原子、自包含、可重复执行。
- Case 可以输出 relay 变量，供 pipeline 中的下游 case 使用。

### Pipeline（流水线）

**定义**：编排多个 case 的执行与编排单元

**属性**：
- `pipeline_key`: 格式为 `{WS_KEY}-{4-5位大写十六进制}`（如 `Y2K-0601`、`Y2K-0001A`）
- `name`: 流水线名称
- `definition`: YAML 格式的执行规则定义（Pipeline YAML）
- `case_keys`: Case keys 列表（可替代 `definition`）
- 支持依赖关系（whenPassed/whenFailed）和变量传递（relay）

**说明**：
- Testany 平台执行的是 Pipeline，而不是单条 Case。
- 即使只有一个 Case，要真正执行也仍然需要一条 Pipeline。

### Execution（执行）

**定义**：一次测试运行的实例

**属性**：
- `execution_id`: 格式为 `{pipeline_key}-{5位大写十六进制}`（如 `Y2K-0601-0000A`）
- `status`: NOT_STARTED(-1), RUNNING(0), SUCCESS(1), FAILURE(2), SKIPPED(3), FAIL_AS_EXPECTED(4), CANCELLED(5), ERROR(99)

**说明**：
- execution 是 trigger 发起之后生成的运行实例
- execution 的观测、刷新、取消、历史查询属于 `testany-execution`

### Plan（定时计划）

**定义**：自动化调度的执行计划

**属性**：
- `plan_key`: 格式为 `P-{workspace_key}-{5位大写十六进制}`（如 `P-Y2K-0001A`）
- 关联多个 pipeline（按配置顺序触发）
- `schedule_expr`: 标准 5 段 Cron（UNIX）`分 时 日 月 周`
- `timezone`: 时区（为空时后端默认 `Asia/Shanghai`）
- watchers / notify_ignore_success：通知相关配置（可选）

### Manual Trigger（手动触发）

**定义**：按需执行一个或多个 pipeline 的触发模板

**属性**：
- `manual_trigger_key`: 格式为 `M-{workspace_key}-{4~5位大写十六进制}`
- 关联一个或多个 pipeline
- 支持按需发起执行，不依赖定时调度或外部 webhook
- Owner 与实际执行人是两个不同概念

**说明**：
- Manual Trigger 是持久化 trigger 资源
- 它不等于“现在立刻执行一次”的 ad-hoc run

### Gatekeeper（Webhook 触发器）

**定义**：通过 Webhook 触发一个“Pipeline Group”（一组 pipelines）执行的触发器

**属性**：
- `gatekeeper_key`: 格式为 `G-{workspace_key}-{5位大写十六进制}`（如 `G-Y2K-0001A`）
- 绑定 pipelines（通过 Pipeline Group 绑定；未绑定时 webhook 会报错 “no pipelines in gatekeeper”）
- `hook_url`: Webhook URL（用于外部系统触发）
- trigger_method / trigger_name / trigger_condition：触发条件的描述信息（便于团队理解与维护）
- watchers / notify_ignore_success / owned_by：通知与归属配置

### Workspace（工作空间）

**定义**：资源隔离和权限控制单元

**属性**：
- `workspace_key`: 3 位大写字母数字（如 `Y2K`）
- 角色：Owner > Admin > Member > Viewer

---

## 可见性规则

### Case / Pipeline 可见性

| 类型 | `is_private` | `workspace_keys` | 可见范围 |
|------|-------------|------------------|----------|
| **Global** | `false` | `[]`（空数组） | 全组织可见 |
| **Private** | `true` | `["WS1", "WS2"]` | 仅指定工作空间可见 |

### 使用建议

- **Global**：共享工具类测试、组织级标准用例
- **Private**：团队专属测试、开发中的用例、含敏感数据的测试

---

## 工作空间角色权限

| 角色 | 权限范围 |
|------|---------|
| **Owner** | 完全控制，包括删除工作空间、管理成员 |
| **Admin** | 管理资源，创建/编辑/删除 case、pipeline、plan |
| **Member** | 执行测试、查看结果、有限编辑 |
| **Viewer** | 只读访问 |

---

## 执行状态码

| 状态 | 值 | 含义 | 是否终态 |
|------|-----|------|---------|
| NOT_STARTED | -1 | 未开始/排队中 | 否 |
| RUNNING | 0 | 执行中 | 否 |
| SUCCESS | 1 | 全部通过 | 是 |
| FAILURE | 2 | 有失败 | 是 |
| SKIPPED | 3 | 跳过（仅 Case） | 是 |
| FAIL_AS_EXPECTED | 4 | 预期失败（仅 Case） | 是 |
| CANCELLED | 5 | 已取消 | 是 |
| ERROR | 99 | 系统错误 | 是 |
