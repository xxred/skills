# 软件发育系统（Software Development System）— 架构基线 04

> **文档定位**：本文件是 `stable-arch-forge` 架构基线的第四份文档，收录并规范化「软件发育系统 V1.0」方案（Software Growth Studio：软件发育工作台）。它与前三份基线（顶层元架构 / AI 编程落地架构 / 全阶段详细设计）的关系是**互补细化**：前三份定义了"治理四层"与"多Agent稳态机制"，本文件把软件开发全过程抽象为**受发育约束的生命体成长**，给出领域对象模型（软件基因组）、一致性引擎、质量门禁、生长预算、受控变异与 AI 受约束编码的完整方案。
>
> **基线版本**：archVersion v1.1.0（本插件文档集版本）
> **来源**：用户提供的《软件发育系统：最终方案 V1.0》
> **应用原则**：本文件为唯一真相源的组成部分；任何技能、MCP 工具、文档投影均不得与本文冲突；本文更新必须同步 `arch-version-log.md` 与受影响技能。

---

## 1. 核心结论：软件开发是"发育过程"

软件开发可以抽象为一种**发育过程**：

- PRD（产品需求文档）定义"要发育成什么"；
- 领域模型定义"有哪些核心器官和业务实体"；
- 架构定义"内部身体结构如何组织"；
- 原型定义"页面和信息如何布局"；
- UX/交互设计定义"用户如何感知、操作和获得反馈"；
- UI 设计定义"最终视觉形态"；
- API/Event/State Contract（契约）定义"器官之间如何连接和传递信息"；
- 代码是实际发育出来的个体；
- 测试是发育检查点；
- 架构规则、不变量、生长预算是发育约束机制；
- CI/Quality Gate（质量门禁）决定一个发育阶段是否允许继续；
- Consistency Engine（一致性引擎）持续判断"实际软件"是否偏离基因、蓝图和约束。

**最重要的设计决策**：不能让 PRD、架构、原型、UI、API、代码分别成为彼此独立的"真相源"。系统必须建立**统一的 Software Genome（软件基因组 / Canonical Model）**，所有文档、代码、测试都是它的不同投影。

因此本插件的最终产品定位不是"文档管理工具"，而是：**软件发育模型 + 发育约束 + 一致性控制 + AI 开发执行平台**。

## 2. 软件发育总体模型

```
                         Software Genome
                           软件基因组（唯一真相源）
                                │
                    ┌───────────┴───────────┐
                    │                       │
                 产品意图                系统知识
                    │                       │
                   PRD              Domain / Architecture
                   （需求）           （领域 / 架构）
                    │                       │
                    └───────────┬───────────┘
                                │
                         形态与行为设计
                      ┌─────────┼─────────┐
                      │         │         │
                     UX       UI       Contract
                   （交互）   （视觉）    （契约）
                      │         │         │
                      └─────────┼─────────┘
                                │
                              Code（代码）
                                │
                          Runtime System（运行系统）
                                │
                       Evidence / Tests（证据 / 测试）
                                │
                    ┌───────────┴───────────┐
                    │                       │
             Consistency Engine       Quality Gate
              （一致性引擎）           （质量门禁）
                    │                       │
                    └───────────┬───────────┘
                                │
                         下一轮发育 / 修复
```

整个系统形成闭环：**定义 → 设计 → 约束 → 实现 → 验证 → 一致性检查 → 修复/变更 → 再发育**。

## 3. 软件发育与生物发育映射

