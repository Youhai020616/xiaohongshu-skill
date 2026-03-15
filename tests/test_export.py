"""Tests for xhs_cli.utils.export"""
import csv
import json

from xhs_cli.utils.export import export_data

SAMPLE = [
    {"note_id": "aaa", "title": "笔记一", "stats": {"likes": 100}},
    {"note_id": "bbb", "title": "笔记二", "stats": {"likes": 200}},
]


class TestJson:
    def test_json(self, tmp_path):
        path = str(tmp_path / "out.json")
        export_data(SAMPLE, path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert "笔记一" in json.dumps(data, ensure_ascii=False)


class TestCsv:
    def test_csv(self, tmp_path):
        path = str(tmp_path / "out.csv")
        export_data(SAMPLE, path)
        with open(path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["note_id"] == "aaa"

    def test_csv_flattens(self, tmp_path):
        path = str(tmp_path / "out.csv")
        export_data(SAMPLE, path)
        with open(path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert "stats.likes" in rows[0]


class TestYaml:
    def test_yaml(self, tmp_path):
        path = str(tmp_path / "out.yaml")
        export_data(SAMPLE, path)
        with open(path, encoding="utf-8") as f:
            assert "note_id" in f.read()
