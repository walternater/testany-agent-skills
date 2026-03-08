# Test Strategy 评审清单

## 预检：脚本化门禁

- [ ] 是否先执行了 `python3 plugins/testany-eng/scripts/trace_lint.py --format json <Test Strategy 路径>`？
- [ ] 是否先执行了 `python3 plugins/testany-eng/scripts/trace_build_rtm.py --format json <PRD 路径> <Test Strategy 路径>`？
- [ ] `trace-lint` 是否通过，且未留下 blocking issue？
- [ ] `trace-build-rtm` 是否没有 `RTM001 / RTM002 / RTM003 / RTM004`？
- [ ] 是否存在 `RTM101 orphan entity`？如有，是否已评估严重度并纳入问题单？

## Gate 1：基线与范围

- `TRACEABILITY-METADATA` block 是否存在且 profile = `test-strategy-profile-v1`
- 是否标明 PRD / API / HLD / Guardrails 基线版本
- 是否明确 In-scope / Out-of-scope
- 是否明确 must-not-regress 能力
- 是否记录假设、豁免、待确认项

## Gate 2：风险覆盖与独立测试分层

- 高风险业务路径是否被覆盖
- 数据一致性、兼容性、恢复能力是否被覆盖
- 外部依赖风险是否被覆盖
- 每个高风险点是否有合理的独立测试主层
- 是否存在明显失衡或重复投入
- 是否把 unit、code-level integration、provider-side contract 错写为测试团队职责

## Gate 3：环境、数据、依赖

- 是否说明在哪些环境执行哪些类型测试
- 是否说明数据准备、隔离、清理
- 是否说明 mock / stub / real dependency 边界
- 是否说明结果判定依赖哪些观测信号
- 是否记录开发内建验证前置条件

## Gate 4：门禁与自动化

- 入口标准是否可判定
- 出口标准是否可判定
- 缺陷等级、豁免规则、owner 是否明确
- 自动化优先级是否和风险匹配
- 回归范围是否覆盖 must-not-regress
