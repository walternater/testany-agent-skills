# Case Visibility Policy

Testany case 可见性的权威文档。凡是涉及 case 创建 / 更新 / 批量更新 / Git 导入的 skill 都链回本文档，不要在各自 skill 内复述规则。

---

## 1. Visibility 模型

`TCase` 上两个字段共同决定可见性：

| 字段 | 类型 | 含义 |
|---|---|---|
| `is_private` | boolean | `false` = global（全租户可见）；`true` = restricted（仅指定 workspace 可见） |
| `workspace_keys` | `List<String>` | `is_private=true` 时**必填**；列出可见的 workspace |

### 合法组合

| `is_private` | `workspace_keys` | 含义 | 合法性 |
|---|---|---|---|
| `false` | `[]` | **Global case** — 任意 workspace 可见 | 仅 `deployment_type=1` |
| `true` | 非空 | **Restricted case** — 仅列出的 workspace 可见 | 任意 deployment_type |
| `true` | `[]` | 非法 | API 返回 `workspace_keys is required when visibility is restricted.` |
| `false` | 非空 | 语义冲突 | API 以 `is_private` 为准，`workspace_keys` 被忽略 |

---

## 2. `deployment_type` 约束

`deployment_type` 是 **tenant 级**属性，一个租户内所有 workspace 共享。Agent 通过 `testany_get_tenant_config()` 获取。

### 两种部署形态

| `deployment_type` | 特征 |
|---|---|
| `1` | 单租户；tenant-level credit 池 |
| `2` | 每个 workspace 独立 credit；没有 tenant-level credit |

### Visibility 规则矩阵

| 操作 | `type=1` | `type=2` |
|---|---|---|
| 新建 restricted（`is_private=true`） | ✅ | ✅ |
| 新建 global（`is_private=false`） | ✅ | ❌ `E400001` |
| 已有 restricted case 保持 restricted | ✅ | ✅ |
| 已有 restricted case 改为 global | ✅ | ❌ `E400001` |
| 已有 **legacy** global case（创建于 type=1，租户后转 type=2） | ✅ | ✅ 保留 |
| Bulk update 批量 `private → global` | ✅ | ❌ 每个受约束 case 都会被拒 |

### 错误码

| 错误码 | 返回消息 | 触发场景 |
|---|---|---|
| `E400001` | `When deployment_type != 1, global visibility (is_private=false) is not allowed for new cases.` | type=2 下新建 global case |
| `E400001` | `When deployment_type != 1, changing visibility from private to global (is_private=false) is not allowed.` | type=2 下 restricted → global |
| `E400001` | `When deployment_type != 1, changing visibility from private to global (is_private=false) is not allowed for cases <keys>.` | Bulk update 同上，列出受影响 case keys |
| `E400001` | `workspace_keys is required when visibility is restricted.` | `is_private=true` 但 `workspace_keys` 为空 |
| `E999001` | `Failed to resolve deployment_type for case visibility validation.` | credit 服务不可达 |

---

## 3. Agent 执行流程

### 决定可见性的标准步骤

1. **调 `testany_get_tenant_config()`** 拿到 `deployment_type`
   - Session 级缓存：tenant 属性在一个 session 内不会变
2. 根据 `deployment_type` + 用户意图决定：

| 用户意图 | `type=1` | `type=2` |
|---|---|---|
| 未明确 / 说不清楚 | **默认 global**（`is_private=false`，`workspace_keys=[]`），无需让用户挑 workspace | **降级为 restricted**（`is_private=true` + 收集 `workspace_keys`），因为 type=2 不允许 global |
| 明确要 global | `is_private=false`，`workspace_keys=[]` | 告知用户 "本租户是 workspace-scoped 部署，新 case 不能 global"，降级到 restricted |
| 明确要 restricted | `is_private=true` + 收集 `workspace_keys` | 同左 |

3. **不要**自作主张推断 deployment_type（例如"看到多个 workspace 就猜是 type=2"）。始终以 `testany_get_tenant_config` 为准。

### 撞 `E400001` 的恢复

如果代码路径意外撞上 `E400001`（例如用户在会话中途切换了 tenant，或 session 缓存过期）：
1. 重新调 `testany_get_tenant_config()` 刷新
2. 向用户解释 visibility 约束
3. 改为 `is_private=true` + 问 `workspace_keys`，重试

---

## 4. Skill 作者 checklist

引用本文档的 skill 应当：

- [ ] 在涉及 `is_private` / `workspace_keys` 的字段表里链回本文档，而不是复制规则
- [ ] 不要出现"Global: 共享工具类测试"之类的建议语 — 这在 type=2 环境下是反向诱导
- [ ] Create / update / bulk update 路径都提 deployment_type preflight
- [ ] 默认策略：`deployment_type=1` 走 **global**（不打扰用户）；`deployment_type=2` 走 **restricted + `workspace_keys`**（因为该部署不允许 global）

---

## 5. Skill 引用点

| Skill | 引用位置 |
|---|---|
| `testany-case` | `SKILL.md` Create 字段表、`references/concepts.md` 可见性规则 |
| `testany-import-git` | `SKILL.md` `selected_files` 组装 |
| `testany-case-writing` | 当前无引用；未来涉及 visibility 建议时链回本文档 |
