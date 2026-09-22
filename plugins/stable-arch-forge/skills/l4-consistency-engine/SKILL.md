---
name: l4-consistency-engine
description: 一致性引擎技能，执行四类一致性检查（文档↔文档、文档→代码、代码→文档、代码→约束），生成一致性报告并定位漂移/冲突/异常增长。用于软件发育过程中的持续一致性监控。
level: L4
dependsOn: ["l4-arch-consistency-guard", "l3-genome-model-design"]
archRef: "../docs/04_software_development_system.md"
archVersion: v1.1.0
---
# 一致性引擎技能

## 1. 架构来源引用

> 引自 `../docs/04_software_development_system.md` §7、§8、§12

一致性引擎是本体系的核心引擎，持续判断"实际软件"是否偏离基因、蓝图和约束。提供四类检查：A. 文档↔文档（跨文档语义漂移）；B. 文档→代码（设计是否实现）；C. 代码→文档（未文档化增长 UNDOCUMENTED_GROWTH）；D. 代码→约束（架构违规/不变量破坏/生长预算超限）。

## 2. 输入条件

- 软件基因组建模完成（`l3-genome-model-design` 输出）
- 发育式开发流程已运行（`l4-dev-workflow` 输出迭代记录）
- 架构一致性守护已建立（`l4-arch-consistency-guard` 输出审计基线）

## 3. 分步执行动作

1. 阅读基线 §7/§8/§12 一致性引擎定义。
2. **A 类检查（文档↔文档）**：对 PRD/Domain/API/UI/Code/Test 中的枚举、命名、字段、状态机、职责、页面行为、API 契约做一致性矩阵比对；识别语义漂移（如同一状态在不同文档中的命名/取值集合不一致）。
3. **B 类检查（文档→代码）**：逐需求检查 realizes/implemented-by/verified-by 链；缺 Test 标记 UNVERIFIED（未验证），缺 Code 标记未实现。
4. **C 类检查（代码→文档）**：扫描代码符号，无对应 Requirement/Feature/Contract/Test 的标记 UNDOCUMENTED_GROWTH（未文档化增长）。
5. **D 类检查（代码→约束）**：检查架构规则（层级依赖方向）、不变量破坏、生长预算超限，标记 ArchitectureErrors（架构错误）。
6. 汇总生成 CONSISTENCY_REPORT（一致性报告）：Aligned（已对齐）/Stale（过期）/Conflict（冲突）/Drifted（漂移）/Undocumented（未文档化）/Orphaned（孤儿）/Unverified（未验证）/ArchitectureErrors（架构错误）计数。
7. 输出处置建议：冲突与漂移按 L4-02 分级处置；异常增长进入审查；不变量破坏阻断发育。

## 4. 输出物清单

- `consistency_report.md`：一致性报告（四类检查明细 + 统计 + 处置建议）。

## 5. 门禁校验（强制）

> 全部满足才算通过；不通过不得进入下一技能。

- [ ] 四类检查（A/B/C/D）均已执行并留痕
- [ ] 报告使用插件内 `docs/` 基线作为比对基准
- [ ] 检测出的 Conflict（冲突）/Drifted（漂移）/Undocumented（未文档化）均已给出处置去向

## 6. 完成态与下一步

- **完成态检查**：本技能正文定义的全部步骤与交付物已产出；按上节门禁项逐项校验，全部通过方可视为完成。
- **硬约束**：门禁未全部通过前，禁止进入下一技能；偏差按 L0~L4 分级处置，L3 以上必须暂停并上报。
- **下一步**：执行「l4-quality-gate」技能（dependsOn 链顺序）；不确定时调用 MCP 工具 `arch_route` 查询。
- **发现架构矛盾时**：禁止修改本技能绕过约束，必须先更新 `docs/` 基线并记录 `arch-version-log.md`，再同步本技能与 MCP 工具规则。

## 7. 更新说明

架构基线更新时（见 `docs/arch-version-log.md`），同步更新本技能内容与 `archVersion`。
