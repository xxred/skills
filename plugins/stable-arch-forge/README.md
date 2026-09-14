# stable-arch-forge Agent Plugin

Agent Plugins 1.0 | 稳态发育多Agent架构落地插件

> 插件目标：提供一套完整的**稳态发育架构**，用于 AI 辅助软件设计、AI 编程；采用 L0 入口 + L1~L4 渐进式技能披露，附带**稳态治理 MCP 工具**与**硬约束 hooks**，让 AI 装上即认知、按导航执行、被硬门禁约束。
> 核心规则：**必须按 L1→L2→L3→L4 顺序执行技能；每个技能门禁校验全部通过方可前进。完整跑完全部技能 = 完整落地整套架构。**

## 安装后：AI 如何直接上手（三步闭环）

1. **装上即认知**：插件自动注入 `l0-arch-entry` 入口技能（metadata 常驻）+ `com.github.copilot/rules/stable-arch.rules` 常驻规则——AI 立即知道"这是什么、有什么硬限制"。
2. **知道下一步**：AI 读取入口技能或调用 MCP `arch_route` 工具，按 `completed_skills` 立即定位当前阶段、下一技能、门禁要求。
3. **被硬约束**：每个技能尾部有「完成态与下一步」门禁校验；MCP `check_permission`/`deviation_classify` 提供硬校验；hooks 拦截私自修改 `skills/` 目录（必须先改 `docs/` 基线）。

## 目录说明

- `plugin.json`：插件清单（Agent Plugins 1.0 规范，skills 与 mcp 自动发现）
- `mcp.json`：MCP 服务器注册（portable MCP 格式，`${PLUGIN_ROOT}` 引用）
- `mcp/stable_homeostasis_server.py`：稳态治理 MCP 服务器（Python 零依赖，stdio）
- `docs/`：架构原始基线文档（唯一真相源，Source of Truth）
- `skills/`：13 个技能（L0 入口 + L1~L4），一技能一目录
- `com.github.copilot/`：VS Code Copilot 组件（agents 角色 / rules 常驻规则 / hooks 硬门禁）
- `templates/`：SKILL.md 模板（含完成态与下一步规范）
- `CHANGELOG.md`：插件版本变更记录

## 配套 MCP 服务器（stable-homeostasis）

插件启用后自动启动，提供 9 个工具，**对齐架构四层能力**：

| 工具 | 对应架构层 | 对应接口/技能 | 功能 |
|------|-----------|---------------|------|
| `arch_route` | 元导航（L0） | l0-arch-entry | 阶段导航：当前阶段/下一技能/门禁/可用工具 |
| `goal_field_init` | 目标场层 | 目标编码器 | 初始化全局目标场（四维快照+版本） |
| `goal_gradient` | 目标场层 | `getGoalGradient` | 计算 Agent 偏差值与优化方向 |
| `peer_validate` | 自组织协同层 | `peerValidate` | 邻域横向校验（目标锚定 + ≥2 邻域） |
| `inspect_scan` | 稳态巡检层 | L3-03 技能 | 稳态巡检五类检查 |
| `deviation_classify` | 稳态巡检层 | 详细设计 §4.1 | 偏差分级 L0~L4 + 处置建议 |
| `check_permission` | 边界约束层 | `checkActionPermission` | 角色权限门禁（白名单默认拒绝） |
| `boundary_rules` | 边界约束层 | L2-02 技能 | 查询技术栈白名单/权限矩阵/禁止项 |
| `arch_consistency_audit` | 稳态层 | L4-04 技能 | 架构一致性审计（漂移检测→重构判定） |

> 所有判定规则（偏差公式、分级阈值、白名单、权限矩阵、禁止项、阶段路由）**直接取自 `docs/` 架构基线**，修改架构须同步更新 `mcp/stable_homeostasis_server.py` 规则数据与 `arch-version-log.md`。

## 硬约束 hooks

`com.github.copilot/hooks/hooks.json` 注册 PreToolUse 钩子（`arch-gate.py`）：

- **拦截**：对插件 `skills/` 目录内文件的直接写操作（强制"先改 docs/ 基线 → 再同步改技能"的治理规则）
- **放行**：`docs/` 基线更新、用户工作区文件、非写工具；设置 `STABLE_ARCH_GATE=1` 可显式放行
- 钩子异常时自动放行（不阻塞正常流程）

## 技能总清单

### L0 入口（导航）
1. `l0-arch-entry`：总入口与导航技能（安装即认知、阶段判断、硬限制）

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
L0 → L1-01 → L1-02 → L2-01 → L2-02 → L3-01 → L3-02 → L3-03 → L3-04 → L4-01 → L4-02 → L4-03 → L4-04
```

每个 SKILL.md 的 frontmatter `dependsOn` 声明前置技能；Agent 加载时自动校验，禁止跳层执行。每个技能尾部含「完成态与下一步」，门禁未过禁止前进。

## 迭代治理规则

1. **修改架构基线**：修改 `docs/` 目录文档，更新 `arch-version-log.md`，同步更新受影响 SKILL.md 与 `mcp/stable_homeostasis_server.py` 规则数据。
2. **修改技能**：仅按正式流程修改 `skills/` 目录（hooks 会拦截直接修改）。若技能执行发现架构矛盾，**必须先更新 `docs/` 基线文档**。
3. **配套工具开发顺序**：更新架构基线 → 更新对应技能 → 更新 MCP 工具规则 → 工具行为严格对齐技能步骤。

## 版本

v1.2.0
