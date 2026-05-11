# Ocean Literature Harbor

文献港 — Zotero-centered, Obsidian-light 科研文献知识工作流技能。

## 触发条件

用户提及以下任意关键词时触发本技能：

- 导入文献、整理文献库、精读文献
- 记录 idea、捕捉灵感
- 查找文献证据、写作前检索文献
- 生成 Zotero Note、加入核心文献索引
- 读取论文、分析论文
- 文献港、Ocean Lit Harbor、OLH

## 设计哲学

让文献停泊在 Zotero，让思想浮出到 Obsidian，让证据流向写作。

- **Zotero 是文献总管**：保存 PDF、MinerU Markdown、Zotero Note。
- **PDF 是原始档案**：不直接用于日常检索。
- **Markdown 是纯文本检索材料**：由 MinerU 从 PDF 转换。读取时由 LLM 清理文末 References 段落后再提取信息（仅在内存中清理，不写回 MD 文件）。
- **Zotero Note 是每篇论文唯一的高信号笔记**：作为论文"外包装"，不含完整文字。
- **Obsidian 只保留两个轻量索引**（由 LLM 直接读写，无需中间脚本）：
  - `03-papers/00_核心文献索引.md`
  - `03-papers/01_思路与问题索引.md`
- **不在 Obsidian 中为每篇论文生成完整 paper note**。

## 检索顺序（固定）

1. Obsidian 两个索引
2. Zotero Notes
3. Zotero Markdown（MinerU 转换，LLM 已清理 References）
4. PDF 原文

---

## Obsidian 索引写入安全协议（最高优先级）

以下规则适用于所有 Obsidian 索引写入操作，**优先级高于工作流具体步骤**。

### 触发写入的关键词

只有用户**明确说出**以下词语时，才能进入写入确认流程：
- "记录"、"写入"、"记下来"
- "加入索引"、"加到索引"
- "保存到 Obsidian"
- "写入核心索引"、"写入 idea 索引"

### 不触发写入的场景

以下场景**绝不能**自动写入：
- 用户只说"帮我分析一下"、"看看这篇"
- 用户只是讨论文献内容
- 用户询问"这篇值不值得加入索引"
- 任何用户未明确授权的场景

### 写入 `03-papers/00_核心文献索引.md` 的强制流程

1. **Read** 当前文件完整内容。
2. **检查**是否已有相同 citekey。如有，提示用户并说明差异，询问是否仍需写入。
3. **生成**拟追加的卡片（使用 `templates/core_index_entry_template.md`，最多 5-8 行）。
4. **向用户展示**拟追加内容。
5. **明确询问**用户是否写入（不可假设同意）。
6. 用户确认后，**先创建 `.bak` 备份**（复制当前文件为 `.bak`）。
7. 用 Edit / Write 工具**增量追加**到文件末尾。
8. **不得覆盖整个文件**。

### 写入 `03-papers/01_思路与问题索引.md` 的强制流程

1. **Read** 当前文件完整内容。
2. **生成 IDEA-ID**：格式 `IDEA-YYYYMMDD-HHMMSS`。
3. **生成**拟追加的 idea 卡片（使用 `templates/idea_entry_template.md`）。
4. **向用户展示**拟追加内容。
5. **明确询问**用户是否写入。
6. 用户确认后，**先创建 `.bak` 备份**。
7. 用 Edit / Write 工具**增量追加**到文件末尾。
8. **不得覆盖整个文件**。

---

## 工作流

### 1. import_paper（导入文献）

**目标**：将一篇新文献纳入知识库，生成 Zotero Note 草稿。

**步骤**：

1. **定位文献**：通过 Zotero MCP 搜索文献 title / citekey / itemKey。
2. **检查 PDF**：获取 PDF attachmentKey。
   - 无 PDF → 提醒用户先添加 PDF。
3. **检查 MD**：获取 MinerU 转换的 Markdown attachmentKey。
   - 无 MD → 提醒用户使用 MinerU 插件转换。
4. **读取并清理 MD**：
   - 读取 MD attachment 内容。
   - **清理文末 References**：LLM 识别并丢弃文末的 References / Bibliography / 参考文献 / 参考资料段落。该段落通常在文档后半部分，以标题行开始。不要删除致谢（Acknowledgments）、附录（Appendix）、补充材料。也不要在正文中误删"references"一词。
   - 清理仅在内存中进行，不写回 MD 文件。
5. **读取 Zotero metadata**（title, authors, abstract, publication, year, DOI, volume, pages）。
6. **如有现有 Zotero Note**，读取其内容（供增量更新判断）。
7. **生成 Zotero Note 草稿**：
   - 严格使用 `templates/zotero_note_template.md` 模板（含 Meta Data 表 + 检索卡 + 研究核心 + 研究内容 + 个人总结）。
   - 生成 Meta Data 表：填入 authors / journal / volume / pages / year / DOI / pdfAttachmentKey / mdAttachmentKey / date。
   - DOI 为空时写 `[无]`，不生成坏链接。
   - 从清理后的 MD 提取方法、数据、结果细节。
   - 不确定内容标记 `[需核对]`。
   - 阅读状态设为 `imported`。
   - 使用 `prompts/read_paper_to_zotero_note.md` 作为生成指引。