| 软件概念 | 生物发育对应 | 主要职责 |
|----------|--------------|----------|
| PRD / Requirement（需求） | 遗传信息 / 发育目标 | 我要成为谁 |
| Feature（功能） | 发育单元 | 要形成什么能力 |
| Domain（领域） | 器官/组织分化 | 核心业务结构 |
| Architecture（架构） | 身体整体结构 | 器官如何组织 |
| Prototype（原型） | 胚胎形态蓝图 | 区域、布局、页面结构 |
| UX / Interaction（交互） | 神经系统、行为机制 | 怎么感知、操作、响应 |
| UI Design（视觉设计） | 器官形态发生 | 最终视觉形态 |
| API / Event（接口 / 事件） | 神经、血管、连接通道 | 信息如何交换 |
| Code（代码） | 细胞、组织、器官的实际形成 | 实际软件 |
| Test（测试） | 发育检查点 | 是否正确发育 |
| Invariant（不变量） | 发育不变量 | 哪些事情绝对不能被破坏 |
| Architecture Rule（架构规则） | 发育调控规则 | 哪些组织不能错误连接 |
| Growth Budget（生长预算） | 生长边界 | 防止异常增生 |
| CI / Quality Gate（质量门禁） | 自然筛选 | 不合格不能继续成长 |
| Consistency Engine（一致性引擎） | 发育监控系统 | 检查实际个体与蓝图是否一致 |
| Change / ADR（变更 / 架构决策记录） | 定向变异与适应 | 受控地改变设计 |

## 4. UI、原型和设计在体系中的位置

UI 不属于孤立的"美化阶段"，而是软件形态发育的一部分：

```
PRD（需求）
 │
 ├── 功能结构
 │      ↓
 │    页面模型
 │      ↓
 │    Prototype（原型）
 │      ↓
 │    UX / Interaction（交互）
 │      ↓
 │    UI Design（视觉设计）
 │      ↓
 │    Frontend Code（前端代码）
 │
 └── 领域/架构结构
        ↓
      API / Contract（契约）
        ↓
      Backend Code（后端代码）
```

UI/UX 与后端领域、架构处于不同维度，但最终都必须指向同一个 Software Genome。

### 4.1 原型（Prototype）
类似"胚胎形态图"，定义：页面有哪些区域、信息如何布局、页面之间如何流动、用户从哪里进入某个功能、哪些内容属于同一个功能区域。

### 4.2 UX / Interaction（交互设计）
类似神经系统和行为机制，定义：用户操作、状态变化、反馈、错误处理、页面间行为、空/加载/异常/成功等状态。

### 4.3 UI Design（视觉设计）
类似器官最终形态，定义：色彩、字体、间距、圆角、控件尺寸、视觉层级、设计组件、页面视觉规范。

### 4.4 Design System（设计系统）
Design System 是 UI 侧最接近"基因表达调控"的机制：

```
Design Token（设计令牌）→ 基础组件 → 业务组件 → 页面模板 → 页面 → 完整产品
```

设计系统也是软件发育约束的一部分。

## 5. 软件基因组（Software Genome）：整个体系的核心

### 5.1 Canonical Model（规范模型）核心对象
至少包括：Requirement（需求）、Feature（功能）、Domain（领域）、Entity（实体）、ValueObject（值对象）、State（状态）、Page（页面）、Component（组件）、Interaction（交互）、Api（接口）、Event（事件）、Invariant（不变量）、ArchitectureRule（架构规则）、DesignToken（设计令牌）、CodeSymbol（代码符号）、Test（测试）、Decision（决策）、Change（变更）、Release（发布）。

### 5.2 Relation（统一关系）
所有对象之间通过统一关系连接：`sourceId`（来源标识）+ `relationType`（关系类型）+ `targetId`（目标标识）。

例如：

```
REQ-001（需求）
 ├── realizes → FEATURE-001（实现为功能）
 ├── shaped-by → DOMAIN-001（由领域塑造）
 ├── represented-by → PAGE-001（由页面呈现）
 ├── exposed-by → API-001（由接口暴露）
 ├── constrained-by → INV-001（受不变量约束）
 ├── implemented-by → CODE-001（由代码实现）
 └── verified-by → TEST-001（由测试验证）
```

这张关系图是软件真正的**"发育谱系"**。

## 6. 文档体系的正确定位

Markdown、设计稿、接口文档等仍然保留，但它们不再互相竞争"谁是真相"。

**统一原则**：Canonical Model（规范模型）是机器可验证的事实；文档是面向人的投影。

```
                Canonical Model（规范模型）
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
         PRD        Architecture  UX/UI
         （需求）     （架构）      （交互/视觉）
          ↓           ↓           ↓
      Markdown     Diagram      Design
      （文档）     （图示）      （设计稿）
          └───────────┬───────────┘
                      ↓
                    Human（人）
```

