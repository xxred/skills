---
name: l3-genome-model-design
description: 软件基因组建模技能，建立统一 Software Genome（软件基因组/Canonical Model 规范模型）——核心对象、统一关系 Relation、发育谱系。用于任何以软件发育系统为目标的建模任务，是一致性引擎、质量门禁、受约束编码的前置。
level: L3
dependsOn: ["l3-boundary-layer-design"]
archRef: "../docs/04_software_development_system.md"
archVersion: v1.1.0
---
# 软件基因组建模技能

## 1. 架构来源引用

> 引自 `../docs/04_software_development_system.md` §5、§6、§18

软件开发必须有一个**唯一真相源**：Software Genome（软件基因组 / Canonical Model 规范模型）。PRD、架构、原型、UI、API、代码、测试都是它的不同投影，禁止各自成为独立真相源。

## 2. 输入条件

- L3 全部技能（含 L3-04 边界约束层设计）门禁校验通过
- 目标项目已明确：采用软件发育系统方法建模

## 3. 分步执行动作

1. 阅读基线文档 §5 软件基因组、§18 数据库核心模型。
2. 建立本项目 Genome 核心对象模型，至少覆盖：Requirement（需求）、Feature（功能）、Domain（领域）、Entity（实体）、State（状态）、Page（页面）、Component（组件）、Api（接口）、Event（事件）、Invariant（不变量）、ArchitectureRule（架构规则）、CodeSymbol（代码符号）、Test（测试）、Decision（决策）、Change（变更）、Release（发布）。
3. 定义统一关系表 Relation：SourceId（来源标识）/SourceType（来源类型）/RelationType（关系类型）/TargetId（目标标识）/TargetType（目标类型）/Version（版本）/CreatedAt（创建时间）。
4. 为关键对象建立**发育谱系**：每个需求必须能回答 realizes（实现为）/shaped-by（由谁塑造）/represented-by（由谁呈现）/exposed-by（由谁暴露）/constrained-by（受谁约束）/implemented-by（由谁实现）/verified-by（由谁验证）。
5. 明确文档定位：Canonical Model（规范模型）是机器可验证的事实，文档是面向人的投影；重要语义必须回写模型。

## 4. 输出物清单

- `software_genome_model.md`：软件基因组规范模型文档（核心对象清单 / Relation 关系表 / 关键对象发育谱系 / 投影文档映射）。

## 5. 门禁校验（强制）

> 全部满足才算通过；不通过不得进入后续技能。

- [ ] 已建立统一 Genome，不存在并行的"多真相源"
- [ ] Relation 统一关系表字段与架构基线一致
- [ ] 每个核心对象均可追溯来源（来自哪里）与去向（影响谁/实现在哪里/验证在哪里/违反了什么）

## 6. 完成态与下一步

- **完成态检查**：本技能正文定义的全部步骤与交付物已产出；按上节门禁项逐项校验，全部通过方可视为完成。
- **硬约束**：门禁未全部通过前，禁止进入下一技能；偏差按 L0~L4 分级处置，L3 以上必须暂停并上报。
- **下一步**：执行「l4-consistency-engine」技能（dependsOn 链顺序）；不确定时调用 MCP 工具 `arch_route` 查询。
- **发现架构矛盾时**：禁止修改本技能绕过约束，必须先更新 `docs/` 基线并记录 `arch-version-log.md`，再同步本技能与 MCP 工具规则。

## 7. 更新说明

架构基线更新时（见 `docs/arch-version-log.md`），同步更新本技能内容与 `archVersion`。
