# stable-arch-forge Agent Plugin

Agent Plugin 1.0 | 稳态发育多Agent架构落地插件

> 插件目标：提供一套完整的**稳态发育架构**，用于 AI 辅助软件设计、AI 编程；采用 L1~L4 渐进式技能披露。
> 核心规则：**必须按 L1→L2→L3→L4 顺序执行；每个技能门禁校验全部通过，方可执行依赖该技能的后续技能。完整跑完全部技能等价于完整落地整套架构。**

## 目录说明

- `plugin.json`：插件清单，VS Code Agent 加载入口
- `docs/`：架构原始基线文档（唯一真相源，Source of Truth）
- `skills/`：渐进式可执行技能集合，一技能一目录
- `agents/`：自定义 Agent 角色定义
- `templates/`：SKILL.md 模板
- `CHANGELOG.md`：插件版本变更记录
- `mcp.json`：预留，后续配套工具 MCP 接入

## 技能总清单

### L1 认知层：读懂架构原理，建立统一认知基线
1. `l1-arch-cognition`：稳态架构核心认知技能
2. `l1-risk-cancer-recognize`：系统癌变失控风险识别认知技能

### L2 规约层：全局刚性约束，定义不可突破的边界门禁
1. `l2-global-spec`：全局刚性规约落地技能
2. `l2-boundary-gate`：边界门禁与白名单约束落地技能

### L3 分层设计层：按架构四层模型完成系统设计
1. `l3-target-field-design`：目标场层设计落地技能
2. `l3-self-org-network`：自组织协同层组网设计技能
3. `l3-stable-inspect-design`：稳态巡检分层设计技能
4. `l3-boundary-layer-design`：底层边界约束层落地设计技能

### L4 稳态运行治理层：开发流程、偏差检测、架构守护闭环
1. `l4-dev-workflow`：全流程发育式开发执行技能
2. `l4-deviation-cancer-dispose`：偏差识别与癌变分级处置技能
3. `l4-cross-layer-collab`：跨层协同流程落地技能
4. `l4-arch-consistency-guard`：架构一致性守护技能

## 依赖链

```
L1-01 → L1-02 → L2-01 → L2-02 → L3-01 → L3-02 → L3-03 → L3-04 → L4-01 → L4-02 → L4-03 → L4-04
```

每个 SKILL.md 的 frontmatter `dependsOn` 声明前置技能；Agent 加载时自动校验，禁止跳层执行。

## 迭代治理规则

1. **修改架构基线**：修改 `docs/` 目录文档，更新 `arch-version-log.md`，遍历本插件 `skills/` 目录所有技能，同步更新受影响 SKILL.md。
2. **修改技能**：仅修改 `skills/` 目录。若技能执行发现架构存在矛盾或缺失，**禁止直接修改技能绕过约束，必须先更新 `docs/` 基线文档**。
3. **配套工具开发顺序**：更新架构基线 → 更新对应技能 → 配置 `mcp.json` → 开发工具，工具行为严格对齐技能步骤。

## 版本

v1.0.0