文档允许人工编辑，但重要语义必须最终回写到 Canonical Model（规范模型）。

## 7. 解决"多个文档各写各的"问题

不能依赖人工维护一致性。系统必须建立 **Cross-Document Consistency（跨文档一致性）**。

例如：PRD 写 ONLINE/OFFLINE，Domain 写 ONLINE/OFFLINE/ERROR，API 写 ONLINE/OFFLINE/FAULT，UI 写 在线/离线/故障，Code 写 Online/Offline/Fault——单独看都可能合理，但组合起来已发生**语义漂移**。系统应自动形成一致性矩阵：

| 对象 | PRD（需求） | Domain（领域） | API（接口） | UI（视觉） | Code（代码） | Test（测试） |
|------|------|------|------|------|------|------|
| ONLINE（在线） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OFFLINE（离线） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FAULT（故障） | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |

检测类型包括：命名冲突、枚举冲突、字段冲突、状态机冲突、职责冲突、页面行为冲突、API 契约冲突、版本过期、文档引用失效。

## 8. 解决"代码和文档不匹配"问题

必须同时进行正向和反向检查。

### 8.1 文档 → 代码（正向）
回答"需求要求的东西是否真的实现"。例如 REQ-001 下 API ✅、Service ✅、UI ✅、Test ❌ → 状态：UNVERIFIED（未验证）。

### 8.2 代码 → 文档（反向）
回答"代码是否自行长出了设计之外的东西"。例如扫描代码发现 `ImageProcessingService`，但找不到 Requirement（需求）、Feature（功能）、Architecture Decision（架构决策）、Contract（契约）、Test（测试）→ 标记：**UNDOCUMENTED_GROWTH（未文档化的异常增长）**。这专门解决"顺手加一个功能/工具类/外部服务"导致的异常增生。

## 9. 发育状态模型

每个重要对象都应该有状态，建议至少：

- DRAFT（草稿）
- DESIGNED（已设计）
- IMPLEMENTING（实现中）
- IMPLEMENTED（已实现）
- VERIFIED（已验证）
- ALIGNED（已对齐）
- STALE（过期）
- CONFLICT（冲突）
- DRIFTED（漂移）
- UNDOCUMENTED（未文档化）
- ORPHANED（孤儿）
- UNVERIFIED（未验证）

例如一个 Feature（功能）TASK-001：Requirement ✅、Domain ✅、Architecture ✅、Prototype ✅、UI ⚠️ STALE（过期）、API ✅、Code ⚠️ DRIFTED（漂移）、Test ❌ UNVERIFIED（未验证）。系统**自动计算**整体发育状态，而不是让用户手动填写。

## 10. 发育约束体系（防止"畸形"的核心）

### 10.1 Invariant（不变量）
必须始终成立的事实。例如：
- INV-TASK-001：COMPLETED（已完成）不能再次进入 EXECUTING（执行中）
- INV-API-001：所有公开 API 必须满足统一响应契约
- INV-DOMAIN-001：Domain（领域层）不得直接依赖基础设施实现

不变量被破坏时，应**阻断发育**。

### 10.2 Architecture Rule（架构规则）
例如：Presentation（表现层）→ Application（应用层）✅、Application → Domain（领域层）✅、Domain → Infrastructure（基础设施层）❌、Infrastructure → Presentation ❌。用于防止结构畸形。

### 10.3 Growth Budget（生长预算）
用于控制异常增生。示例：模块公开类型数 ≤ 20、Service（服务）公开方法数 ≤ 10、模块直接依赖数 ≤ N、循环依赖 = 0、架构违规 = 0、重复代码 ≤ X%、单方法复杂度 ≤ X。这些是**项目可配置的边界**，不是绝对真理。

## 11. Change、ADR 与受控变异

软件不应该被禁止变化，而应该被允许**有证据地变化**。任何影响既有模型的变更，都应形成：

