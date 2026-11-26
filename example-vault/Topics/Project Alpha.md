---
area: work
kind: project-home
status: active
updated: 2026-10-15
tags:
  - project/alpha
---
# Project Alpha

虚构示例项目：展示如何在跨 Agent 协作中分离“用户明确要求”、“外部来源证据”与“AI 建议”。

## 目的与约束

- 用户明确要求：第一阶段只做静态原型与本地校验脚本，不接云端数据库（依据：[src-alpha-20261015-01](../Sources/alpha-sources.md#src-alpha-20261015-01)）。
- 外部接口限制：公开查询接口仅返回摘要字段，完整附件需单独下载（依据：[src-alpha-20261015-02](../Sources/alpha-sources.md#src-alpha-20261015-02)）。

## 已确认决定与待验证建议

- **已确认决定**：输出目录按 `Topics/` 与 `Sources/` 分层保存，每次更新后运行 `kb.py check`。
- **AI 建议（未采纳，待定）**：曾建议引入向量数据库做语义检索；用户认为当前规模无需增加复杂度，暂不采用。

## 相关笔记

- [[Topics/Career Notes|Career Notes]]：记录了该项目的复盘输出标准。

## 更新记录

- 2026-10-15：初始化示例项目笔记，绑定两条来源记录。
