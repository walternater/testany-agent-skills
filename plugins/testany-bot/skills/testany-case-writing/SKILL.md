---
name: testany-case-writing
description: Testany platform case 编写助手 - 将传统测试场景拆解为 Testany platform cases，并生成可注册的 case packages
argument-hint: "[需求描述]，如：根据 test spec 拆解登录场景、把订阅流程写成可上传到 Testany 的 cases"
---

# Testany Platform Case Writing

将传统测试场景拆解为 **Testany platform cases**，并生成可注册到 Testany 平台的脚本、metadata 和 ZIP 包。

用户输入: $ARGUMENTS

---

## 宿主能力适配

- 如果宿主支持 slash command，可把 `testany-case` 作为推荐注册入口，把 `testany-pipeline` 作为推荐编排入口。
- 如果宿主不支持 slash command，则直接在当前线程继续对应 workflow。

---

## 先统一心智模型

在开始之前，先按 [automation-model.md](../testany-guide/references/automation-model.md) 理解对象边界：

- 用户给出的通常是 **traditional test scenario**，也就是完整测试场景/业务验证目标。
- 本 skill 产出的是 **Testany platform case**，也就是可复用的原子自动化步骤包。
- **pipeline** 才是 Testany 的执行与编排单元。
- **trigger** 是 `Plan / Manual Trigger / Gatekeeper`，作用于 pipeline，而不是 case。

**重要结论**：
- 不要默认把“一个传统测试场景”直接写成“一个 Testany case”。
- 先判断该场景需要拆成几个 platform cases，再写脚本和 ZIP。

---

## 职责

- 消费传统测试场景输入：用户自然语言、`test-spec`、现有测试设计文档
- 判断一个场景要拆成几个 Testany platform cases
- 为每个 platform case 选择合适的 Executor
- 生成每个 platform case 的 metadata、脚本和 ZIP 包
- 产出面向下游的 **automation design / decomposition summary**

---

## 不负责的事情

- **不**负责把 case 注册到 Testany 平台；这属于 `testany-case`
- **不**负责创建/更新 pipeline；这属于 `testany-pipeline`
- **不**负责配置 Plan / Manual Trigger / Gatekeeper；这属于 `testany-trigger`

---

## 工作流程

### Phase 1: 理解输入场景

优先收集以下信息：
1. 场景目标：要验证什么业务行为或系统行为
2. 输入来源：来自 `test-spec`、用户口述，还是已有测试文档
3. 技术约束：API / UI / Java / Python / Postman / Playwright
4. 关键依赖：登录态、创建资源、清理动作、失败分支、回滚动作

### Phase 2: 先做 decomposition，再写代码

必须先判断一个传统测试场景在 Testany 平台上应拆成几个 platform cases。

优先拆成多个 platform cases 的情况：
- 某一步会产出 relay 输出给下游复用
- 某一步本身是可复用前置条件，例如登录、创建资源、清理资源
- 不同步骤需要不同 executor / runtime
- 存在条件分支、失败分支或 `expect: fail`
- 你希望主流程、校验流程、清理流程分开维护

可以保持为单个 platform case 的情况：
- 整个动作天然原子
- 不需要 relay 给下游
- 不需要条件分支或跨 case 依赖
- 单一 executor 即可稳定表达

### Phase 3: 为每个 platform case 产出 package

每个 platform case 至少要产出：
- `name`
- `description`
- `case_labels`
- `executor`
- `path` 或 `command`
- `environment_variables`
- 如需 relay：`type=output` 的输出变量
- 代码文件
- ZIP 包

### Phase 4: 明确 downstream handoff

完成 case package 后，必须显式说明：
- 本次共拆出多少个 platform cases
- 每个 case 的职责、输入、输出、executor
- 哪些 case 之间存在依赖
- 是否需要 relay
- 是否需要 `testany-pipeline` 继续编排

**强制规则**：
- 如果存在依赖、relay、条件分支、清理分支、失败分支，**必须**产出“需要后续 pipeline 编排”的结论，不能停在 ZIP。
- 即使只有一个 platform case，只要用户要的是“可执行资产”，也应明确说明后续仍需要一条 pipeline 才能在 Testany 中运行。

### Phase 5: 引导下游 workflow

- 如果用户要把 package 注册到平台：切到 `testany-case`
- 如果用户要形成可执行链路：继续到 `testany-pipeline`
- 如果用户要配置执行入口：再继续到 `testany-trigger`

---

## 推荐输出结构

### 1. Scenario Summary

- 原始传统测试场景是什么
- 为什么这样拆分

### 2. Platform Case Inventory

