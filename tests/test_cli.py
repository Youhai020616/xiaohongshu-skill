"""Tests for CLI commands (no network)."""
from click.testing import CliRunner

from xhs_cli.main import cli

runner = CliRunner()


class TestCLI:
    def test_version(self):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "xhs-cli" in result.output

    def test_help(self):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "小红书" in result.output

    def test_all_commands_registered(self):
        result = runner.invoke(cli, ["--help"])
        for cmd in [
            "search", "detail", "publish", "like", "favorite",
            "comment", "reply", "feeds", "me", "profile",
            "analytics", "notifications", "login", "logout",
            "status", "server", "account", "config", "init",
        ]:
            assert cmd in result.output, f"'{cmd}' not in help"


class TestSubcommandHelp:
    SUBCOMMANDS = [
        ["search", "--help"],
        ["detail", "--help"],
        ["publish", "--help"],
        ["like", "--help"],
        ["favorite", "--help"],
        ["comment", "--help"],
        ["reply", "--help"],
        ["feeds", "--help"],
        ["me", "--help"],
        ["profile", "--help"],
        ["analytics", "--help"],
        ["notifications", "--help"],
        ["login", "--help"],
        ["logout", "--help"],
        ["status", "--help"],
        ["server", "--help"],
        ["account", "--help"],
        ["config", "--help"],
        ["config", "show", "--help"],
        ["init", "--help"],
    ]

    def test_all_help(self):
        for args in self.SUBCOMMANDS:
            result = runner.invoke(cli, args)
            assert result.exit_code == 0, f"'{' '.join(args)}' failed: {result.output}"


class TestAliases:
    def test_s(self):
        r = runner.invoke(cli, ["s", "--help"])
        assert "搜索" in r.output

    def test_r(self):
        r = runner.invoke(cli, ["r", "--help"])
        assert "详情" in r.output

    def test_read(self):
        r = runner.invoke(cli, ["read", "--help"])
        assert "详情" in r.output

    def test_pub(self):
        r = runner.invoke(cli, ["pub", "--help"])
        assert "发布" in r.output

    def test_fav(self):
        r = runner.invoke(cli, ["fav", "--help"])
        assert "收藏" in r.output

    def test_noti(self):
        r = runner.invoke(cli, ["noti", "--help"])
        assert "通知" in r.output

    def test_cfg(self):
        r = runner.invoke(cli, ["cfg", "--help"])
        assert "配置" in r.output

    def test_acc(self):
        r = runner.invoke(cli, ["acc", "--help"])
        assert "账号" in r.output

    def test_srv(self):
        r = runner.invoke(cli, ["srv", "--help"])
        assert "MCP" in r.output
