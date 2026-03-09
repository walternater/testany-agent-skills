# Testany 核心概念（Pipeline 相关）

## Pipeline（流水线）

**定义**：编排多个 case 的执行与编排单元

**属性**：
- `pipeline_key`: 格式为 `{WS_KEY}-{4-5位大写十六进制}`（如 `Y2K-0601`、`Y2K-0001A`）
- `name`: 流水线名称
- `description`: 描述
- `definition`: YAML 格式的执行规则定义
- `case_keys`: 关联的 case key 列表
- `environments`: 环境标签列表
- `creator`: 创建者（不可更新）
- `owned_by`: 所有者（可通过更新转移）
- `pipeline_labels`: Pipeline 标签列表

Pipeline 支持依赖关系（whenPassed/whenFailed）、变量传递（relay）和 `expect: fail`。

**说明**：
- Testany 平台执行的是 Pipeline，而不是单条 Case。
- 即使只有一个 Case，要真正执行也仍然需要一条 Pipeline。

---

## Case（测试用例）

**定义**：Testany 平台上的可复用原子自动化步骤包

**属性**：
- `case_key`: 8 位大写十六进制标识符（如 `A1B2C3D4`）
- `name`: 用例名称
- `case_meta`: 执行配置（trigger_method, environment_variables）

Pipeline 通过 `case_key` 引用 case。

**说明**：
- Case 不等同于传统测试语义中的完整测试场景。
- 一个传统测试场景可能会拆成多个 Cases，再由 Pipeline 编排。

---

## Execution（执行）

**定义**：一次测试运行的实例

**属性**：
- `execution_id`: 格式为 `{pipeline_key}-{5位大写十六进制}`（如 `Y2K-0601-0000A`）
- `status`: 执行状态

---

## Workspace（工作空间）

**定义**：资源隔离和权限控制单元

**属性**：
- `workspace_key`: 3 位大写字母数字（如 `Y2K`）
- Pipeline Key 的前缀来自所属 workspace

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
