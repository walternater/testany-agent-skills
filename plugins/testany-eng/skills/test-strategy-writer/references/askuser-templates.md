# AskUserQuestion 模板

## 1. 基线确认

```yaml
question: "请确认测试策略所依据的最新批准基线："
header: "测试基线"
multiSelect: false
options:
  - label: "当前提供的 PRD/API/HLD 就是最新基线"
    description: "可直接按当前文档编写测试策略"
  - label: "还需补充 Guardrails / ADR"
    description: "存在额外约束文档，补齐后再定策略"
  - label: "基线未冻结"
    description: "先记录草案，暂不形成正式测试策略"
```

## 2. 风险容忍度确认

```yaml
question: "本次变更最不能接受哪类失败？"
header: "风险优先级"
multiSelect: true
options:
  - label: "核心业务流程失败"
    description: "如注册、下单、支付、登录等核心路径"
  - label: "数据错误或不一致"
    description: "写错、漏写、重复写、脏数据"
  - label: "兼容性回归"
    description: "老客户端、老集成方、旧数据受影响"
  - label: "性能或稳定性下降"
    description: "响应时间、吞吐、错误率、恢复能力恶化"
```

## 3. 依赖策略确认

```yaml
question: "外部依赖在测试中优先采用哪种策略？"
header: "依赖策略"
multiSelect: false
options:
  - label: "真实依赖优先"
    description: "更接近生产，但成本更高、稳定性更受限"
  - label: "Sandbox / 测试实例优先"
    description: "兼顾真实度与可控性"
  - label: "Mock / Stub 优先"
    description: "便于覆盖异常与边界，但需补真实联调"
```
