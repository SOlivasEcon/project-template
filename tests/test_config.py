"""Checks of how project_package.config reads paths from .env and the environment."""

from pathlib import Path

import pytest

from project_package import config


def test_empty_setting_is_none(monkeypatch):
    monkeypatch.setenv("SOME_ROOT", "  ")
    assert config.optional_path("SOME_ROOT") is None


def test_relative_path_starts_at_repo_root(monkeypatch):
    monkeypatch.setenv("SOME_ROOT", "data/raw")
    assert config.optional_path("SOME_ROOT") == config.PROJECT_ROOT / "data" / "raw"


def test_tilde_is_home(monkeypatch):
    monkeypatch.setenv("SOME_ROOT", "~/research")
    assert config.optional_path("SOME_ROOT") == Path.home() / "research"


def test_missing_required_setting_names_the_variable(monkeypatch):
    monkeypatch.delenv("SOME_ROOT", raising=False)
    with pytest.raises(RuntimeError, match="SOME_ROOT not set"):
        config.required_path("SOME_ROOT")


def test_program_variable_pointing_nowhere_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("STATA_EXE", str(tmp_path / "no-stata.exe"))
    with pytest.raises(RuntimeError, match="STATA_EXE"):
        config.program_path("stata")
