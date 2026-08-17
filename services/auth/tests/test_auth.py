import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from services.auth.src.main import app, PermissionChecker

client = TestClient(app)

def test_permission_checker_allowed():
    # Mock user with the required permission
    user = {"sub": "test_user", "permissions": ["auth:manage"]}
    checker = PermissionChecker("auth:manage")

    # Since __call__ is async, we can't call it directly with a sync test
    # but we can test the logic inside it or use pytest-asyncio
    import asyncio
    result = asyncio.run(checker(user))
    assert result == user

def test_permission_checker_forbidden():
    # Mock user without the required permission
    user = {"sub": "test_user", "permissions": ["some:other"]}
    checker = PermissionChecker("auth:manage")

    import asyncio
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(checker(user))

    assert excinfo.value.status_code == 403
    assert "Missing required permission" in excinfo.value.detail
