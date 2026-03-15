"""Tests for xhs_cli.utils.config"""
import os

import pytest

from xhs_cli.utils import config


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    cfg_dir = str(tmp_path / ".xhs")
    monkeypatch.setattr(config, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", os.path.join(cfg_dir, "config.json"))
    yield cfg_dir


class TestLoadSave:
    def test_default_config(self):
        cfg = config.load_config()
        assert cfg["default"]["engine"] == "auto"

    def test_save_and_load(self):
        cfg = config.load_config()
        cfg["mcp"]["proxy"] = "http://test:8080"
        config.save_config(cfg)
        loaded = config.load_config()
        assert loaded["mcp"]["proxy"] == "http://test:8080"

    def test_save_creates_dir(self, tmp_config):
        assert not os.path.isdir(tmp_config)
        config.save_config(config.DEFAULT_CONFIG)
        assert os.path.isfile(os.path.join(tmp_config, "config.json"))


class TestGetSet:
    def test_get_nested(self):
        config.save_config(config.DEFAULT_CONFIG)
        assert config.get("default.engine") == "auto"

    def test_get_missing(self):
        assert config.get("no.key", "fb") == "fb"

    def test_set_value(self):
        config.save_config(config.DEFAULT_CONFIG)
        config.set_value("mcp.port", 9999)
        assert config.get("mcp.port") == 9999


class TestDeepMerge:
    def test_merge(self):
        base = {"a": 1, "b": {"x": 10, "y": 20}}
        override = {"b": {"y": 99}}
        result = config._deep_merge(base, override)
        assert result["a"] == 1
        assert result["b"]["x"] == 10
        assert result["b"]["y"] == 99
