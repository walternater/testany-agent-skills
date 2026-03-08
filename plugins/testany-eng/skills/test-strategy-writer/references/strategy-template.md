# Test Strategy 模板

```markdown
# 测试策略：{项目/功能名称}

<!-- TRACEABILITY-METADATA:BEGIN -->
```yaml
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: test-strategy-profile-v1
artifact:
  id: TSTRAT-[DOMAIN]-001
  type: TEST_STRATEGY
  title: {项目/功能名称}
  status: draft
  owners: []
  created_at: YYYY-MM-DD
  updated_at: YYYY-MM-DD
  source_documents: []
entities:
  requirements: []
  risks: []
  must_not_regress: []
  external_behaviors: []
  decisions: []
  flows: []
  test_cases: []
relations: []
waivers: []
```
<!-- TRACEABILITY-METADATA:END -->

## 基本信息

- **PRD 基线**：{路径} v{版本}
- **API Contract 基线**：{路径} v{版本}
- **HLD 基线**：{路径} v{版本}
- **Guardrails**：{路径} / N/A
- **编写时间**：{YYYY-MM-DD}
- **状态**：Draft / Reviewed / Approved

## 上下文收集报告

### 已确认基线
- {基线 1}
- {基线 2}

### 关键约束
- {约束 1}
- {约束 2}

### 已识别风险
- {风险 1}
- {风险 2}

## 测试目标

- {目标 1}
- {目标 2}

## 范围

### In-scope
- {内容}

### Out-of-scope
- {内容}

### Must-not-regress
- {能力/流程}

## 质量风险清单

| 风险 ID | 风险描述 | 来源基线 | 影响 | 概率 | 优先级 |
|---------|----------|----------|------|------|--------|
| RISK-XXX-001 | {描述} | PRD/HLD/API | 高/中/低 | 高/中/低 | 高/中/低 |

## 独立测试层分配矩阵

| 风险/能力 | System Integration | E2E / Journey | Regression | Compatibility | Non-functional | Owner |
|-----------|--------------------|---------------|------------|---------------|----------------|-------|
| {能力/风险} | 主/辅/否 | 主/辅/否 | 主/辅/否 | 主/辅/否 | 主/辅/否 | {角色} |

## 环境、数据、依赖策略

### 环境策略
- {环境说明}

### 数据策略
- {数据准备/隔离/清理}

### 依赖策略
- {mock/stub/real dependency 边界}

### 观测与验证
- {日志/指标/trace/DB/事件}

## 开发内建验证前置条件

- **Unit Test**：由开发负责，状态/要求：{说明}
- **Code-level Integration Test**：由开发负责，状态/要求：{说明}
- **Provider-side Contract Test**：由开发或 SDET 负责，状态/要求：{说明}
- **说明**：以上内容仅记录为上游前置条件，不在本测试策略的设计与门禁范围内

## 入口标准

- {标准 1}
- {标准 2}

## 出口标准

- {标准 1}
- {标准 2}

## 自动化与回归策略

### Smoke
- {内容}

### Critical Regression
- {内容}

### Compatibility Regression
- {内容}

## 假设、豁免、待确认项

| 类型 | 内容 | 影响 | Owner | 截止时间 |
|------|------|------|-------|----------|
| 假设/豁免/待确认 | {描述} | {影响} | {人/角色} | {日期} |
```
