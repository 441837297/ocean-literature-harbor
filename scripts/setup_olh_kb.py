"""
Ocean Literature Harbor (OLH) setup script.

Interactive wizard that creates config.local.json and initializes
the two Obsidian index files (core index + idea index).

Index files are created by LLM via direct file write — this script
only creates minimal placeholder files if they don't exist.
"""

import json
import os
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG = SKILL_ROOT / "config.example.json"
LOCAL_CONFIG = SKILL_ROOT / "config.local.json"

# Minimal header for index files — LLM will populate them
CORE_INDEX_HEADER = """# 00 核心文献索引

> Ocean Literature Harbor (OLH) 知识库核心文献索引。只收录已精读、对未来写作有直接参考价值的文献。
> 每篇文献一张短卡片（5-8 行），完整笔记见 Zotero Note。
> 检索顺序：本索引 → idea 索引 → Zotero Notes → Zotero MD → PDF

---

"""

IDEA_INDEX_HEADER = """# 01 思路与问题索引

> Ocean Literature Harbor (OLH) 知识库灵感与问题索引。收录研究过程中的灵感、假设、问题、实验设计。
> 每条 idea 自动生成 IDEA-ID，关联文献标注 citekey。
> 检索顺序：核心文献索引 → 本索引 → Zotero Notes → Zotero MD → PDF

---

"""


def ask(prompt: str, default: str = "") -> str:
    """Prompt the user with a default value."""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    return input(f"{prompt}: ").strip()


def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
    """Ask a yes/no question."""
    suffix = " [Y/n]: " if default_yes else " [y/N]: "
    response = input(prompt + suffix).strip().lower()
    if not response:
        return default_yes
    return response in ("y", "yes")


def create_index_file(filepath: Path, content: str) -> bool:
    """Create an index file if it doesn't exist. Returns True if created."""
    if filepath.exists():
        print(f"  [已存在] {filepath}")
        return False
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    print(f"  [已创建] {filepath}")
    return True


def main():
    print("=" * 60)
    print("  Ocean Literature Harbor — 初始化配置")
    print("=" * 60)
    print()

    # --- Load example config ---
    if not EXAMPLE_CONFIG.exists():
        print(f"[错误] 找不到示例配置文件: {EXAMPLE_CONFIG}")
        sys.exit(1)

    with open(EXAMPLE_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)

    # --- 1. Obsidian vault path ---
    print("--- Obsidian 设置 ---")
    while True:
        vault_default = config["obsidian"]["vaultPath"] or os.path.expanduser("~/Documents/Obsidian")
        vault_path = ask("Obsidian vault 路径", vault_default)
        vault = Path(vault_path)
        if vault.exists():
            config["obsidian"]["vaultPath"] = str(vault.resolve())
            break
        print(f"  [错误] 路径不存在: {vault}")
        print("  请输入有效的 Obsidian vault 路径。")

    # --- 2. Index file paths ---
    core_default = config["obsidian"]["coreIndex"]
    idea_default = config["obsidian"]["ideaIndex"]
    core_input = ask("核心文献索引路径（相对于 vault）", core_default)
    idea_input = ask("思路与问题索引路径（相对于 vault）", idea_default)
    config["obsidian"]["coreIndex"] = core_input
    config["obsidian"]["ideaIndex"] = idea_input

    # --- 3. Zotero MCP ---
    print()
    print("--- Zotero MCP 设置 ---")
    config["zotero"]["mcpServerName"] = ask("Zotero MCP server name", config["zotero"]["mcpServerName"])
    config["zotero"]["mcpUrl"] = ask("Zotero MCP URL", config["zotero"]["mcpUrl"])
    config["zotero"]["noteTitlePrefix"] = ask("Zotero Note 标题前缀", config["zotero"]["noteTitlePrefix"])

    # --- 4. Write policy ---
    print()
    print("--- 写入策略 ---")
    print("（直接回车使用默认值 confirm）")
    for key in ("zoteroNote", "coreIndex", "ideaIndex"):
        val = ask(f"写入前确认? {key} (confirm/auto)", "confirm")
        config["writePolicy"][key] = val
    config["writePolicy"]["metadata"] = ask("Zotero metadata 写入策略 (never_by_default/confirm)", "never_by_default")

    # --- 5. Write config.local.json ---
    print()
    print("--- 保存配置 ---")
    with open(LOCAL_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"  [已保存] {LOCAL_CONFIG}")

    # --- 6. Create Obsidian index files ---
    print()
    print("--- 创建 Obsidian 索引文件 ---")
    core_path = vault / config["obsidian"]["coreIndex"]
    idea_path = vault / config["obsidian"]["ideaIndex"]
    create_index_file(core_path, CORE_INDEX_HEADER)
    create_index_file(idea_path, IDEA_INDEX_HEADER)

    # --- Done ---
    print()
    print("=" * 60)
    print("  初始化完成！")
    print(f"  Vault:      {vault}")
    print(f"  核心索引:   {core_path}")
    print(f"  Idea 索引:  {idea_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
