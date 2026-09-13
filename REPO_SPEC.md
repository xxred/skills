# 仓库全局规范 REPO_SPEC.md

本仓库遵循 **VS Code Agent Plugins 1.0** 标准，用于存放多个 Agent 插件包。

## 1. 目录约束（不可修改）

- 所有插件必须放在 `plugins/` 下，一个插件 = 一个独立文件夹。
- 每个插件根目录必须存在 `plugin.json`（插件清单，声明 skills / agents 路径）。
- 插件内架构/设计文档：统一放在**插件内 `docs/`**，**禁止放置仓库根目录**。
- 插件技能：插件内 `skills/`，一个技能一个子目录，每个子目录包含 `SKILL.md`，技能名称 kebab-case。
- 仓库根目录仅维护：`README.md`、`REPO_SPEC.md`、`update-log.md`，不存放业务架构文档。

## 2. 新增插件流程

1. 在 `plugins/` 新建插件文件夹。
2. 创建 `plugin.json`，声明技能路径与 Agent 路径。
3. 编写插件 `README.md`、`CHANGELOG.md`。
4. 放入 `docs/` 架构基线 + `skills/` 技能集 + `agents/` 角色（如需）。
5. 更新仓库根 `README.md` 插件索引。
6. 写入 `update-log.md`。

## 3. 在已有插件内新增技能

1. 在插件 `skills/` 下新建 kebab-case 命名技能目录，新建 `SKILL.md`，使用插件内 `templates/template_skill.md` 模板。
2. 在 `plugin.json` 的 `skills` 数组追加技能 path。
3. 更新插件 `README.md` 技能清单。
4. 写入插件 `CHANGELOG.md`。
5. 写入仓库 `update-log.md`。

## 4. 架构与技能双向同步规则

1. **架构变更**：修改插件内部 `docs/`，更新 `docs/arch-version-log.md`，扫描并更新本插件所有关联 `SKILL.md`（含 `archVersion`）。
2. **技能执行发现架构缺陷**：禁止直接修改技能绕过约束；先修改插件内 `docs/` 基线，再更新技能。
3. 每个 `SKILL.md` 必须在头部 frontmatter 标记：`archRef`、`archVersion`、`dependsOn`，绑定插件内架构文档与前置依赖。

## 5. 渐进式技能约束

技能依赖写在 `SKILL.md` frontmatter 的 `dependsOn` 字段；Agent 加载时自动校验前置技能是否已完成门禁校验，**禁止跳过层级执行**（L1→L2→L3→L4）。

## 6. 后续配套工具开发流程

1. 更新插件 `docs/` 架构基线。
2. 更新插件内对应 `SKILL.md` 技能。
3. 在插件中新增/修改 `mcp.json`，接入 MCP 服务。
4. 开发配套工具，保证工具行为严格对齐技能执行步骤。
