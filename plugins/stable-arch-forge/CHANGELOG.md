# CHANGELOG - stable-arch-forge

## v1.0.0 (2026-09-13)

- 初始化完整插件包，遵循 VS Code Agent Plugin 1.0 规范
- 新增 `docs/` 全套架构基线文档：01_meta_architecture.md、02_agent_dev_architecture.md、03_full_detail_design.md、arch-version-log.md
- 新增 12 个 L1~L4 渐进式技能，全部技能附带 YAML frontmatter 依赖声明与门禁校验
- 新增 `agents/stable-architect.agent.md` 稳态架构师 Agent 角色提示
- 新增技能模板 `templates/template_skill.md`
- `plugin.json` 注册全部技能与 Agent 角色
- 预留 `mcp.json` 用于后续配套工具接入