```
Change（变更）
  ↓
Impact Analysis（影响分析）
  ↓
Affected Nodes（受影响节点）
  ↓
Affected Documents（受影响文档）
  ↓
Affected Code（受影响代码）
  ↓
Affected Tests（受影响测试）
  ↓
Decision / ADR（决策 / 架构决策记录）
  ↓
Controlled Evolution（受控演化）
```

例如修改任务状态 WAITING/EXECUTING/COMPLETED/ABNORMAL，增加 CANCELLED——系统必须自动找到 Domain State Machine（领域状态机）、API、UI、Component、Code、Tests、Reports、Documentation，**不能允许只修改 PRD 而其他部分长期保持旧模型**。

## 12. Consistency Engine（一致性引擎）

本体系的核心引擎之一，至少提供四类检查：

- **A. Document ↔ Document**：检查 PRD、Domain、Architecture、UX、UI、API 之间的一致性；
- **B. Document → Code**：检查设计是否已经实现；
- **C. Code → Document**：发现未被模型描述的代码增长；
- **D. Code → Constraint**：检查架构违规、不变量破坏、生长预算超限。

最终产生 CONSISTENCY_REPORT（一致性报告）：

```
Aligned（已对齐）:           124
Stale（过期）:                 3
Conflict（冲突）:              1
Drifted（漂移）:               2
Undocumented（未文档化）:      4
Orphaned（孤儿）:              1
Unverified（未验证）:          6
ArchitectureErrors（架构错误）: 2
```

## 13. AI Agent 的正确位置

AI Agent 不应该拿着一句自然语言需求直接自由编码。它应该成为**"受发育机制约束的编码细胞"**。

### 13.1 Development Context（开发上下文）
每个编码任务先生成上下文包：

```
taskId: TASK-001
requirements: [REQ-001]          # 需求
features: [FEATURE-001]          # 功能
architectureRules: [ARCH-001, ARCH-003]  # 架构规则
invariants: [INV-001, INV-004]   # 不变量
contracts: [API-001]             # 契约
pages: [PAGE-001]                # 页面
expectedCode: [TaskService, TaskController]  # 预期代码符号
tests: [TEST-001, TEST-002]      # 测试
```

AI 的工作流程固定为：读取 Development Context → 读取相关代码 → 分析影响范围 → 形成实现计划 → 修改代码 → 运行测试 → 运行架构检查 → 运行契约检查 → 运行一致性检查 → 生成工作汇报。

### 13.2 AI 不能自行改变事实
AI 可以：实现已有需求、创建实现细节、提出技术方案、提出新的设计建议。
AI 不应未经授权自行：改变核心需求、改变领域规则、改变公共 API 语义、增加未经记录的外部依赖、引入架构层级、增加无对应需求的业务能力。如有必要，必须进入 Change / ADR（受控变更流程）。

## 14. 软件发育健康度

首页不应只是传统项目统计，而应展示软件当前发育状态：

```
Software Organism（软件个体）
────────────────────────────────
Genome（基因组）          98%
Architecture（架构）      96%
UX/UI（交互/视觉）        94%
Contracts（契约）        100%
Implementation（实现）    91%
Verification（验证）      87%

Detected（检测到）
  3 stale documents（3 个过期文档）
  2 undocumented growth（2 处未文档化增长）
  1 contract conflict（1 个契约冲突）
  4 unverified changes（4 个未验证变更）
```

注意：这些百分比是项目内部的**度量值**，不是评价"软件好坏"的绝对分数，而是帮助开发者定位未完成、未验证和漂移区域。

## 15. 导航与产品定位

已有导航：首页、治理、规划、需求、设计、调研、汇报。建议保持信息架构，但重新定义语义：

| 导航 | 核心职责 |
|------|----------|
| 首页 | 软件个体当前发育状态、偏差、风险、近期变化 |
| 治理 | Invariant（不变量）、Architecture Rule（架构规则）、Growth Budget（生长预算）、Quality Gate（质量门禁） |
| 规划 | Roadmap（路线图）、Milestone（里程碑）、Development Phase（发育阶段）、Change（变更） |
| 需求 | Requirement（需求）、Feature（功能）、Product Intent（产品意图） |
| 设计 | Domain（领域）、Architecture（架构）、Prototype（原型）、UX（交互）、UI（视觉）、Contract（契约） |
| 调研 | Research（调研）、Evidence（证据）、Assumption（假设）、Decision（决策） |
| 汇报 | Development Report（发育报告）、Change Report（变更报告）、Verification Evidence（验证证据） |

