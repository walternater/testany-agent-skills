# PyRes (Python) 模板 - 推荐

PyRes 是 Testany 推荐的 Python 测试执行器，基于 pytest。

## ZIP 结构

```
my-test.zip
├── tests/
│   └── test_api.py
└── requirements.txt (可选)
```

## Trigger 配置

```json
{
  "executor": "pyres",
  "trigger_command": ["python", "-m", "pytest", "tests/", "-v"]
}
```

## 代码模板

```python
import os
import pytest
import requests

# 环境变量
API_BASE_URL = os.getenv("API_BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def test_login_success():
    """测试用户登录成功"""
    response = requests.post(
        f"{API_BASE_URL}/api/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data

def test_login_invalid_credentials():
    """测试无效凭据登录失败"""
    response = requests.post(
        f"{API_BASE_URL}/api/login",
        json={"username": "invalid", "password": "wrong"}
    )
    assert response.status_code == 401
```

## Relay 输出

```python
def relay_output(data: dict):
    """将数据 relay 给 pipeline 中的下游 case"""
    relay_service = os.getenv("TESTANY_OUTPUT_RELAY_SERVICE")
    if relay_service:
        requests.post(relay_service, json=data)

# 使用
relay_output({"ACCESS_TOKEN": token, "USER_ID": user_id})
```

## 凭证获取

在 case metadata 里把变量声明为 `type: secrets`，并填好 `secret_ref`（`workspace_key` / `credential_safe_key` / `credential_key`）；脚本里直接读同名环境变量即可：

```python
import os

# 假设 metadata 中声明过：
#   - name: PASSWORD
#     type: secrets
#     secret_ref:
#       workspace_key: WKS
#       credential_safe_key: WKS-CS-0001
#       credential_key: test-account-password
password = os.getenv("PASSWORD")
```

> 不需要引入凭证获取 helper，也不需要额外 HTTP 调用。
>
> 如果 `credential_safe_key` / `credential_key` 未知，可在 case 注册阶段用 MCP 工具 `testany_list_credential_safes` → `testany_list_credential_keys` 查询；详细流程见 `testany-case/references/executors.md`。

## 官方文档

- [PyRes Best Practice](https://docs.testany.io/en/docs/test-case-writing-guideline-best-practice-pyres/)
