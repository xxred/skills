---
name: l4-dev-context
description: 受约束编码技能，为每个编码任务生成 Development Context（开发上下文）包，约束 AI 按上下文执行而非自由编码，AI 不得未经授权改变核心需求/领域规则/公共契约。用于 AI 编程落地。
level: L4
dependsOn: ["l4-quality-gate"]
archRef: "../docs/04_software_development_system.md"
archVersion: v1.1.0
---
# 受约束编码技能

## 1. 架构来源引用

> 引自 `../docs/04_software_development_system.md` §13

AI Agent 是"受发育机制约束的编码细胞"：不应拿着自然语言需求直接自由编码，必须按 Development Context（开发上下文）包执行。AI 可以实现已有需求、创建实现细节、提出技术方案与设计建议；不得未经授权改变核心需求、领域规则、公共 API 语义、增加未记录的外部依赖、引入架构层级、增加无对应需求的业务能力。

## 2. 输入条件

- 软件基因组规范模型（`l3-genome-model-design` 输出）
- 质量门禁报告（`l4-quality-gate` 输出，确认可进入实现阶段）

## 3. 分步执行动作

1. 阅读基线 §13 Development Context 定义。
2. 为每个编码任务构建上下文包：taskId（任务标识）、requirements（需求列表）、features（功能列表）、architectureRules（架构规则列表）、invariants（不变量列表）、contracts（契约列表）、pages（页面列表）、expectedCode（预期代码符号）、tests（测试列表）。
3. 固定执行工作流（AI 必须遵循）：读取 Development Context → 读取相关代码 → 分析影响范围 → 形成实现计划 → 修改代码 → 运行测试 → 运行架构检查 → 运行契约检查 → 运行一致性检查 → 生成工作汇报。
4. 识别"不可自行改变的事实"清单：核心需求、领域规则、公共 API 语义、外部依赖、架构层级、无需求业务能力。任何此类变更必须进入 Change / ADR（受控变异流程）。
5. 完成实现后，按 §22 汇报模型生成 Development Report（发育报告）：本次变化、发育链、约束、证据。

## 4. 输出物清单

- `development_context.md`：开发上下文包（taskId + 九要素）。
- `development_report.md`：发育报告（本次变化 / 发育链 / 约束 / 证据）。

## 5. 门禁校验（强制）

> 全部满足才算通过；不通过不得宣称完成。

- [ ] 每个编码任务先有 Development Context 再动代码
- [ ] 实现未超出上下文包范围（无越界能力）
- [ ] 任何"改变事实"类变更均进入 Change / ADR，未静默修改
- [ ] 报告含证据链，未验证项标注 UNVERIFIED（未验证）

## 6. 完成态与下一步

- **完成态检查**：本技能正文定义的全部步骤与交付物已产出；按上节门禁项逐项校验，全部通过方可视为完成。
- **硬约束**：门禁未全部通过前，禁止宣称任务完成；偏差按 L0~L4 分级处置，L3 以上必须暂停并上报。
- **下一步**：本技能为软件发育闭环终端技能。此后进入**稳态循环**：持续执行一致性检查（`l4-consistency-engine`）与质量门禁（`l4-quality-gate`），触发下一轮发育；不确定时调用 MCP 工具 `arch_route` 查询。
- **发现架构矛盾时**：禁止修改本技能绕过约束，必须先更新 `docs/` 基线并记录 `arch-version-log.md`，再同步本技能与 MCP 工具规则。

## 7. 更新说明

架构基线更新时（见 `docs/arch-version-log.md`），同步更新本技能内容与 `archVersion`。
