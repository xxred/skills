# CHANGELOG - stable-arch-forge

## v1.3.0 (2026-09-22)

- **新增架构基线** `docs/04_software_development_system.md`：完整收录软件发育系统方案（Software Growth Studio 定位）——Software Genome（软件基因组/Canonical Model）唯一真相源、Relation 发育谱系、Consistency Engine（一致性引擎四类检查）、Quality Gate（质量门禁 G1~G7）、Growth Budget（生长预算）、Change/ADR（受控变异）、Development Context（受约束编码）、Evidence（证据链）；`arch-version-log.md` 升至架构基线 v1.1.0
- **新增 4 个技能**：`l3-genome-model-design`（软件基因组建模）、`l4-consistency-engine`（一致性引擎）、`l4-quality-gate`（质量门禁）、`l4-dev-context`（受约束编码）；技能总数 13 → 17
- **MCP 新增 5 个工具**（共 14 个）：`genome_relation_audit`（发育谱系审计）、`consistency_check`（四类一致性检查）、`quality_gate`（G1~G7 门禁）、`growth_budget`（生长预算校验）、`dev_context_build`（开发上下文构建）；`arch_route` 阶段路由同步扩展至 17 技能
- **L0 入口技能更新**：技能清单、阶段表、MCP 工具表同步；硬限制新增四条（单一真相源 / 变化受控 Change/ADR / 未验证不等于完成 / 无来源增长必须被发现）
- 更新 README、CHANGELOG、仓库 update-log

## v1.2.0 (2026-09-14)

- **新增 L0 总入口技能** `l0-arch-entry`：安装即认知、四阶段状态机导航、阶段判断、硬限制清单、跑偏处置指引
- **MCP 新增 `arch_route` 阶段导航工具**：按已完成技能返回当前阶段/下一技能/门禁/可用工具（共 9 个工具）
- **新增硬约束 hooks**：`com.github.copilot/hooks/hooks.json` + `arch-gate.py`（PreToolUse 拦截私自修改 `skills/`，强制先改 `docs/` 基线流程）
- **新增常驻规则** `com.github.copilot/rules/stable-arch.rules`（装即认知的持续注入指令）
- **12 个技能统一追加「完成态与下一步」**：门禁校验、下一技能、架构矛盾处理规范
- 技能模板 `templates/template_skill.md` 新增完成态/下一步规范节

## v1.1.0 (2026-09-13)

- **新增配套 MCP 服务器**：`mcp/stable_homeostasis_server.py`（Python 零依赖，stdio JSON-RPC 2.0），提供 8 个工具对齐架构四层能力：`goal_field_init`、`goal_gradient`、`peer_validate`、`inspect_scan`、`deviation_classify`、`check_permission`、`boundary_rules`、`arch_consistency_audit`
- **重写 `mcp.json`** 为 portable MCP 格式（`mcpServers` 顶层对象，`${PLUGIN_ROOT}` 引用插件路径），注册 `stable-homeostasis` 服务器
- **修正 `plugin.json`** 为 Agent Plugins 1.0 规范最小集（skills 与 mcp 自动发现，不再列出组件路径；`author` 改为对象；版本升至 1.1.0）
- **迁移 Agent 角色**：`agents/stable-architect.agent.md` → `com.github.copilot/agents/stable-architect.agent.md`（VS Code Copilot 命名空间规范）
- 更新插件 README：新增 MCP 工具清单与架构对应关系

## v1.0.0 (2026-09-13)

- 初始化完整插件包，遵循 VS Code Agent Plugin 1.0 规范
- 新增 `docs/` 全套架构基线文档：01_meta_architecture.md、02_agent_dev_architecture.md、03_full_detail_design.md、arch-version-log.md
- 新增 12 个 L1~L4 渐进式技能，全部技能附带 YAML frontmatter 依赖声明与门禁校验
- 新增稳态架构师 Agent 角色提示与技能模板 `templates/template_skill.md`