8. **写入前确认**：向用户展示草稿，确认后通过 Zotero MCP 写入 Note。
   - 如果已有 Note，仅 append 或更新指定 section，不覆盖用户已有个人笔记。

### 2. deep_read_paper（精读文献）

**目标**：深度阅读一篇文献，提取关键洞察。

**步骤**：

1. **读取 Zotero Note**：获取已有笔记全文。
2. **必要时读取 MD**：当需要精确核查数据、方法细节时，读取 MinerU Markdown（先清理 References，同上）。
3. **与用户讨论**：逐 section 讨论论文内容，记录用户的判断和洞察。
4. **生成新增 insight**：
   - 个人总结部分严格区分：作者结论 / 我的判断 / 待验证问题。
   - 更新阅读状态为 `deep-read`。
5. **写入确认**：询问用户：
   - 是否写回 Zotero Note（append 或更新指定 section）？
   - 是否加入 Obsidian 核心文献索引？→ 触发 `promote_to_core_index`（遵循 Obsidian 索引写入安全协议）。
   - 是否产生新的 idea？→ 触发 `capture_idea`（遵循 Obsidian 索引写入安全协议）。

### 3. capture_idea（捕捉灵感）

**目标**：将灵感、问题、假设写入 idea 索引。

**步骤**：

1. **收集信息**：与用户对话，明确 idea 的核心内容。
2. **生成 IDEA-ID**：格式 `IDEA-YYYYMMDD-HHMMSS`。
3. **生成 idea 卡片**：使用 `templates/idea_entry_template.md` 模板和 `prompts/capture_idea.md` 指引。
4. **写入前**：严格遵循 [Obsidian 索引写入安全协议](#obsidian-索引写入安全协议最高优先级)。
5. **关联文献**：如果 idea 明确关联某篇文献，询问用户是否将 idea 追加到对应 Zotero Note 的 `💭 思考启发` 或 `📌 待解决` section。
6. **写入前必须确认**，除非用户明确说"记录"或"写入"。

### 4. answer_with_kb（基于知识库回答）

**目标**：基于知识库回答科学问题，输出 evidence cards。

**步骤**：

1. **按固定顺序检索**：
   - 先查 Obsidian 核心文献索引 → idea 索引（LLM 直接 Read 两个 .md 文件）。
   - 再查 Zotero Notes（通过 Zotero MCP 搜索）。
   - 必要时查 Zotero Markdown（全文搜索，先清理 References）。
   - 最后查 PDF 原文。
2. **不得跳过索引直接扫描所有 PDF**。
3. **输出格式**：answer + evidence cards（每条证据标注来源层级）。
4. 使用 `prompts/answer_with_kb.md` 作为生成指引。
5. **注意**：answer_with_kb 是只读检索流程，不写入任何 Obsidian 索引。如需写入，转入对应的 capture_idea 或 promote_to_core_index 流程。

---

## 安全规则

- **默认不修改** Zotero metadata。
- **默认不覆盖** Zotero Note（只 append 或更新指定 section）。
- **默认不修改** PDF 文件。
- **默认不修改** MinerU MD 原文（References 清理仅在内存中进行，不写回文件）。
- **Obsidian 索引写入必须遵循安全协议**：Read → 检查重复 → 生成卡片 → 展示给用户 → 明确确认 → .bak 备份 → 增量追加。不得覆盖整个文件。
- **用户只说"分析"不代表授权写入**。必须用户明确说"记录/写入/加入索引/保存到 Obsidian"。
- **不存储 API key 或 secret**。

---

## 依赖

- **Zotero MCP Server**：用于 Zotero 文献操作（搜索、读写 Note、获取 metadata、读取 attachment）。
- **MinerU 插件**：用于 PDF → Markdown 转换。
- **Python 3.8+**：仅用于 `config_manager.py` 和 `setup_olh_kb.py` 两个配置工具。
- **Obsidian**：用于两个索引文件的存放，由 LLM 直接读写，无需中间脚本。

## 文件结构

```
ocean-literature-harbor/
├── SKILL.md                          # 本文件
├── README.md                         # 用户文档
├── config.example.json               # 示例配置
├── .gitignore
├── prompts/                          # 工作流 prompt 指引
│   ├── read_paper_to_zotero_note.md
│   ├── promote_to_core_index.md
│   ├── capture_idea.md
│   └── answer_with_kb.md
├── templates/                        # 笔记/卡片模板
│   ├── zotero_note_template.md
│   ├── core_index_entry_template.md
│   └── idea_entry_template.md
├── scripts/                          # Python 配置工具
│   ├── setup_olh_kb.py
│   └── config_manager.py
└── tests/
    └── test_config_manager.py
```
