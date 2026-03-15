"""Tests for xhs_cli.utils.envelope"""
from xhs_cli.utils.envelope import SCHEMA_VERSION, error_envelope, success_envelope


class TestEnvelope:
    def test_success(self):
        env = success_envelope({"items": [1, 2]})
        assert env["ok"] is True
        assert env["schema_version"] == SCHEMA_VERSION
        assert env["data"] == {"items": [1, 2]}

    def test_error(self):
        env = error_envelope("mcp_error", "connection refused")
        assert env["ok"] is False
        assert env["error"]["code"] == "mcp_error"

    def test_success_none(self):
        env = success_envelope(None)
        assert env["ok"] is True
        assert env["data"] is None
