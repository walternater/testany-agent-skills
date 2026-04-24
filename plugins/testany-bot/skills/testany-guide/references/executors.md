# Executor 配置详解

## Executor 选择规则

根据脚本语言/框架自动选择 executor：

| 脚本类型 | 默认 Executor | 判断依据 |
|---------|--------------|----------|
| Python (.py) | `pyres` | Python 脚本默认使用 pyres（推荐） |
| Java | `maven` | 有 `pom.xml` 则使用 maven |
| Java | `gradle` | 有 `build.gradle` 则使用 gradle |
| Postman | `postman` | `.postman_collection.json` 文件 |
| Playwright | `playwright` | `.spec.js` / `.spec.ts` 文件 |

**注意**：`python` 和 `pyres` 的区别是 pyres 提供更丰富的测试报告能力，推荐使用 `pyres`。

---

## Postman

**Executor**: `postman`

| 字段 | 必填 | 说明 |
|------|-----|------|
| `executor` | 是 | 固定值 `postman` |
| `trigger_path` | 是 | Collection JSON 在 ZIP 中的相对路径 |

```json
{
  "case_meta": {
    "trigger_method": {
      "executor": "postman",
      "trigger_path": "my-collection.postman_collection.json"
    }
  }
}
```

**ZIP 结构**：
```
my-case.zip
└── my-collection.postman_collection.json
```

---

## Python / PyRes

**Executor**: `pyres`（推荐）或 `python`

| 字段 | 必填 | 说明 |
|------|-----|------|
| `executor` | 是 | `pyres`（推荐）或 `python` |
| `trigger_command` | 是 | 命令数组，空格连接执行 |

```json
{
  "case_meta": {
    "trigger_method": {
      "executor": "pyres",
      "trigger_command": ["python", "test_api.py", "--env", "staging"]
    }
  }
}
```

执行命令：`python test_api.py --env staging`

**ZIP 结构**：
```
my-case.zip
├── test_api.py
└── utils/
    └── helpers.py
```

**高级用法** - 嵌套目录执行：
```json
{
  "trigger_command": ["cd", "tests", ";", "python", "run_all.py"]
}
```

---

## Maven

**Executor**: `maven`

| 字段 | 必填 | 说明 |
|------|-----|------|
| `executor` | 是 | 固定值 `maven` |
| `trigger_path` | 是 | 测试文件路径或 `./` 表示项目根目录 |

```json
{
  "case_meta": {
    "trigger_method": {
      "executor": "maven",
      "trigger_path": "./"
    }
  }
}
```

**指定测试文件**：
```json
{
  "trigger_path": "src/test/java/com/testany/LoginTest.java"
}
```

**ZIP 结构**：
```
my-case.zip
├── pom.xml
└── src/
    └── test/
        └── java/
            └── com/testany/LoginTest.java
```

---

## Gradle

**Executor**: `gradle`

配置与 Maven 类似，区别在于项目根目录有 `build.gradle` 而非 `pom.xml`。

```json
{
  "case_meta": {
    "trigger_method": {
      "executor": "gradle",
      "trigger_path": "./"
    }
  }
}
```

---

## Playwright

**Executor**: `playwright`

| 字段 | 必填 | 说明 |
|------|-----|------|
| `executor` | 是 | 固定值 `playwright` |
| `trigger_path` | 是 | spec 文件相对路径 |
| `playwright_config_path` | 否 | 配置文件路径，省略则自动检测 |

```json
{
  "case_meta": {
    "trigger_method": {
      "executor": "playwright",
      "trigger_path": "tests/e2e/login.spec.js",
      "playwright_config_path": "playwright.config.js"
    }
  }
}
```

**必需文件**：
- `package.json`
- `playwright.config.js`（或在 `playwright_config_path` 指定）

**ZIP 结构**：
```
my-case.zip
├── package.json
├── playwright.config.js
└── tests/
    └── e2e/
        └── login.spec.js
```

---

## 环境变量类型

| type | 用途 | 如何填 |
|------|------|-------|
| `env`（默认） | 普通环境变量、relay 输入 | 填 `value`（必填、非空） |
| `output` | 输出变量，供 pipeline 中其他 case relay 消费 | 填 `value`（运行时由脚本写入，初始可用 `"-"` 占位） |
| `secrets` | 引用 workspace 的 Credential Safe 条目 | 填 `secret_ref`（**禁止**填 `value`）；脚本里直接读同名环境变量即可 |

**`secret_ref` 结构**：`{ workspace_key, credential_safe_key, credential_key }`，三个字段都必填。

**`secrets` 行的只读字段**：读回时每条 `secrets` 行附带 `status`（`valid` / `blocked` / `invalid`）和 `status_reasons[]`；非 `valid` 要向用户说明原因。写入时不要传这两个字段。

**配置示例**：
```json
{
  "case_meta": {
    "environment_variables": [
      { "name": "API_URL", "type": "env", "value": "https://api.example.com" },
      {
        "name": "API_KEY",
        "type": "secrets",
        "secret_ref": {
          "workspace_key": "WKS",
          "credential_safe_key": "WKS-CS-0001",
          "credential_key": "prod-api-key"
        }
      },
      { "name": "TOKEN", "type": "output", "value": "-" }
    ]
  }
}
```
