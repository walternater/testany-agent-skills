---
description: Testany platform case 编写，先拆解测试场景，再生成可注册的 case packages
argument-hint: <需求描述>，如：把登录场景拆成 Testany cases、根据 test spec 生成可上传 case
---

# Testany Platform Case 编写

将传统测试场景拆解为 Testany platform cases，并生成可注册的 metadata、脚本和 ZIP 包。

## 使用方式

$ARGUMENTS

## 核心动作

- **场景拆解**：先判断一个传统测试场景要拆成几个 Testany platform cases
- **case package 生成**：为每个 platform case 生成 metadata、脚本和 ZIP
- **automation design 输出**：明确后续是否需要 `testany-pipeline`

## 支持的 Executor

- **PyRes (Python)** - 推荐，适合 API 测试
- **Postman** - 无需编程，快速 API 验证
- **Playwright** - UI/E2E 测试
- **Maven/Gradle** - Java 项目测试

## 示例

```
/case-writing 写一个测试用户登录 API 的 Python 测试
/case-writing 生成 Playwright E2E 测试，测试购物车结算流程
/case-writing 创建 Postman Collection 测试支付接口
/case-writing 写一个 Java 测试，验证订单创建 API
/case-writing 根据 test spec 把订阅流程拆成可上传到 Testany 的多个 cases
```

## 输出

- platform case inventory
- Testany-compatible 测试脚本
- 可直接上传的 ZIP 包
- 面向 `testany-pipeline` 的 decomposition / handoff 摘要