对每个 platform case 给出：
- 别名 / 本地文件名
- 目标动作
- executor
- 输入变量
- 输出变量
- ZIP 包路径

### 3. Automation Design Summary

- `single-case runnable?`：是否只是单个原子步骤
- `pipeline required`：默认 `yes`
- `dependencies`：A -> B -> C
- `relay map`：例如 `LOGIN.AUTH_TOKEN -> SUBSCRIBE.AUTH_TOKEN`
- `branching`：是否存在 `whenFailed` / `expect: fail`

### 4. Next Step

- 注册这些 platform cases → `testany-case`
- 组装 pipeline → `testany-pipeline`

---

## Executor 选择决策树

```
Platform case 类型
    ├─ API 调用 / Python 优先 → PyRes ✓
    ├─ API 调用 / 不想写代码 → Postman
    ├─ UI / E2E 步骤 → Playwright
    └─ Java 项目测试 → Maven 或 Gradle
```

根据选择的 Executor，参考对应模板：

| Executor | 模板文件 | 适用场景 |
|----------|---------|---------|
| PyRes | [pyres.md](./references/executors/pyres.md) | Python API 测试（推荐） |
| Postman | [postman.md](./references/executors/postman.md) | 快速 API 验证 |
| Playwright | [playwright.md](./references/executors/playwright.md) | UI/E2E 测试 |
| Maven/Gradle | [maven.md](./references/executors/maven.md) | Java 项目测试 |

> 注意：`executor` 是后端严格字符串。本 skill 涉及的取值为：`pyres`, `postman`, `playwright`, `maven`, `gradle`（平台还支持 `python`, `jmeter`）。

---

## 环境变量类型（case_meta.environment_variables.type）

| 类型 | 用途 | 示例 |
|------|------|------|
| `env` | 输入/普通配置（包括 relay 输入） | `API_BASE_URL`, `AUTH_TOKEN` |
| `output` | Relay 输出 | `ACCESS_TOKEN`, `USER_ID` |

> 约束（与平台校验一致）：
> - `type` 仅支持 `env` 与 `output`
> - `name` 必须以大写字母开头，只能包含大写字母、数字、下划线；同一 case 内必须唯一
> - `name`/`value` 不能为空或仅空白字符；如需表达“空值”，请显式填 `-`
> - 敏感凭证请使用 Secure key reference 绑定，并在代码中通过 `TESTANY_SECRETS_SERVICE` 获取

---

## Output Relay 关键规则

Relay 是 **pipeline 层编排 + case 层输出配置** 的组合能力。只有同时满足两端约束才有效。

### Output Case

- 在 case metadata 中声明 `type: output` 的变量
- 在代码中把同名 key POST 到 `TESTANY_OUTPUT_RELAY_SERVICE`

### Input Case

- 在 case metadata 中声明 `type: env` 的变量
- 在代码中作为环境变量读取

### 编排层

- 由 `testany-pipeline` 在 pipeline YAML 中配置 `relay.key` 与 `relay.refKey`
- 只有 passed 的上游 case 才能提供 relay 数据

如果你已经识别出 relay 需求，必须在输出中明确告诉下游：
- 哪个 case 产出什么变量
- 哪个 case 消费该变量
- 后续需要 `testany-pipeline` 进行 relay 编排

---

## 完成后

交付时必须告诉用户：
1. 本次传统测试场景被拆成了几个 platform cases
2. 已生成的文件列表和 ZIP 包位置
3. 哪些 case 需要注册到 Testany
4. 是否必须继续到 `testany-pipeline`
5. 如宿主支持 slash command，可建议 `/testany-case` 和 `/testany-pipeline`

---

## 参考文档

### 本地 References

- [Testany 自动化对象模型](../testany-guide/references/automation-model.md)
- [测试设计原则](./references/test-design.md)
- [Case 元数据规范](./references/case-metadata-spec.md)
- [PyRes (Python)](./references/executors/pyres.md)
- [Postman](./references/executors/postman.md)
- [Playwright](./references/executors/playwright.md)
- [Maven/Gradle](./references/executors/maven.md)

### 文档（兜底）

如果本地 references 不足以解决问题，请查阅 Testany 文档中心；当本 skill 的示例与文档不一致时，以文档为准：

- [How to Build a Testany-Compatible Test Case](https://docs.testany.io/en/docs/how-to-build-a-testany-compatible-test-case/)
- [Managing Test Case](https://docs.testany.io/en/docs/managing-test-case/)
- [Understanding Output Relay](https://docs.testany.io/en/docs/understanding-output-relay/)
