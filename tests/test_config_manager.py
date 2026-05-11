"""
Tests for config_manager.py
"""

import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from scripts.config_manager import (
    load_config,
    get_core_index_path,
    get_idea_index_path,
    get_zotero_config,
    get_write_policy,
)


def test_load_example_config():
    """Verify config.example.json can be loaded and has required sections."""
    config = load_config(SKILL_ROOT)
    assert "obsidian" in config
    assert "zotero" in config
    assert "writePolicy" in config


def test_resolve_core_index_path(tmp_path):
    """Core index path resolves to absolute path under vault."""
    config = {
        "obsidian": {
            "vaultPath": str(tmp_path),
            "coreIndex": "03-papers/00_核心文献索引.md",
            "ideaIndex": "03-papers/01_思路与问题索引.md",
        }
    }
    path = get_core_index_path(config)
    assert path == tmp_path / "03-papers/00_核心文献索引.md"


def test_resolve_idea_index_path(tmp_path):
    """Idea index path resolves to absolute path under vault."""
    config = {
        "obsidian": {
            "vaultPath": str(tmp_path),
            "coreIndex": "03-papers/00_核心文献索引.md",
            "ideaIndex": "03-papers/01_思路与问题索引.md",
        }
    }
    path = get_idea_index_path(config)
    assert path == tmp_path / "03-papers/01_思路与问题索引.md"


def test_get_zotero_config_defaults():
    """Zotero config returns defaults when fields are missing."""
    config = {"zotero": {}}
    zc = get_zotero_config(config)
    assert zc["mcpServerName"] == "zotero"
    assert zc["mcpUrl"] == "http://127.0.0.1:23120/mcp"


def test_get_zotero_config_custom():
    """Zotero config returns custom values when provided."""
    config = {"zotero": {"mcpServerName": "my-zotero", "mcpUrl": "http://custom:1234/mcp"}}
    zc = get_zotero_config(config)
    assert zc["mcpServerName"] == "my-zotero"
    assert zc["mcpUrl"] == "http://custom:1234/mcp"


def test_get_write_policy_defaults():
    """Write policy returns defaults for all keys when section is empty."""
    config = {"writePolicy": {}}
    wp = get_write_policy(config)
    assert wp["zoteroNote"] == "confirm"
    assert wp["coreIndex"] == "confirm"
    assert wp["ideaIndex"] == "confirm"
    assert wp["metadata"] == "never_by_default"


def test_missing_vault_path_raises(tmp_path):
    """Clear error when vault path doesn't exist."""
    config = {
        "obsidian": {
            "vaultPath": str(tmp_path / "nonexistent"),
            "coreIndex": "03-papers/00_核心文献索引.md",
            "ideaIndex": "03-papers/01_思路与问题索引.md",
        }
    }
    with pytest.raises(FileNotFoundError, match="Obsidian vault path does not exist"):
        get_core_index_path(config)


def test_empty_vault_path_raises():
    """Clear error when vaultPath is empty string."""
    config = {
        "obsidian": {
            "vaultPath": "",
            "coreIndex": "03-papers/00_核心文献索引.md",
            "ideaIndex": "03-papers/01_思路与问题索引.md",
        }
    }
    with pytest.raises(ValueError, match="vaultPath is empty"):
        get_core_index_path(config)
