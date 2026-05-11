"""
Ocean Literature Harbor (OLH) configuration manager.

Reads config.local.json (or falls back to config.example.json),
validates paths, and returns resolved absolute paths for Obsidian indices.
"""

import json
from pathlib import Path


def _find_skill_root() -> Path:
    """Find the skill root directory (parent of this script's directory)."""
    return Path(__file__).resolve().parent.parent


def load_config(skill_root: Path = None) -> dict:
    """
    Load configuration from config.local.json, falling back to config.example.json.

    Returns:
        dict: Configuration dictionary.

    Raises:
        FileNotFoundError: If neither config file exists.
        json.JSONDecodeError: If config file contains invalid JSON.
        ValueError: If required sections or keys are missing.
    """
    if skill_root is None:
        skill_root = _find_skill_root()

    local_config = skill_root / "config.local.json"
    example_config = skill_root / "config.example.json"

    if local_config.exists():
        with open(local_config, "r", encoding="utf-8") as f:
            config = json.load(f)
    elif example_config.exists():
        with open(example_config, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        raise FileNotFoundError(
            f"Neither config.local.json nor config.example.json found in {skill_root}. "
            "Run setup_olh_kb.py to create your configuration."
        )

    _validate_structure(config)
    return config


def _validate_structure(config: dict) -> None:
    """Validate config structure (sections and keys exist). Does NOT check file existence."""
    if "obsidian" not in config:
        raise ValueError("Missing 'obsidian' section in config.")
    for key in ("vaultPath", "coreIndex", "ideaIndex"):
        if key not in config["obsidian"]:
            raise ValueError(f"Missing 'obsidian.{key}' in config.")


def _check_vault_exists(config: dict) -> Path:
    """
    Verify vaultPath is not empty and the directory exists.
    Returns the vault Path. Raises on failure.
    """
    vault_path = config["obsidian"]["vaultPath"]
    if not vault_path:
        raise ValueError(
            "obsidian.vaultPath is empty. Run setup_olh_kb.py to configure it."
        )
    vault = Path(vault_path)
    if not vault.exists():
        raise FileNotFoundError(
            f"Obsidian vault path does not exist: {vault}\n"
            "Please check your config.local.json and update obsidian.vaultPath."
        )
    return vault


def get_core_index_path(config: dict = None) -> Path:
    """
    Resolve the absolute path to the core literature index file.

    Returns:
        Path: Absolute path to 00_核心文献索引.md

    Raises:
        ValueError: If vaultPath is empty.
        FileNotFoundError: If vault path does not exist.
    """
    if config is None:
        config = load_config()
    vault = _check_vault_exists(config)
    return vault / config["obsidian"]["coreIndex"]


def get_idea_index_path(config: dict = None) -> Path:
    """
    Resolve the absolute path to the idea index file.

    Returns:
        Path: Absolute path to 01_思路与问题索引.md

    Raises:
        ValueError: If vaultPath is empty.
        FileNotFoundError: If vault path does not exist.
    """
    if config is None:
        config = load_config()
    vault = _check_vault_exists(config)
    return vault / config["obsidian"]["ideaIndex"]


def get_zotero_config(config: dict = None) -> dict:
    """
    Get Zotero MCP configuration section.

    Returns:
        dict: Zotero config with mcpServerName, mcpUrl, noteTitlePrefix.
    """
    if config is None:
        config = load_config()
    zc = config.get("zotero", {})
    return {
        "mcpServerName": zc.get("mcpServerName", "zotero"),
        "mcpUrl": zc.get("mcpUrl", "http://127.0.0.1:23120/mcp"),
        "noteTitlePrefix": zc.get("noteTitlePrefix", "OLH Reading Note"),
    }


def get_write_policy(config: dict = None) -> dict:
    """Get write policy configuration."""
    if config is None:
        config = load_config()
    defaults = {
        "zoteroNote": "confirm",
        "coreIndex": "confirm",
        "ideaIndex": "confirm",
        "metadata": "never_by_default",
    }
    wp = config.get("writePolicy", {})
    return {k: wp.get(k, v) for k, v in defaults.items()}