导航不负责重复管理信息，而是**不同角度查看同一个 Software Genome（软件基因组）**。

## 16. MVP：先跑通一条垂直切片

第一阶段不要把所有功能都开发完，只需完整跑通一条 Vertical Slice（垂直切片）：

```
创建一个需求 → 生成 Feature（功能）→ 建立 Domain/Design 关联 → 建立 Invariant（不变量）
→ 生成 Development Task（开发任务）→ 生成 Development Context（开发上下文）
→ AI/开发者实现 → 关联 Code（代码）→ 运行 Test（测试）
→ Consistency Check（一致性检查）→ 生成 Verification Evidence（验证证据）→ 生成 Development Report（发育报告）
```

只要这条链成立，产品核心就成立。

## 17. 推荐开发顺序（十个阶段）

```
Phase 1  Software Genome（软件基因组）
Phase 2  Relation Graph（关系图谱）
Phase 3  Development State / Version（发育状态 / 版本）
Phase 4  Consistency Engine（一致性引擎）
Phase 5  第一条 Vertical Slice（垂直切片）
Phase 6  Code Scanner / Code Mapping（代码扫描 / 代码映射）
Phase 7  Test / Quality Gate（测试 / 质量门禁）
Phase 8  Development Context（开发上下文）
Phase 9  AI Agent Execution（AI 执行）
Phase 10 完整业务功能扩展
```

各阶段要点：
- **Phase 1**：建立核心领域模型与持久化模型（后端数据库访问层按项目既定方案使用 NewLife.XCode，而非 EF Core）。核心对象：Requirement、Feature、Domain、Entity、State、Page、Component、Api、Event、Invariant、ArchitectureRule、CodeSymbol、Test、Decision、Relation。
- **Phase 2**：对象间关系与关系查询。重点：谁依赖谁、谁实现谁、谁验证谁、谁影响谁、谁过期了、谁没有关联。
- **Phase 3**：状态、版本、变更记录与状态推导。
- **Phase 4**：最小检查集合：命名冲突、字段冲突、状态冲突、关系断裂、代码未关联、文档未实现、架构违规。
- **Phase 5**：拿一个真实小需求完整走通。
- **Phase 6**：Repository（仓库）→ File（文件）→ Type（类型）→ Method（方法）→ Line/Symbol（符号），使模型可追踪到真实代码。
- **Phase 7**：接入 Unit Test、Integration Test、E2E、Architecture Test、Contract Test、Visual Regression。
- **Phase 8**：把模型自动转换成 AI 可执行的任务上下文。
- **Phase 9**：让 AI 按上下文执行，而不是自由修改项目。
- **Phase 10**：逐渐扩展需求管理、架构建模、原型、UI、调研、报告、规划、更多 AI Agent。

## 18. 第一版数据库核心模型

```
Project（项目）
  ├── Requirement（需求）
  ├── Feature（功能）
  ├── Domain（领域）
  ├── Entity（实体）
  ├── State（状态）
  ├── Page（页面）
  ├── Component（组件）
  ├── Api（接口）
  ├── Event（事件）
  ├── Invariant（不变量）
  ├── ArchitectureRule（架构规则）
  ├── CodeSymbol（代码符号）
  ├── Test（测试）
  ├── Decision（决策）
  ├── Change（变更）
  └── Release（发布）
```

统一关系表 Relation：

```
Relation（关系）
----------------
Id（标识）
SourceId（来源标识）
SourceType（来源类型）
RelationType（关系类型）
TargetId（目标标识）
TargetType（目标类型）
Version（版本）
CreatedAt（创建时间）
```

优先支持的 RelationType（关系类型）：contains（包含）、refines（细化）、depends-on（依赖）、realizes（实现）、represented-by（呈现）、implemented-by（实现于）、verified-by（验证于）、constrained-by（受约束于）、exposed-by（暴露于）、emits（发出）、consumes（消费）、supersedes（取代）、impacts（影响）、derived-from（派生自）。

