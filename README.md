# OpenForgeSelf Skills Repository

> 仓库地址：https://github.com/xxred/skills
> 仓库类型：**VS Code Agent Plugins 1.0 插件包集合**

本仓库用于存放 **VS Code Agent Plugins 1.0 插件包集合**，每个插件独立封装架构文档、技能、Agent 角色、MCP 配置。**架构文档存放于对应插件内部 `docs/` 目录，不在仓库根目录存放业务架构文档。**

## 插件列表

| 插件 | 路径 | 版本 | 简介 |
|------|------|------|------|
| stable-arch-forge | `plugins/stable-arch-forge/` | v1.0.0 | 稳态发育多Agent架构落地插件：顶层元架构 + AI编程软件完整设计体系 + L1~L4 渐进式技能集，用于架构落地、偏差识别与系统癌变治理 |

## 快速上手

1. 进入插件目录 `plugins/stable-arch-forge/`
2. 阅读插件 `README.md` 与 `docs/` 架构基线
3. 从 L1 技能开始，严格按 `L1→L2→L3→L4` 顺序执行，每个技能通过门禁校验后进入下一技能

## 仓库规范

- 新增插件/技能请阅读 [`REPO_SPEC.md`](./REPO_SPEC.md)
- 每次新增、修改插件，同步更新：本 README 插件索引、插件内部 CHANGELOG.md、全局 `update-log.md`

## 更新日志

- 全局变更记录见 [`update-log.md`](./update-log.md)
