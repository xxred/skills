# CHANGELOG - stable-arch-forge

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
