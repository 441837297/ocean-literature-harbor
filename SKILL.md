# Ocean Literature Harbor

文献港 — Zotero-centered, Obsidian-light 科研文献知识工作流技能。

## 触发条件

用户提及以下任意关键词时触发本技能：

- 处理文献、整理文献、导入文献、生成 Note
- 精读文献、deep read
- 记录 idea、捕捉灵感
- 查找文献证据、写作前检索
- 文献港、Ocean Lit Harbor、OLH

## 设计哲学

让文献停泊在 Zotero，让思想浮出到 Obsidian，让证据流向写作。

OLH 只有两个实际内容层级：

1. **Markdown 层**：Zotero `output.md` — MinerU 从 PDF 转换的纯文本检索材料。不是原始档案，References 边界明确时可清理。
2. **Note 层**：Zotero Note — 每篇论文唯一的高信号 OLH 格式笔记。不含完整文字，是用户个人精读参考，手动翻阅或精读时使用。自动检索流程（answer_with_kb）不读 Note。

- **PDF 是原始档案**：永远不修改，不直接用于日常检索。
- **Obsidian 只保留两个轻量索引**：
  - `03-papers/00_核心文献索引.md`
  - `03-papers/01_思路与问题索引.md`
- **不在 Obsidian 中为每篇论文生成完整 paper note**。

## 可用证据层级

OLH 的常规证据层级如下，但 `answer_with_kb` 不会自动一路查到底：

1. Obsidian 两个轻量索引：可选，用于快速定位和轻量背景，不作为强制第一步。
2. Zotero item metadata（Abstract）：`get_item_details(preview)` 即可获取，answer 流程的第二轮过滤层。
3. Zotero `output.md`：Haiku subagent 带着问题定向阅读，answer 流程的第三轮深入层。
4. PDF 原文：非常规检索层，仅用户明确要求，或 `output.md` 仍不足且用户同意时读取。

Zotero Note 保留为用户个人精读参考（"处理这篇""精读这篇"流程），但不作为 answer_with_kb 的检索层。

---

## 入口引导

OLH 被唤起后，根据用户意图直接路由：

