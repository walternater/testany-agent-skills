# Git Connection 健康检查与修复

Testany Git 连接的健康状态由**两条独立维度**决定：

1. **配置层**：`status`（Testany 内部的 OAuth / scope 状态机）
2. **凭证层**：`token_expires_at`（GitHub 侧颁发的 access_token 有效期）

必须**两条都检查**。只看 `status` 是**滞后指标** —— access_token 单纯到期时 `status` 仍显示 `connected_scope_ready`，直到下一次实际用 token 的 API 失败后才翻成 `token_expired`。

---

## 1. `ConnectionView` 响应字段

顶层字段：

| 字段 | 说明 |
|---|---|
| `id` | 连接 uuid |
| `user_id` | Testany 操作者 |
| `platform` | `github`（Phase 1 只支持 GitHub） |
| `platform_user_id` / `platform_username` / `platform_avatar_url` | GitHub 侧身份信息 |
| `status` | **配置层健康状态**，枚举见 §2 |
| `not_ready_reason` | `status` 非 ready 时的可读原因（可为 null） |
| `scope_management_entry_url` | 平台侧 scope 管理入口（通常是 GitHub App installations 页面） |
| `installation_bindings[]` | GitHub App installation 列表，见 §3 |
| `token_expires_at` | **凭证层** —— access_token 过期时刻（ISO-8601） |
| `created_at` / `updated_at` | 创建 / 最近更新时间 |

---

## 2. `status` 枚举

| 值 | 含义 | 对应修复路径 |
|---|---|---|
| `connected_scope_ready` | ✅ **一切就绪**（健康值） | — |
| `authorized_no_installation` | OAuth 完成但还没装 GitHub App installation | 用户去 `scope_management_entry_url` 浏览器装 installation |
| `token_expired` | Token refresh 失败，access_token 无法续期 | `testany_reauthorize_git_connection`（浏览器） |
| `permission_changed` | GitHub 侧 scope / repo 选择被改 / 撤销 | 优先 `refresh_connection_scope`；若不行再 `reauthorize` |
| `disconnected` | 用户主动断开 | `testany_initiate_git_oauth` 重新授权 |

⚠️ 注意：**健康值是 `connected_scope_ready`，不是字面 `"ready"`**。代码里对字符串做相等比较时必须用完整值。

---

## 3. `installation_bindings[]` 每项字段

| 字段 | 说明 |
|---|---|
| `installation_id` | GitHub App installation 的数字 id，浏览仓库时必填 |
| `account_login` / `account_type` | 账号名 / `User` or `Organization` |
| `account_avatar_url` | 头像 URL |
| `repository_selection` | `all` 或 `selected`（GitHub App 安装时的 repo 选择模式） |
| `selected_repository_count` / `effective_repository_count` | 选择数量 / 实际可达数量 |
| `installation_html_url` | GitHub 侧 installation 管理页 |
| `scope_verified_at` | 最近一次 Testany 与 GitHub 校对 scope 的时间 |

---

## 4. 健康检查决策树

每次要访问需要实际调用 GitHub API 的 tool 前（repo browse / sync / addFiles 等），先做三项检查：

```
┌─ token_expires_at 是否存在且 > now + 60s？
│    ├─ 否 ─→ 调 refresh_connection_scope 续命（server-to-server）
│    │         ├─ 成功 ─→ 继续
│    │         └─ 失败（status 翻到 token_expired）─→ 调 reauthorize_git_connection 给用户浏览器 URL
│    └─ 是 ─→ 下一步
│
├─ status 是否 == "connected_scope_ready"？
│    ├─ authorized_no_installation ─→ 把 scope_management_entry_url 交给用户浏览器装 installation
│    ├─ token_expired              ─→ reauthorize_git_connection
│    ├─ permission_changed         ─→ refresh_connection_scope（优先），失败则 reauthorize
│    ├─ disconnected               ─→ initiate_git_oauth 重新授权
│    └─ connected_scope_ready      ─→ 继续
│
└─ 准备使用的 installation 的 scope_verified_at 是否太旧（>24h）？
     ├─ 是 ─→ 可选：refresh_connection_scope 刷新校对
     └─ 否 ─→ 继续
```

60 秒缓冲是为了避免"调用发出时还没过期、到达后端时过期"的边界窗口。

---

## 5. `reauthorize` vs `refresh_connection_scope` 的分工

这是 skill 里最容易搞混的一对。**行为本质不同**：

| Tool | 流程 | 是否需要浏览器 | 典型触发场景 |
|---|---|---|---|
| `testany_reauthorize_git_connection` | 生成新的 `authorize_url`，响应里只返回 URL | **需要** —— agent 必须把 URL 交给用户 | `status=token_expired`；refresh_token 也挂了；用户主动断开后重建 |
| `testany_refresh_git_connection_scope` | 用 refresh_token 向 GitHub 换新 access_token + 重新校对 installation scope | **不需要** —— server-to-server，agent 调完即可直接继续 | `token_expires_at` 临近过期；`status=permission_changed`；周期性健康检查 |

**推论：**
- Token 单纯到期时（refresh_token 还在），`refresh_connection_scope` 是优先选择 —— 不打扰用户
- 只有 refresh 本身失败（`refresh_token` 挂了 / scope 撤销太严重 / disconnected），才需要走 `reauthorize` 让用户浏览器重新授权

---

## 6. GitHub App token 生命周期参考

- Access token：**默认 8 小时** 过期
- Refresh token：**6 个月** 过期

只要在 refresh token 有效期内至少触发一次 `refresh_connection_scope`（或任何间接触发 server-to-server refresh 的操作），这条连接可以**长期免浏览器维护**。
