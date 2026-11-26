# Obsidian Agent Memory Skill

一套面向多 AI Agent（Claude Code / Codex / Kimi Code / DeepSeek Harness）协作的个人工作流模板：用本地 Obsidian Markdown 目录作为跨工具交接层，搭配分层写作规则与确定性 Python 校验脚本 `kb.py`，控制上下文体积并减少模型擅自改写口径的问题。

> 本仓库是从个人日常工作流脱敏整理出的**可运行模板**，纯属个人vibe-coding存档，含水量100%，详见下文的AI介绍。

---

## 解决上下文无法跨对话迁移的问题

在同时使用多款编码与对话 Agent 推进项目时，解决以下痛点：

1. **上下文无法跨工具迁移**：在一个 Agent 里陈述过的背景、对齐过的项目边界、否定过的方案，换到另一个 Agent 往往要从头解释。
2. **模型容易混淆事实与建议**：长对话后追记总结时，模型常把“待验证的 AI 建议”写成“用户已拍板的决定”，或者替用户补全并未承诺的期限。
3. **纯靠 Prompt 记规则会漂移**：只把目录规范和引用要求写进系统提示词，文件一多就会出现断链、重复建档或一次读入整篇长文浪费 token。

---

## 核心 Harness 取舍

- **规则分层与证据隔离（`rules/Rules.md`、`rules/Harness.md`）**：
  - 明确区分四类内容：用户明确表达、外部来源依据、已确认决定、AI 待验证建议；
  - 采用“主题笔记 + 必要原话片段”保存，开发代码与提交历史留在原项目 Git 中，知识库只保留源码路径与来源编号（`src-*`），不复制大段代码。
- **确定性检索与结构校验（`tools/kb.py`）**：
  - 提供 `notes` / `outline` / `section` / `lines` / `find` / `src` 等只读片段命令，让 Agent 先看大纲或来源片段，再按需读行，减少全量读文；
  - 通过 `check` 子命令扫描所有 Markdown 相对链接、标题锚点（`#src-...`）与 Obsidian 双向链接（`[[...]]`），在写入后用脚本兜底，不依赖模型肉眼检查。

---

## 目录结构

```text
obsidian-agent-memory-skill/
├── README.md
├── SKILL.md                # 标准 Agent Skill 入口（适用于 Claude Code / Codex / DS Bot）
├── rules/
│   ├── Harness.md          # 跨 Agent 协作背景与存储边界说明
│   └── Rules.md            # 忠实记录、自检流程与分层组织规则
├── tools/
│   └── kb.py               # 零依赖片段检索与链接/锚点校验脚本（默认检查 example-vault/）
└── example-vault/          # 内置虚构示例库（Topics/ + Sources/ + 双向链接）
    ├── README.md
    ├── Topics/
    │   ├── Project Alpha.md
    │   └── Career Notes.md
    └── Sources/
        └── alpha-sources.md
```

---

## 复用

换新设备时只需两步：

```sh
# 1. 拉取公开模板仓库（可直接软链或复制到 ~/.codex/skills/ 或 ~/.dsh/skills/）
git clone https://github.com/RainshadowQAQ/obsidian-agent-memory-skill.git

# 2. 用 --kb 指向私密同步的个人知识库目录完成校验
python3 obsidian-agent-memory-skill/tools/kb.py --kb "/path/to/your/private-vault" check
```

---

## 本地运行验证

无需安装第三方包，直接在仓库根目录运行：

```sh
# 1. 检查示例库所有双向链接、相对路径与来源锚点
python3 tools/kb.py check

# 2. 按领域列出主题笔记（不读正文）
python3 tools/kb.py notes

# 3. 精确读取某条来源记录或章节片段
python3 tools/kb.py src src-alpha-20261015-01
python3 tools/kb.py section "Project Alpha" "已确认决定"
```

如需指向你自己的 Obsidian 知识库目录，传入 `--kb` 参数即可：

```sh
python3 tools/kb.py --kb "/path/to/your/AI Knowledge Base" check
```
