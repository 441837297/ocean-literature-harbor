# Ocean Literature Harbor

文献港 — Zotero-centered, Obsidian-light 科研文献知识工作流。

让文献停泊在 Zotero，让思想浮出到 Obsidian，让证据流向写作。

**设计用于 Claude Code 环境**，通过 Zotero MCP 与 Zotero 文献库交互，LLM 直接读写 Obsidian 索引文件。

---

## Ocean Research Toolkit 全景

OLH 是 Ocean Research Toolkit 的中枢，连接 PDF 解析入口与论文写作出口：

```
┌─────────────────────────────────────────────────────────┐
│                 Ocean Research Toolkit                   │
│                    (Claude Code 环境)                     │
├───────────────┬──────────────────────┬──────────────────┤
│ mineru-plugin │ ocean-literature     │ ocean-paper      │
│               │      -harbor         │     -writer      │
├───────────────┼──────────────────────┼──────────────────┤
│ PDF → MD      │ 归档 → 封装 → 检索    │ 准备 → 方法 → 结构│
│ Zotero 附件    │                      │ 写作 → 审阅 → 润色│
│               │                      │ → 投稿信          │
├───────────────┼──────────────────────┼──────────────────┤
│ 触发方式        │ 触发方式              │ 触发方式          │
│ Zotero 右键菜单 │ Claude Code 对话     │ Claude Code 对话  │
│               │ /ocean-literature    │ /ocean-paper     │
│               │     -harbor          │     -writer      │
├───────────────┼──────────────────────┼──────────────────┤
│ 输出            │ 输出                  │ 输出              │
│ MD 附件 (Zotero)│ Zotero Note          │ 稿件 .md 文件     │
│               │ Obsidian 两个索引      │ 投稿信            │
└───────────────┴──────────────────────┴──────────────────┘
```

### 三工具分工

| 阶段 | 工具 | 做什么 | 输出在哪 |
|------|------|--------|---------|
| 1. 解析 | `zotero-mineru-plugin` | PDF → Markdown，存为 Zotero 附件 | Zotero |
| 2. 入库 | OLH `import_paper` | 读 MD + metadata → 生成结构化 Zotero Note | Zotero |
| 3. 精读 | OLH `deep_read_paper` | 逐 section 讨论 → 提取洞察 → 追加到 Note | Zotero |
| 4. 索引 | OLH `promote_to_core_index` | 将核心文献写入 Obsidian 索引卡片 | Obsidian |
| 5. 灵感 | OLH `capture_idea` | 捕捉 idea → 写入 Obsidian idea 索引 | Obsidian |
| 6. 取证 | OLH `answer_with_kb` | 按索引→Note→MD→PDF 逐层检索证据 | 对话输出 |
| 7. 写作 | `ocean-paper-writer` | 基于证据库撰写/审阅/润色/投稿 | 项目目录 |

---

## 典型工作流

### 场景 A：新论文入库

```
1. Zotero 中导入 PDF                          ← 你的操作
2. 右键 PDF → "用 MinerU 转换为 Markdown"       ← mineru-plugin，约 30-60s
3. Claude Code 中说：
   "文献港，帮我导入这篇 [citekey/title]"         ← OLH import_paper
4. OLH 读 MD + metadata → 生成 Zotero Note 草稿
5. 你确认 → Note 写入 Zotero
```

### 场景 B：精读并加入核心索引

```
1. Claude Code 中说：
   "文献港，精读这篇 [citekey]"                 ← OLH deep_read_paper
2. OLH 读已有 Note + MD → 与你逐 section 讨论
3. 讨论结束后 OLH 问：是否更新 Note / 加入核心索引？
4. 你确认 → Note 更新 + 核心索引卡片写入 Obsidian
```

### 场景 C：写作前检索证据

```
1. Claude Code 中说：
   "文献港，涡旋能量趋势有哪些模式证据？"         ← OLH answer_with_kb
2. OLH 按顺序检索：
   Obsidian 核心索引 → Zotero Notes → Zotero MD
3. 输出 answer + evidence cards（标注来源层级）
4. 拿到证据后，切换到写作：
   "ocean-paper-writer，帮我把这段证据写进 Discussion"
```

---

## 快速开始

### 前置条件

| 组件 | 用途 | 必需 |
|------|------|------|
| Zotero 7 | 文献管理 | 是 |
| Zotero MCP Server 插件 | Claude Code ↔ Zotero 通信 | 是 |
| MinerU + `zotero-mineru-plugin` | PDF → MD 转换 | 推荐 |
| Obsidian | 轻量索引存放 | 是 |
| Claude Code | 运行环境 | 是 |

### 1. 安装工具链

```bash
# mineru-plugin: 在 Zotero 中安装 mineru-converter.xpi
# 详见 https://github.com/441837297/zotero-mineru-plugin

# ocean-paper-writer: 已内置为 Claude Code Skill
```

### 2. 初始化 OLH

```bash
cd ~/.claude/skills/ocean-literature-harbor
python scripts/setup_olh_kb.py
```

按提示输入 Obsidian vault 路径。setup 会生成 `config.local.json` 并在 Obsidian 中创建两个索引文件：
- `03-papers/00_核心文献索引.md`
- `03-papers/01_思路与问题索引.md`

### 3. 开始使用

在 Claude Code 中：

```
/ocean-literature-harbor              # 斜杠命令加载 skill
文献港，帮我导入这篇 xxx               # 自然语言触发
OLH，查一下这个论点有没有文献支持       # 对话式检索
```

### 4. 运行测试

```bash
cd ~/.claude/skills/ocean-literature-harbor
pytest tests/ -v
```

---

## 设计原则

- **Zotero 是文献总管**：存储 PDF、MinerU Markdown、Zotero Note
- **Obsidian 只保留两个轻量索引**（由 LLM 直接读写），不为每篇论文生成完整 note
- **MD References 清理由 LLM 在读取时完成**，不使用正则脚本，不写回 MD 文件
- **检索顺序固定**：Obsidian 索引 → Zotero Notes → Zotero MD → PDF 原文
- **写入前必须确认**：所有 Zotero Note、Obsidian 索引写入操作需用户明确授权
- **不存储 API key 或 secret**

## 许可

MIT License
