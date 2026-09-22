---
name: l0-arch-entry
description: 本插件（stable-arch-forge）总入口与导航技能。安装本插件后、用户开始任何 AI 软件开发/编程/设计任务、或询问"这个插件怎么用、下一步做什么、现在处于哪个阶段"时，必须先读取本技能：它说明插件是什么、四阶段执行路径、当前所处阶段的判断方法、每阶段门禁要求、可用的 MCP 工具，以及不可逾越的硬限制。按本技能导航执行，是完整落地稳态发育架构的唯一正确路径。
level: L0
dependsOn: []
archRef: docs/01_meta_architecture.md, docs/02_agent_dev_architecture.md, docs/03_full_detail_design.md, docs/04_software_development_system.md
archVersion: v1.1.0
---

# L0 总入口：稳态发育架构导航

你是已安装 `stable-arch-forge` 插件的 Agent。本技能是你所有软件开发/设计任务的**起点**。先回答三个问题：这是什么 → 我在哪 → 下一步做什么。

## 1. 这是什么（30 秒认知）

本插件封装一套**稳态发育多Agent架构**：借鉴生物发育的稳态机制（目标场引导、邻域协同、分层巡检、边界约束），防止 AI 编程/多Agent 系统"癌变"（跑偏失控、偏离目标、架构腐化）。插件同时落地**软件发育系统**（Software Growth Studio 定位）：以 Software Genome（软件基因组）为唯一真相源，所有文档/代码/测试都是它的投影，由一致性引擎、质量门禁、生长预算与受约束编码持续约束。

- 架构基线（唯一真相源）：插件 `docs/` 目录 5 份文档（顶层元架构 / AI编程落地架构 / 全阶段详细设计 / 软件发育系统 / 版本日志）
- 执行载体：`skills/` 下 17 个技能（本入口 + L1~L4），**必须按序执行**
- 硬能力：`stable-homeostasis` MCP 服务器（14 个治理与发育工具，可查询/校验）
- 角色：`stable-architect` 架构师 Agent（可选，用于复杂架构决策）

## 2. 执行路径（四阶段状态机）

```
[L0 入口] → L1 认知层 → L2 规约层 → L3 分层设计层 → L4 稳态运行治理层 → 闭环
```

| 阶段 | 技能链 | 完成态（门禁） | 主要 MCP 工具 |
|------|--------|----------------|---------------|
| L1 认知 | `l1-arch-cognition` → `l1-risk-cancer-recognize` | 理解架构原理与癌变风险；能回答"为什么这样设计" | `arch_route` |
| L2 规约 | `l2-global-spec` → `l2-boundary-gate` | 全局刚性规约成文；边界门禁与白名单落地 | `boundary_rules`, `check_permission` |
| L3 设计 | `l3-target-field-design` → `l3-self-org-network` → `l3-stable-inspect-design` → `l3-boundary-layer-design` → `l3-genome-model-design` | 四层分层设计完成且互不矛盾；软件基因组（唯一真相源）建模完成 | `goal_field_init`, `arch_consistency_audit`, `genome_relation_audit` |
| L4 运行 | `l4-dev-workflow` → `l4-deviation-cancer-dispose` → `l4-cross-layer-collab` → `l4-arch-consistency-guard` → `l4-consistency-engine` → `l4-quality-gate` → `l4-dev-context` | 开发全流程走通；偏差按 L0~L4 分级处置；架构漂移受控；一致性引擎、质量门禁 G1~G7、受约束编码全部生效 | `goal_gradient`, `peer_validate`, `inspect_scan`, `deviation_classify`, `consistency_check`, `quality_gate`, `growth_budget`, `dev_context_build` |

## 3. 我在哪（阶段判断）

按任务特征定位当前阶段，不确定时调用 MCP 工具 `arch_route` 查询：

- 用户要求"了解这套架构/为什么这么设计" → **L1**
- 用户给出项目，需"定规约、定边界、定技术栈" → **L2**
- 已有规约，需"做系统/模块分层设计" 或 "建立软件基因组（统一模型/关系/发育谱系）" → **L3**
- 已进入"开发、编码、测试、巡检、纠偏、一致性检查、质量门禁" → **L4**
- 已完成一轮完整执行 → 回到入口，进入**稳态循环**（按需重复 L4 一致性巡检与质量门禁）

## 4. 下一步做什么（执行规则）

1. 先读取当前阶段第一个技能（按 `dependsOn` 链，**禁止跳级**）。
2. 执行技能正文定义的全部步骤，产出该技能的**全部交付物**。
3. 执行完读技能尾部「完成态与下一步」，逐项校验门禁；**门禁未全部通过，禁止进入下一技能**。
4. 需要硬校验时，调用 `stable-homeostasis` MCP 工具（见上表），以工具结果为准，不自行推断。
5. 完成后执行下一技能，直至 L4 软件发育闭环（一致性引擎 → 质量门禁 → 受约束编码）。

## 5. 硬限制（不可逾越，违反即"癌变"）

1. **禁止跳阶段/逆流程**：依赖链 L1→…→L4 必须顺序执行；任何技能未通过门禁不得前进。
2. **禁止私自修改架构**：`docs/` 是唯一真相源。发现架构矛盾时，**先改 docs/ 基线 + 更新 arch-version-log.md，再同步改技能**；禁止只改技能绕过约束。
3. **单一真相源原则**：Software Genome（软件基因组）是唯一事实源；PRD/架构/原型/UI/API/代码/测试都是投影。禁止在文档或代码中并行建立"第二真相源"；发现文档与模型冲突，先回写模型再改投影。
4. **禁止越权动作**：任何写操作前先调用 `check_permission` 校验；白名单默认拒绝；不在白名单的动作必须拒绝并向用户说明。
5. **禁止绕过门禁**：MCP 校验是硬门禁，不接受"软约束替代硬门禁"；校验失败必须整改，不得放行。质量门禁 G1~G7 逐级判定，未通过不得进入下一发育阶段。
6. **禁止破坏边界**：模块/Agent 不得跨层调用、不得修改他模块内部数据、不得引入白名单外依赖。
7. **变化必须受控**：任何影响核心需求/领域规则/公共 API 语义/架构层级/外部依赖的变更，必须进入 Change / ADR（受控变异）流程，禁止静默修改局部。
8. **未验证不等于完成**："代码写完"只是 IMPLEMENTED（已实现），必须通过测试、约束与一致性检查后才能宣称 VERIFIED（已验证）/ALIGNED（已对齐）。
9. **无来源的增长必须被发现**：不能追溯到需求/设计/约束/技术决策的新增能力，必须标记 UNDOCUMENTED_GROWTH（未文档化增长）并进入审查，禁止视为正常功能。
10. **偏差必须分级处置**：调用 `deviation_classify`，按 L1~L4 处置；L3 以上必须暂停并上报，不得继续。
11. 插件 hooks 已对 `docs/`、`skills/` 目录实施写保护：直接改写会被拦截（需经正式架构变更流程）。

## 6. 跑偏了怎么办

发现执行偏离目标场（需求/架构/质量/进度任一维度偏差超阈值）：
1. 调用 `goal_gradient` 计算偏差与优化优先级；
2. 调用 `deviation_classify` 定级；
3. 按级别处置（L1 就地修复 / L2 回滚整改 / L3 暂停排查 / L4 终止回滚），处置后重新校验门禁再继续。