- 用户明确说"查找文献证据 / 写作前检索 / 帮我找文献" → 直接进入 [内部只读服务：answer_with_kb](#内部只读服务answer_with_kb)。
- 用户明确说"记录 / 写入 / 加入索引 / 保存到 Obsidian" → 直接进入 [Obsidian 索引写入安全协议](#obsidian-索引写入安全协议最高优先级)。
- 用户明确说"处理这篇" → 执行 [处理这篇](#处理这篇)。
- 用户明确说"精读这篇 / deep read" → 执行 [精读这篇](#精读这篇)。
- 用户未明确目标（如"看这篇论文 / 用 OLH 处理这篇文献"）→ 询问："要处理这篇，还是精读这篇？"

用户明确说"只转 MD / 只转 Markdown / 转完再说"时，可以只生成、清理并导入 `output.md` 后停止；这不是默认入口，不主动展示为选项。

---

## 处理这篇

自动检查已有状态，把文献处理到 Zotero Note，并写入内容主题 tags。

### 流程

1. 定位 Zotero item
2. 检查 PDF
3. 生成或确认 `output.md`
4. References 清理与导入 Zotero
5. Zotero Note 与内容主题 tags

完成后轻提示："已处理完成。如需精读，请说"精读这篇"。"

### 步骤

**1. 定位 Zotero item**

- 用 title / citekey / itemKey 定位。
- 只读 metadata、附件列表、child note 简要状态（excerpt / 前 300–500 字符，识别 `<!-- OLH-NOTE` 和阅读状态）。
- 不读 PDF / MD 正文。
- 找不到或多候选无法判断时询问用户。

**2. 检查 PDF**

- 有 PDF attachment → 继续。
- 无 PDF → 停止，告诉用户需要先添加 PDF。

**3. 生成 output.md**

- 已有有效 `output.md`（文件存在、非空、> 500 bytes、含正文内容）→ 跳到步骤 4。
- 无 `output.md` 或明显损坏 → 调用 MinerU 转换。

**MinerU 转换**（`run_in_background: true`，超时 10 分钟）：
```bash
STORAGE_KEY="<attachmentKey>" pwsh -NoProfile -Command '
$ErrorActionPreference = "Stop"
$env:PATH = "C:\ProgramData\miniconda3\envs\mineru;C:\ProgramData\miniconda3\envs\mineru\Scripts;C:\ProgramData\miniconda3\envs\mineru\Library\bin;" + $env:PATH
$env:MINERU_MODEL_SOURCE = "modelscope"
$storageDir = Join-Path "C:\Users\zhisheng\Zotero\storage" $env:STORAGE_KEY
$pdf = Get-ChildItem $storageDir -Filter "*.pdf" | Select-Object -First 1
if (-not $pdf) { Write-Host "NO_PDF"; exit 1 }
$tmp = Join-Path $env:TEMP ("mineru_" + (Get-Random))
New-Item -ItemType Directory -Force $tmp | Out-Null
$pdfAscii = Join-Path $tmp "input.pdf"
Copy-Item $pdf.FullName $pdfAscii
mineru -p $pdfAscii -o $tmp -b pipeline
$md = Get-ChildItem $tmp -Recurse -Filter "*.md" | Select-Object -First 1
if (-not $md) { Write-Host "NO_MD_OUTPUT"; Remove-Item -Recurse -Force $tmp; exit 1 }
if ($md.Length -eq 0) { Write-Host "EMPTY_MD"; Remove-Item -Recurse -Force $tmp; exit 1 }
$destPath = Join-Path $storageDir "output.md"
Copy-Item $md.FullName $destPath
if (-not (Test-Path $destPath)) { Write-Host "COPY_FAILED"; Remove-Item -Recurse -Force $tmp; exit 1 }
if ((Get-Item $destPath).Length -eq 0) { Write-Host "COPY_EMPTY"; Remove-Item -Recurse -Force $tmp; exit 1 }
Remove-Item -Recurse -Force $tmp
Write-Host "DONE"
'
```

- 转换失败 → 停止，返回失败原因。
- 转换成功 → `output.md` 已写入 Zotero storage 目录，继续步骤 4（暂未导入 Zotero）。

用户明确说"只转 MD / 只转 Markdown / 转完再说"时，跳至步骤 4 做 References 清理，导入后停止。否则继续到步骤 5。

**4. References 清理与导入 Zotero**

- Haiku subagent（`model: haiku`）读取 `output.md` 尾部 20–30%。
- 查找以下标题：`# References` / `# REFERENCES` / `# REFERENCES AND NOTES` / `# Bibliography` / `# Literature Cited` / `# Works Cited`
- 如果 References 后有 `# Acknowledgements` / `# Data availability` / `# Supplementary`，References 结束于下一个 `#` header 之前。
- 找到明确边界 → 返回行号。不确定 → 返回 `ambiguous`，不要猜。
- Haiku 不修改文件，不生成 Note，不把 MD 正文返回主 agent。
- 返回 JSON：`{"status": "found|not_found|ambiguous", "ref_line_start": 115, "ref_line_end": 139, "confidence": 0.92}`
- 主 agent：`status = "found"` 且 `confidence >= 0.8` → 用 Edit 删除对应行。否则保留，后续 Opus subagent 在内存中忽略文末 References。
- 主 agent 不读 MD 全文。

References 清理完成后，将最终的 `output.md` 导入 Zotero：
```
mcp__zotero__write_item(action="import", filePath="<storageDir>\\output.md", parentItemKey="<itemKey>")
```
- 导入成功 → 主 agent 记录返回的 MD attachmentKey，供步骤 5 的 Opus subagent 使用。
- 导入失败 → 标记 `import_failed`，该篇停止，不进入步骤 5（Zotero Note 生成）。

**5. Zotero Note 与内容主题 tags**

检查已有 child notes：

- 已有 `deep-read` Note → 不覆盖，提示"这篇已处理完成（deep-read），如需更新请明确说明"，然后结束。
- 已有 OLH Note（`<!-- OLH-NOTE`）→ 默认不覆盖，也不重跑 Opus subagent、不单独补 tags。用户明确要求更新 Note 或更新 tags 时才执行对应更新。
- 只有旧格式 Note（无 `<!-- OLH-NOTE` 标识）→ 旧 Note 保留，新建 OLH Note。
- 无 OLH Note → 新建。

Opus subagent（`model: opus`，一次只处理一篇）：
1. Read 模板 `~/.claude/skills/ocean-literature-harbor/templates/zotero_note_template.md`
2. `get_content` 读取 `output.md` 全文（References 已在步骤 4 清理，若无则在内存中忽略文末 References）
3. 按模板生成完整 OLH Note（中文，学术严谨），阅读状态 `note-generated`
4. 同时给出 3–6 个内容主题 tags（研究区域、研究对象、过程机制、方法、数据产品——不写操作状态/流程 tags）
5. 调用 `write_note(action="create", parentKey=...)` 写入 Zotero
6. 将 tags 写入 Zotero item（调用 `write_tag`）
7. 返回短 JSON：`{"status": "written|skipped|failed", "noteKey": "xxx", "tags": ["..."]}`

主 agent 不接收完整 Note Markdown。主 agent 汇总时检查 noteKey 非空，否则标记为 failed。

不主动写 Obsidian；只有用户明确说"记录 / 写入 / 加入索引 / 保存到 Obsidian"时，才执行 Obsidian 写入安全协议。

---

## 精读这篇

基于 OLH Note 与用户交互式精读，把个人判断写回 Zotero Note。

### 流程

1. 定位 Zotero item
2. 检查 OLH Note
3. 逐 section 精读讨论
4. 写回个人总结
5. 更新阅读状态为 `deep-read`

### 步骤

**1. 定位 Zotero item**

- 用 title / citekey / itemKey 定位。
- 找不到或多候选无法判断时询问用户。

**2. 检查 OLH Note**

- 有 OLH Note → 直接精读。
- 无 OLH Note，但有 PDF 或可生成 `output.md` → 告诉用户"这篇还没有 OLH Note，我会先处理到 Note，然后继续精读"，执行"处理这篇"，完成后继续精读。
- 无 PDF 且无 OLH Note → 停止，请用户先添加 PDF。

**3. 精读讨论**

- 主 agent 读取 Zotero Note。
- 逐 section 与用户讨论。
- 记录：作者结论、我的判断、关键限制、待验证问题、与研究问题的关系。

**4. 写回**

- 更新 Zotero Note 的个人总结 / 待解决 / 思考启发 section。
- 更新阅读状态为 `deep-read`。
- `write_note(action="update", noteKey=...)` 写回 Zotero。

**5. Obsidian 写入**

- 不主动写 Obsidian。
- 可轻提示"如需加入 Obsidian 索引，请明确说明"。
- 用户明确说"记录 / 写入 / 加入索引 / 保存到 Obsidian"后，执行 [Obsidian 索引写入安全协议](#obsidian-索引写入安全协议最高优先级)。

---

## 内部只读服务：answer_with_kb

该服务主要由 ocean-paper-writer 显式调用。用户直接问文献证据时也可使用，但 OLH 被直接唤起时不主动列为启动选项。

### 设计原则

- 以最低 token 成本定位相关文献，仅在确认相关性后才深入全文。
- Note 是用户个人精读参考，**不作为 answer 流程的检索层**。
- 只有"带着问题去读"的层面才派 Haiku subagent。
- 发现某篇没有 `output.md` 时标记 `[MD NOT AVAILABLE]`，不自动触发生成。

### 模型分配

| 步骤 | 执行者 | 模型 | subagent? |
|------|------|:---:|:---:|
| Round 1: 搜索锁定候选 | 主 agent | 当前模型 | 否 |
| Round 2: Abstract 过滤 | 主 agent | 当前模型 | 否（≤5 篇时） |
| Round 3: 定向阅读 output.md | Haiku subagent | haiku | 是，多篇可并行 |
| 汇总回答 | 主 agent | 当前模型 | — |

Opus 在 answer_with_kb 中不需要出场。

### 轮间确认规则

每轮完成后主 agent 必须向用户汇报结果，**询问是否继续下一轮**。不等用户确认前不进入下一轮。

汇报格式：
- Round 1 结束后：列出候选列表 + 初步判断，问"是否进入 Round 2 读取 Abstract？"
- Round 2 结束后：列出过滤结果 + 每篇相关性简述，问"是否进入 Round 3 定向阅读 X 篇？"
- Round 3 结束后：汇总证据，问"是否满足需求，还是需要查 PDF 原文？"

### 检索步骤

**Round 1 — 搜索锁定候选**

- `search_library` 按关键词搜索，拿到候选列表（key + title + creators + date）。
- 主 agent 根据标题判断初步相关性，锁定需要进一步查看的候选（通常 3–8 篇）。
- Obsidian 两个轻量索引可选：如果索引中已有相关 citekey，可直接用于定位，但非强制步骤。
- **Round 1 结束后：向用户展示候选列表，确认是否继续。**

**Round 2 — Abstract 过滤**

- 对每篇候选调用 `get_item_details(itemKey=..., mode="preview")`。
- `preview` 模式返回 abstractNote（~200–500 字符/篇），token 成本极低。
- 主 agent 根据 Abstract 判断是否与研究问题相关，筛选出需要深入阅读的文献（通常 1–5 篇）。
- 候选 > 5 篇时可派并行 Haiku subagent 过滤，返回 `{"relevant": true/false, "reason": "..."}`。
- **Round 2 结束后：向用户展示过滤结果 + 相关性简述，确认是否继续深入。**

**Round 3 — 定向阅读 output.md（Haiku subagent）**

- Haiku subagent（`model: haiku`）一次处理一篇。
- subagent 读取 `output.md` 全文，**带着研究问题定向提取**证据。
- subagent 不生成 Note，不修改文件。只返回与问题相关的 2–5 段原文引用 + 位置标注。
- 多篇互不依赖 → 可并行派多个 Haiku subagent。
- 某篇没有 `output.md` → 标记 `[MD NOT AVAILABLE]`，降级到 Abstract 层回答。
- **Round 3 结束后：汇总证据回答，询问是否需要查 PDF 原文。**

**PDF 不是常规检索层**

- 仅用户明确要求，或 `output.md` 仍不足且用户同意时才查 PDF。

### 主 agent 汇总

- 汇总所有 Haiku subagent 返回的证据片段。
- 用 2–5 句话直接回答研究问题。
- 每条证据标注来源层级（Abstract 层 / MD 层 / PDF 层）。
- 证据不充分时明确说明不确定性和信息缺口。

### 全程约束

- 不读 Zotero Note（answer 模式下 Note 不是检索层）。
- 不写 Zotero tags、Note、metadata。
- 不写 Obsidian。
- 不自动调用"处理这篇"。
- 如用户在问答中明确说"记录 / 写入 / 加到索引"，再进入 Obsidian 写入安全协议。

---

## 与 ocean-paper-writer 的关系

- ocean-paper-writer 是写作主控，OLH 是文献证据服务和文献预处理服务。
- ocean-paper-writer 默认只调用 `answer_with_kb`。
- `answer_with_kb` 走三轮检索：`search_library` → Abstract 过滤 → Haiku subagent 读 `output.md`。
- `answer_with_kb` 不读 Zotero Note（Note 是用户个人精读参考）。
- 如果某篇文献还没有 `output.md`，标记 `[MD NOT AVAILABLE]`，不得在 answer 模式中自动调用"处理这篇"。
- 写作过程中缺 citation 时，优先返回 `[CITATION NEEDED]` 或 `[REFERENCE CANDIDATE]`，不编造 citation。

---

## 附录：批量处理

用户明确要求批量处理时，对每篇文献重复"处理这篇"的流程。主 agent 只保留 itemKey、状态、必要 Ref 行号、MD attachmentKey 和 noteKey；每个 Opus subagent 一次只处理一篇。已有 deep-read Note 的跳过。

---

## Subagent Prompt 规范

### Haiku subagent: References 边界检测

- `model: haiku`，`subagent_type: general-purpose`
- 只读 `output.md` 尾部 20–30%。
- 不生成 Note，不修改文件，不把 MD 正文返回主 agent。
- 返回 JSON：
  ```json
  {
    "status": "found | not_found | ambiguous",
    "ref_line_start": 115,
    "ref_line_end": 139,
    "confidence": 0.92
  }
  ```
- 主 agent 仅在 `status = "found"` 且 `confidence >= 0.8` 时删除 References。

### Opus subagent: Note 生成

- `model: opus`，`subagent_type: general-purpose`
- 一次只处理一篇论文。
- prompt 必须包含：
  - itemKey
  - MD attachmentKey
  - PDF attachmentKey
  - title
  - authors
  - year
  - journal
  - DOI
  - citekey
  - **模板 HTML 示例**：主 agent 先 Read 模板文件，将完整 HTML 嵌入 prompt（而非只写路径，禁止用文字描述 CSS 样式规则）
  - 阅读状态：`note-generated` 或 `imported`
- prompt 不包含：其他论文 metadata、全局候选列表、完整旧 Note 正文。
- subagent 执行：`get_content` 读 MD → 按 prompt 中嵌入的模板 HTML 示例生成 Note + 内容主题 tags（3–6 个）→ `write_note` → `write_tag`。
- 只返回短 JSON：`{"status": "written|skipped|failed", "noteKey": "xxx", "tags": ["..."]}`。
- 主 agent 不接收完整 Note Markdown。
- 主 agent 汇总时检查 noteKey 非空，否则标记 failed。

---

## Obsidian 索引写入安全协议（最高优先级）

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

## 安全规则

- **默认不修改** Zotero metadata；但"处理这篇"中明确允许写入 3–6 个内容主题 tags。
- 禁止写入操作状态 / 流程 tags，例如 `OLH:*`、`processed:*`、`status:*`。
- **默认不覆盖** Zotero Note（只 append 或更新指定 section）。
- **默认不修改** PDF 文件（原始档案）。
- `output.md` 是 MinerU 派生文本，References 边界明确时可清理；不确定时保留。
- **用户只说"分析"不代表授权写入**。
- **不存储 API key 或 secret**。
- **多附件处理**：遇到多个 PDF、多个 `output.md` 或多个 OLH Note 时，若能唯一判断主文件则使用主文件；无法唯一判断时停止并让用户选择，不自动猜。

---

## 前置条件

| 条件 | 说明 |
|------|------|
| Zotero 运行中 | Zotero 桌面版 7.x，MCP 插件已加载 |
| MinerU 已安装 | conda 环境 `mineru`，CLI 可调用 |
| zotero-mcp ≥ 1.4.7+import | 必须包含 `import` action |
| 磁盘空间 | TEMP 目录有足够空间存放临时文件 |

## 依赖

- **Zotero 桌面版 7.x**：文献管理核心。
- **zotero-mcp（含 import 支持）**：`write_item` 的 `import` action 用于附加 MD 文件。
- **MinerU**：PDF → Markdown 转换。conda 环境 `mineru`（`pip install -U "mineru[all]"`），模型源 `modelscope`。
- **Obsidian**：存放两个轻量索引文件。

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