## 19. 版本与基线

软件不能只保存"当前值"，需要保存**发育过程**。每次重要变更形成一个版本：

```
Genome v1（基因组版本1）→ Design v1（设计版本1）→ Code v1（代码版本1）→ Verified v1（验证版本1）
Change（变更）→ Genome v2（基因组版本2）→ Affected Design（受影响设计）→ Affected Code（受影响代码）→ Re-Verification（重新验证）
```

版本状态建议：Draft（草稿）、Baseline（基线）、Released（已发布）、Superseded（已取代）。其中 **Baseline（基线）** 是某一个时刻被认可的一致状态。

## 20. Quality Gate（质量门禁）

每个发育阶段必须有门禁。最小 Gate：

- **G1 Requirement Gate（需求门禁）**：需求完整
- **G2 Design Gate（设计门禁）**：Domain/Architecture/UI 足够明确
- **G3 Contract Gate（契约门禁）**：API/Event/State 已确定
- **G4 Implementation Gate（实现门禁）**：Code 与上下文匹配
- **G5 Verification Gate（验证门禁）**：Tests 通过
- **G6 Consistency Gate（一致性门禁）**：无关键漂移、冲突、未文档化增长
- **G7 Release Gate（发布门禁）**：当前版本形成可追踪 Baseline

只有通过 Gate 才允许进入下一阶段。

## 21. 代码不是唯一的"证据"

最终一致性判断应尽量基于 **Evidence（证据）**，而不是人工勾选。证据来源：Git Commit（提交）、Pull Request（合并请求）、Code Symbol（代码符号）、Build Result（构建结果）、Unit Test Result（单元测试结果）、Integration Test Result（集成测试结果）、E2E Screenshot（端到端截图）、API Contract Test（契约测试）、Architecture Check（架构检查）、Runtime Observation（运行观测）、Manual Approval（人工审批）。

例如：`REQ-001 → CODE-001 → COMMIT-a123 → TEST-007 → PASS` 就是完整的**"发育证据链"**。

## 22. 汇报模型

"汇报"应围绕发育变化而不是传统工作日报。示例：

```
Development Report（发育报告）
Feature: TASK-001

本次变化
  + 创建 Task API（接口）
  + 创建 TaskService（服务）
  + 增加状态转换
  + 增加 4 个测试

发育链
  Requirement（需求）✅   Domain（领域）✅   Design（设计）✅
  Contract（契约）✅     Code（代码）✅     Test（测试）✅   Consistency（一致性）✅

约束
  Architecture Violations（架构违规）0
  Invariant Violations（不变量破坏） 0
  Undocumented Growth（未文档化增长）0

证据
  Commit（提交）: XXXXX
  Tests（测试）:  XX passed
```

AI 完成工作后自动生成，不依靠人工整理。

## 23. 最终解决的核心问题

传统软件开发：需求文档 → 设计文档 → 开发 → 测试 → "应该没问题"。
本系统变为：Software Genome（软件基因组）→ Development Plan（发育计划）→ Design（设计）→ Constraints（约束）→ Code（代码）→ Evidence（证据）→ Consistency Engine（一致性引擎）→ Quality Gate（质量门禁）→ Baseline（基线）。

核心变化五个：
1. 从**文档中心**转向**模型中心**；
2. 从**事后测试**转向**持续发育验证**；
3. 从**自由编码**转向**受约束编码**；
4. 从**人工发现偏差**转向**自动检测 Drift（漂移）**；
5. 从**AI 自由生成代码**转向**AI 按 Development Context（开发上下文）执行**。

## 24. 最终产品定位

对外定义为：**Software Growth Studio：软件发育工作台**。一个以 Software Genome（软件基因组）为核心，把需求、架构、领域、UX/UI、契约、代码、测试和 AI Agent 连接起来，并持续检测软件发育一致性与异常增长的软件工程平台。

它不是普通文档工具、普通项目管理工具、普通原型工具、普通代码生成工具、普通测试平台，而是把这些组织成**连续的发育过程**：

