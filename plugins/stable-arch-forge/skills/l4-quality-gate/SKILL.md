---
name: l4-quality-gate
description: 质量门禁技能，按 G1~G7 七级门禁（需求/设计/契约/实现/验证/一致性/发布）判定每个发育阶段是否允许继续，只有通过门禁才能进入下一阶段。用于软件发育各阶段的阶段放行校验。
level: L4
dependsOn: ["l4-consistency-engine"]
archRef: "../docs/04_software_development_system.md"
archVersion: v1.1.0
---
# 质量门禁技能

## 1. 架构来源引用

> 引自 `../docs/04_software_development_system.md` §20、§21

每个发育阶段必须有门禁（Quality Gate）。只有通过 Gate 才允许进入下一阶段。门禁判定应基于 Evidence（证据：提交、构建、测试、契约检查、架构检查等），而不是人工勾选。

## 2. 输入条件

- 一致性报告（`l4-consistency-engine` 输出）
- 发育式开发迭代记录（`l4-dev-workflow` 输出）
- 代码符号与测试证据（如已接入）

## 3. 分步执行动作

1. 阅读基线 §20 质量门禁、§21 证据定义。
2. 逐级判定七个 Gate：
   - **G1 Requirement Gate（需求门禁）**：需求完整（含验收标准与状态机定义）。
   - **G2 Design Gate（设计门禁）**：Domain（领域）/Architecture（架构）/UI（视觉）足够明确。
   - **G3 Contract Gate（契约门禁）**：API/Event/State 已确定且无冲突。
   - **G4 Implementation Gate（实现门禁）**：Code 与 Development Context 匹配，无越界实现。
   - **G5 Verification Gate（验证门禁）**：Tests 通过（证据链完整：REQ→CODE→COMMIT→TEST→PASS）。
   - **G6 Consistency Gate（一致性门禁）**：一致性报告无关键漂移/冲突/未文档化增长。
   - **G7 Release Gate（发布门禁）**：当前版本形成可追踪 Baseline（基线）。
3. 任一门禁未通过：输出阻断原因与整改建议，禁止进入下一阶段；整改后重新执行对应门禁。
4. 门禁全过：标记版本为 Baseline，进入下一发育阶段。

## 4. 输出物清单

- `quality_gate_report.md`：质量门禁报告（G1~G7 逐级判定 / 证据引用 / 阻断与放行结论 / Baseline 版本标记）。

## 5. 门禁校验（强制）

> 全部满足才算通过；本技能自身即门禁系统，判定须以证据为准。

- [ ] G1~G7 逐级判定，未跳过任何一级
- [ ] 每个判定均有 Evidence（证据）支撑，非人工勾选
- [ ] 未通过门禁时明确阻断并给出整改建议

## 6. 完成态与下一步

- **完成态检查**：本技能正文定义的全部步骤与交付物已产出；按上节门禁项逐项校验，全部通过方可视为完成。
- **硬约束**：门禁未全部通过前，禁止进入下一技能；偏差按 L0~L4 分级处置，L3 以上必须暂停并上报。
- **下一步**：执行「l4-dev-context」技能（dependsOn 链顺序）；不确定时调用 MCP 工具 `arch_route` 查询。
- **发现架构矛盾时**：禁止修改本技能绕过约束，必须先更新 `docs/` 基线并记录 `arch-version-log.md`，再同步本技能与 MCP 工具规则。

## 7. 更新说明

架构基线更新时（见 `docs/arch-version-log.md`），同步更新本技能内容与 `archVersion`。