```
                    软件个体
                       │
              ┌────────┼────────┐
              ↓        ↓        ↓
            功能轴    结构轴    体验轴
              │        │        │
             PRD      架构      UX/UI
             （需求）  （架构）  （交互/视觉）
              │        │        │
              └────────┼────────┘
                       ↓
                    Contract（契约）
                       ↓
                     Code（代码）
                       ↓
                   Evidence（证据）
                       ↓
                 Consistency（一致性）
                       ↓
                   Governance（治理）
                       ↓
                  持续发育
```

## 25. 最终实施原则（七原则）

1. **模型优先**：先建立 Software Genome，再建立围绕它的页面和文档。
2. **关系优先**：任何重要对象都必须能回答：来自哪里？影响谁？实现在哪里？验证在哪里？违反了什么？
3. **约束必须机器可执行**：不写"请保持架构清晰"，而写成 `Rule: Domain MUST NOT depend on Infrastructure` 并自动检查。
4. **允许变化，但必须受控**：新需求、设计、架构、技术方案通过 Change / ADR 进入软件基因组，而不是偷偷修改局部。
5. **代码必须可追踪**：Requirement → Feature → Design → Contract → Code Symbol → Test → Evidence 全程可追溯。
6. **未验证不等于完成**："代码写完"只是 IMPLEMENTED；只有通过测试、约束和一致性检查后，才能进入 VERIFIED / ALIGNED。
7. **没有来源的代码增长必须被发现**：所有不能追溯到需求、设计、约束或明确技术决策的新增能力，都必须进入审查状态。

## 26. 开发第一批任务

进入开发后，第一批任务固定为：
1. Project / Workspace（项目 / 工作区）
2. Software Genome Core Model（软件基因组核心模型）
3. Relation Model（关系模型）
4. Requirement CRUD（需求增删改查）
5. Feature CRUD（功能增删改查）
6. Invariant / ArchitectureRule CRUD（不变量 / 架构规则增删改查）
7. Development State Engine（发育状态引擎）
8. Basic Impact Analysis（基础影响分析）
9. Basic Consistency Engine（基础一致性引擎）
10. 第一条 Vertical Slice（垂直切片）

第一条 Vertical Slice 成功后再扩展：Prototype、UX、UI、API Designer、Code Scanner、Test Runner、AI Agent、Reports、Dashboard。

## 27. 一句话总结

让软件像一个受基因、形态规则和发育检查点约束的生命体一样成长：**需求定义它要成为谁，设计定义它应该长成什么样，约束规定它允许怎样生长，代码实现实际发育，测试提供发育证据，一致性引擎持续发现偏差，而 AI Agent 负责在这些约束之内加速发育。**

---

## 附录 A：与稳态四层架构（01/02/03 基线）的关系映射

| 软件发育系统概念 | 对应稳态四层机制 | 说明 |
|------------------|------------------|------|
| Software Genome（软件基因组） | 目标场层 + 全局规约 | 单一真相源；目标场是发育意图，Genome 是其领域化、对象化的完整表达 |
| Relation / 发育谱系（关系 / 发育谱系） | 目标追溯原则 | 所有对象可追溯来源与去向 |
| Invariant / Architecture Rule / Growth Budget（不变量 / 架构规则 / 生长预算） | 边界约束层 | 机器可执行的硬约束；Growth Budget 即"生长边界"的量化形式 |
| Consistency Engine（一致性引擎） | 稳态巡检层 | 巡检的自动化和对象化：四类检查对应五类巡检的细化 |
| Quality Gate G1~G7（质量门禁） | 门禁校验机制 | 阶段门禁的标准化序列 |
| Change / ADR（受控变异） | 跨层协同 + 架构变更流程 | 变更必须进入模型并全量影响分析 |
| Development Context（开发上下文） | 目标场下发任务 | AI 受约束编码的输入包 |
| Evidence / Tests（证据 / 测试） | 完成态校验 | 未验证不等于完成 |
| Development Report（发育报告） | 汇报闭环 | 围绕发育变化自动生成 |