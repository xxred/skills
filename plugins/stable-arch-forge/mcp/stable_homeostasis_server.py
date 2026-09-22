#!/usr/bin/env python3
"""
stable-homeostasis MCP Server
=============================
为 `stable-arch-forge` Agent Plugin 提供配套 MCP 工具，将「发育稳态」四层架构
（目标场层 / 自组织协同层 / 稳态巡检层 / 边界约束层）与「软件发育系统」
（软件基因组 / 一致性引擎 / 质量门禁 / 生长预算 / 受约束编码）落地为可调用工具。

实现约束：
- 零第三方依赖，基于 MCP 协议（JSON-RPC 2.0 over stdio）实现。
- 所有工具的判定规则严格对齐插件 docs/ 架构基线：
  * 偏差分级阈值与综合偏差公式：docs/03_full_detail_design.md §4.1
  * 技术栈白名单 / 角色权限矩阵：docs/03_full_detail_design.md §1.1
  * 巡检五类检查项：docs/03_full_detail_design.md §4.2
  * 门禁默认拒绝原则：docs/02_agent_dev_architecture.md
  * 发育谱系 / 四类一致性检查 / 质量门禁 G1~G7 / 生长预算 / 开发上下文：docs/04_software_development_system.md

用法：
  python3 stable_homeostasis_server.py
（由插件 mcp.json 通过 stdio 启动）
"""

import json
import sys
import os

# ---------------------------------------------------------------------------
# 架构规则数据（对齐 docs/ 基线，禁止在此处私自变更架构定义）
# ---------------------------------------------------------------------------

# 综合偏差权重（详细设计 §4.1）
DEV_WEIGHTS = {
    "requirement": 0.4,   # 需求偏差
    "architecture": 0.3,  # 架构偏差
    "quality": 0.2,       # 质量偏差
    "progress": 0.1,      # 进度偏差
}

# 偏差分级（详细设计 §4.1）
DEVIATION_LEVELS = [
    {"min": 0.0, "max": 0.1, "level": "L0", "name": "正常", "biophor": "细胞状态正常", "dispose": "无需处置，持续观测"},
    {"min": 0.1, "max": 0.2, "level": "L1", "name": "普通偏差", "biophor": "细胞轻微异常", "dispose": "邻域提示，自动修复，当日闭环，无需上报"},
    {"min": 0.2, "max": 0.4, "level": "L2", "name": "严重偏差", "biophor": "细胞脱离邻域调控", "dispose": "巡检器介入，回滚到上一通过版本+整改清单，2个工作日内复检"},
    {"min": 0.4, "max": 0.6, "level": "L3", "name": "重度偏差", "biophor": "组织级发育异常", "dispose": "暂停模块开发，架构师介入定位根因，全模块排查，整改后全量巡检"},
    {"min": 0.6, "max": 1.01, "level": "L4", "name": "癌变级", "biophor": "恶性肿瘤", "dispose": "终止Agent，清除分支，回滚稳定版本，紧急排查，输出事故报告，人工介入"},
]

# 技术栈白名单（详细设计 §1.1）——不在白名单默认拒绝
TECH_WHITELIST = {
    "languages": ["TypeScript", "C#", "Python"],
    "frontend": ["Vue 3.x"],
    "backend": [".NET 8", "FastAPI"],
    "databases": ["MySQL 8.0", "Redis 7.x"],
    "versions": {"TypeScript": "5.4+", "C#": "10.0+", "Python": "3.10+", "Vue": "3.4+"},
}

# 角色权限矩阵（详细设计 §1.1）
ROLE_PERMISSIONS = {
    "requirement_agent":   {"code": "read:docs", "tools": ["requirement_split", "prototype_parse"], "forbidden": ["modify_code", "deploy"]},
    "architecture_agent":  {"code": "read:all", "tools": ["architecture_analyze", "dependency_analyze"], "forbidden": ["commit_code", "merge_branch"]},
    "dev_agent":           {"code": "read+write:dev_branch", "tools": ["code_gen", "static_check"], "forbidden": ["merge_main", "modify_prod_config", "modify_other_module"]},
    "test_agent":          {"code": "read+write:test_branch", "tools": ["test_gen", "test_run"], "forbidden": ["modify_business_code", "access_prod_data"]},
    "inspect_agent":       {"code": "read:all", "tools": ["scan", "analyze"], "forbidden": ["modify_any_code", "modify_config"]},
    "platform_engine":     {"code": "rw:rules_only", "tools": ["permission_manage", "gate_control"], "forbidden": ["run_business_logic", "gen_business_code"]},
}

# 禁止项清单（详细设计 §1.3 / §2.4）
FORBIDDEN_ITEMS = [
    "隐式全局状态", "循环依赖", "跨模块直接修改内部数据", "绕过门禁",
    "向上/跨层调用", "未授权依赖引入", "跳阶段/逆流程", "软约束替代硬门禁",
]

# 巡检五类检查项（详细设计 §4.2）
INSPECT_CHECKS = {
    "goal_trace":      {"name": "目标追溯检查", "desc": "产出物是否关联目标场目标"},
    "spec_compliance": {"name": "规约合规检查", "desc": "是否遵守全局刚性规约"},
    "arch_consistency": {"name": "架构一致性检查", "desc": "实现是否匹配架构模型"},
    "boundary_scan":   {"name": "边界越界扫描", "desc": "模块职责、依赖是否突破边界"},
    "whitelist_check": {"name": "技术栈白名单检查", "desc": "是否引入未授权依赖"},
}


# ---------------------------------------------------------------------------
# 核心判定逻辑
# ---------------------------------------------------------------------------

def _clamp01(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        v = 0.0
    return max(0.0, min(1.0, v))


def classify_deviation(deviation):
    """按综合偏差值分级（详细设计 §4.1）。"""
    deviation = _clamp01(deviation)
    for lvl in DEVIATION_LEVELS:
        if lvl["min"] <= deviation < lvl["max"]:
            return lvl
    return DEVIATION_LEVELS[-1]


def compute_gradient(current):
    """计算综合偏差（详细设计 §4.1 公式）。

    current: {requirement: 0~1, architecture: 0~1, quality: 0~100, progress: 0~1}
    偏差 = (1-需求)*0.4 + (1-架构)*0.3 + (100-质量)/100*0.2 + (1-进度)*0.1
    """
    req = 1.0 - _clamp01(current.get("requirement", 1.0))
    arch = 1.0 - _clamp01(current.get("architecture", 1.0))
    try:
        quality = max(0.0, min(100.0, float(current.get("quality", 100))))
    except (TypeError, ValueError):
        quality = 100.0
    qdev = (100.0 - quality) / 100.0
    prog = 1.0 - _clamp01(current.get("progress", 1.0))
    return {
        "requirement": round(req, 4),
        "architecture": round(arch, 4),
        "quality": round(qdev, 4),
        "progress": round(prog, 4),
    }


def compute_goal_gradient(agent_id, current):
    dim = compute_gradient(current)
    deviation = round(
        dim["requirement"] * DEV_WEIGHTS["requirement"]
        + dim["architecture"] * DEV_WEIGHTS["architecture"]
        + dim["quality"] * DEV_WEIGHTS["quality"]
        + dim["progress"] * DEV_WEIGHTS["progress"],
        4,
    )
    level = classify_deviation(deviation)
    # 优化优先级：按维度偏差降序
    priority = [k for k, _ in sorted(dim.items(), key=lambda kv: -kv[1])]
    return {
        "agent_id": agent_id,
        "deviation": deviation,
        "level": level["level"],
        "level_name": level["name"],
        "dimension_deviation": dim,
        "optimize_priority": priority,
        "suggest": "先修正优先级最高的维度，再触发邻域校验" if deviation > 0 else "当前与全局目标对齐",
    }


def peer_validate(output, neighbor_ids):
    """邻域横向校验（自组织协同层 peerValidate）。"""
    issues = []
    if not isinstance(output, dict):
        output = {}
    # 必需字段：目标追溯 + 基本完整性
    if not output.get("goal_id"):
        issues.append({"level": "error", "field": "goal_id", "desc": "产出物未锚定目标场目标（违反目标锚定原则）"})
    if not output.get("type"):
        issues.append({"level": "error", "field": "type", "desc": "产出物缺少类型声明（design/code/test/doc）"})
    if not output.get("content"):
        issues.append({"level": "warning", "field": "content", "desc": "产出物内容为空"})
    # 邻域数量约束：至少 2 个邻域节点
    neighbors = neighbor_ids or []
    if len(neighbors) < 2:
        issues.append({"level": "error", "field": "neighbors", "desc": f"邻域校验节点至少 2 个，当前 {len(neighbors)} 个"})
    passed = not any(i["level"] == "error" for i in issues)
    return {"passed": passed, "neighbor_ids": neighbors, "issues": issues}


def inspect_scan(targets):
    """稳态巡检五类检查（稳态巡检层）。"""
    if not isinstance(targets, dict):
        targets = {}
    report = []
    for key, meta in INSPECT_CHECKS.items():
        value = targets.get(key)
        if value is None:
            status = "skipped"
            detail = "未提供检查输入"
        elif value is True:
            status = "passed"
            detail = "通过"
        else:
            status = "failed"
            detail = str(value)
        report.append({"check": key, "name": meta["name"], "status": status, "detail": detail})
    failed = [r for r in report if r["status"] == "failed"]
    return {"passed": len(failed) == 0, "report": report, "failed_checks": [r["check"] for r in failed]}


def check_permission(agent_id, action, target):
    """边界门禁校验（边界约束层 checkActionPermission）——白名单默认拒绝。"""
    if agent_id not in ROLE_PERMISSIONS:
        return {"allowed": False, "reason": f"未注册角色 {agent_id}，默认拒绝"}
    perm = ROLE_PERMISSIONS[agent_id]
    forbidden = perm.get("forbidden", [])
    if action in forbidden:
        return {"allowed": False, "reason": f"角色 {agent_id} 被禁止执行 {action}"}
    if action in perm.get("tools", []):
        return {"allowed": True, "reason": f"动作 {action} 在角色 {agent_id} 工具白名单内"}
    # 不在工具白名单、也不在禁止项 → 按默认拒绝原则处理
    return {"allowed": False, "reason": f"动作 {action} 不在角色 {agent_id} 白名单内，默认拒绝"}


def boundary_rules(category):
    cat = (category or "all").lower()
    if cat in ("tech", "tech_stack", "technology"):
        return {"category": "tech_stack", "whitelist": TECH_WHITELIST, "default": "deny"}
    if cat in ("role", "permission", "role_permission"):
        return {"category": "role_permission", "matrix": ROLE_PERMISSIONS, "default": "deny"}
    if cat in ("forbidden", "forbidden_items"):
        return {"category": "forbidden_items", "items": FORBIDDEN_ITEMS}
    return {
        "category": "all",
        "tech_stack": TECH_WHITELIST,
        "role_permission": ROLE_PERMISSIONS,
        "forbidden_items": FORBIDDEN_ITEMS,
        "default": "deny",
    }


def goal_field_init(project_name, requirements, constraints):
    """初始化全局目标场（目标场层）。"""
    if not requirements:
        return {"error": "requirements 不能为空"}
    return {
        "project": project_name or "unnamed",
        "version": "v1.0.0",
        "field": {
            "requirement_alignment": 1.0,
            "architecture_compliance": 1.0,
            "quality_score": 100,
            "progress": 0.0,
        },
        "weights": DEV_WEIGHTS,
        "constraints": constraints or [],
        "status": "initialized",
        "note": "初始目标场：需求/架构/质量满分，进度为 0；后续通过 goal_gradient 实时计算偏差",
    }


def arch_consistency_audit(baseline_version, current_model):
    """架构一致性审计（稳态层 L4-04）：对比当前模型与基线，输出漂移报告。"""
    model = current_model or {}
    layers = model.get("layers") or {}
    expected_layers = ["target_field", "self_organizing", "stable_inspection", "boundary"]
    drift_points = []
    for layer in expected_layers:
        if layer not in layers:
            drift_points.append({"layer": layer, "status": "missing", "desc": "缺少该层，架构不完整"})
    violations = model.get("violations") or []
    for v in violations:
        drift_points.append({"layer": v.get("layer", "unknown"), "status": "violation", "desc": v.get("desc", "")})
    drift_ratio = len(drift_points) / (len(expected_layers) + max(len(violations), 1)) if drift_points else 0.0
    threshold = float(model.get("threshold", 0.3))
    over = drift_ratio > threshold
    return {
        "baseline_version": baseline_version or "v1.0.0",
        "expected_layers": expected_layers,
        "drift_points": drift_points,
        "drift_ratio": round(drift_ratio, 4),
        "threshold": threshold,
        "over_threshold": over,
        "dispose": "启动架构重构计划，修复漂移" if over else "记录漂移，持续观测",
    }


# ---------------------------------------------------------------------------
# 阶段导航路由（对齐 l0-arch-entry 入口技能的 L1~L4 状态机）
# ---------------------------------------------------------------------------

STAGES = [
    {
        "stage": "L1",
        "name": "认知层",
        "entry": "l0-arch-entry",
        "skills": ["l1-arch-cognition", "l1-risk-cancer-recognize"],
        "gate": "理解架构原理与癌变风险，能回答为什么这样设计",
        "tools": ["arch_route"],
    },
    {
        "stage": "L2",
        "name": "规约层",
        "entry": "l0-arch-entry",
        "skills": ["l2-global-spec", "l2-boundary-gate"],
        "gate": "全局刚性规约成文；边界门禁与白名单落地",
        "tools": ["boundary_rules", "check_permission"],
    },
    {
        "stage": "L3",
        "name": "分层设计层",
        "entry": "l0-arch-entry",
        "skills": [
            "l3-target-field-design",
            "l3-self-org-network",
            "l3-stable-inspect-design",
            "l3-boundary-layer-design",
            "l3-genome-model-design",
        ],
        "gate": "四层架构分层设计完成且互不矛盾；软件基因组（唯一真相源）建模完成",
        "tools": ["goal_field_init", "arch_consistency_audit", "genome_relation_audit"],
    },
    {
        "stage": "L4",
        "name": "稳态运行治理层",
        "entry": "l0-arch-entry",
        "skills": [
            "l4-dev-workflow",
            "l4-deviation-cancer-dispose",
            "l4-cross-layer-collab",
            "l4-arch-consistency-guard",
            "l4-consistency-engine",
            "l4-quality-gate",
            "l4-dev-context",
        ],
        "gate": "开发全流程走通；偏差分级处置；架构漂移受控；一致性引擎、质量门禁 G1~G7、受约束编码全部生效",
        "tools": ["goal_gradient", "peer_validate", "inspect_scan", "deviation_classify", "consistency_check", "quality_gate", "growth_budget", "dev_context_build"],
    },
]

# 技能 → 下一技能（依赖链，最后一个为空表示闭环）
SKILL_CHAIN = {
    "l0-arch-entry": "l1-arch-cognition",
    "l1-arch-cognition": "l1-risk-cancer-recognize",
    "l1-risk-cancer-recognize": "l2-global-spec",
    "l2-global-spec": "l2-boundary-gate",
    "l2-boundary-gate": "l3-target-field-design",
    "l3-target-field-design": "l3-self-org-network",
    "l3-self-org-network": "l3-stable-inspect-design",
    "l3-stable-inspect-design": "l3-boundary-layer-design",
    "l3-boundary-layer-design": "l3-genome-model-design",
    "l3-genome-model-design": "l4-dev-workflow",
    "l4-dev-workflow": "l4-deviation-cancer-dispose",
    "l4-deviation-cancer-dispose": "l4-cross-layer-collab",
    "l4-cross-layer-collab": "l4-arch-consistency-guard",
    "l4-arch-consistency-guard": "l4-consistency-engine",
    "l4-consistency-engine": "l4-quality-gate",
    "l4-quality-gate": "l4-dev-context",
    "l4-dev-context": "",
}

TASK_TO_STAGE = {
    "understand": "L1", "cognition": "L1", "认识": "L1", "认知": "L1",
    "spec": "L2", "constraint": "L2", "gate": "L2", "规约": "L2", "边界": "L2", "白名单": "L2",
    "design": "L3", "architecture": "L3", "分层": "L3", "设计": "L3", "genome": "L3", "model": "L3", "建模": "L3", "模型": "L3", "基因组": "L3",
    "dev": "L4", "develop": "L4", "code": "L4", "coding": "L4", "开发": "L4", "编码": "L4", "巡检": "L4", "运维": "L4",
    "consistency": "L4", "quality": "L4", "一致性": "L4", "质量门禁": "L4", "门禁": "L4", "context": "L4", "上下文": "L4",
}


def arch_route(task_type, current_stage, completed_skills):
    """阶段导航：返回当前阶段、下一技能、门禁要求与可用 MCP 工具。"""
    done = set(completed_skills or [])
    # 1) 根据已完成技能链定位第一个未完成技能（l0-arch-entry 是导航起点，视为已完成）
    next_skill = ""
    for skill, nxt in SKILL_CHAIN.items():
        if skill == "l0-arch-entry" or skill in done:
            continue
        next_skill = skill
        break
    if not next_skill:
        # 全部完成 → 闭环
        return {
            "status": "closed",
            "message": "全部技能已完成，架构闭环进入稳态运行态：按需重复 L4 巡检（inspect_scan）、一致性检查（consistency_check）与质量门禁（quality_gate）",
            "next_skill": "",
            "stage": "L4",
            "gate": "稳态循环：持续巡检与一致性监控，偏差 L3 以上暂停上报，未验证不等于完成",
            "tools": ["inspect_scan", "deviation_classify", "goal_gradient", "arch_consistency_audit",
                      "consistency_check", "quality_gate", "growth_budget", "dev_context_build"],
        }
    # 2) 找到该技能所属阶段
    stage_key = current_stage or TASK_TO_STAGE.get((task_type or "").lower(), "")
    current = None
    for s in STAGES:
        if next_skill in s["skills"]:
            current = s
            break
    if current is None:
        current = STAGES[0]
    stage_done = [sk for sk in current["skills"] if sk in done]
    stage_left = [sk for sk in current["skills"] if sk not in done]
    return {
        "status": "in_progress",
        "stage": current["stage"],
        "stage_name": current["name"],
        "next_skill": next_skill,
        "stage_progress": {"done": stage_done, "remaining": stage_left},
        "gate": current["gate"],
        "mcp_tools": current["tools"],
        "rule": "执行 next_skill 技能，产出技能正文全部交付物并校验门禁；门禁未全部通过禁止进入下一技能",
    }


# ---------------------------------------------------------------------------
# 软件发育系统工具（对齐 docs/04_software_development_system.md，v1.1.0 基线）
# ---------------------------------------------------------------------------

# 质量门禁 G1~G7 定义
QUALITY_GATES = [
    ("G1", "需求门禁（Requirement Gate）", "需求完整（含验收标准与状态机定义）"),
    ("G2", "设计门禁（Design Gate）", "Domain/Architecture/UI 足够明确"),
    ("G3", "契约门禁（Contract Gate）", "API/Event/State 已确定且无冲突"),
    ("G4", "实现门禁（Implementation Gate）", "Code 与开发上下文匹配，无越界实现"),
    ("G5", "验证门禁（Verification Gate）", "Tests 通过（证据链 REQ→CODE→COMMIT→TEST→PASS）"),
    ("G6", "一致性门禁（Consistency Gate）", "无关键漂移、冲突、未文档化增长"),
    ("G7", "发布门禁（Release Gate）", "当前版本形成可追踪 Baseline"),
]
# 生长预算默认限额（项目可配置）
DEFAULT_BUDGET_LIMITS = {
    "public_types": 20, "public_methods": 10, "direct_deps": 10,
    "cyclic_deps": 0, "arch_violations": 0, "dup_ratio": 0.2, "complexity": 10,
}


def genome_relation_audit(objects, relations):
    """发育谱系审计：检查每个核心对象的关系完整性，标记孤儿/未验证/未文档化增长。"""
    objs = objects or []
    rels = relations or []

    def _has(source, relation_types):
        return any(r.get("source") == source and r.get("relationType") in relation_types for r in rels)

    items, stats = [], {"total": len(objs), "aligned": 0, "orphaned": 0, "undocumented": 0, "unverified": 0}
    for o in objs:
        oid = o.get("id", "")
        otype = o.get("type", "")
        missing = []
        if otype in ("Requirement", "需求", "Feature", "功能"):
            # 需求/功能必须有实现与验证去向
            if not _has(oid, ("implemented-by", "realizes", "represented-by")):
                missing.append("无实现去向（implemented-by/realizes/represented-by 缺失）")
            if not _has(oid, ("verified-by",)):
                missing.append("无验证去向（verified-by 缺失 → UNVERIFIED）")
                stats["unverified"] += 1
            status = "UNVERIFIED" if missing else "ALIGNED"
        elif otype in ("CodeSymbol", "代码符号", "Code", "代码"):
            # 代码必须有来源（被 implemented-by 引用，即模型登记过的符号）
            has_source = any(r.get("target") == oid and r.get("relationType") == "implemented-by" for r in rels)
            if not has_source:
                missing.append("无模型来源 → UNDOCUMENTED_GROWTH（未文档化增长）")
                stats["undocumented"] += 1
            status = "UNDOCUMENTED" if missing else "ALIGNED"
        else:
            # 其他对象：至少有一条入边（derived-from/contains/refines/realizes 等来源关系）
            in_edges = [r for r in rels if r.get("target") == oid and r.get("relationType") in
                        ("derived-from", "contains", "refines", "realizes", "represented-by", "shaped-by")]
            if not in_edges:
                missing.append("无任何来源关系（ORPHANED 孤儿）")
                stats["orphaned"] += 1
            status = "ORPHANED" if missing else "ALIGNED"
        if not missing:
            stats["aligned"] += 1
        items.append({"object_id": oid, "type": otype, "status": status, "missing": missing})

    dispose = []
    if stats["orphaned"] > 0:
        dispose.append("孤儿对象：补充来源关系或归档移除")
    if stats["undocumented"] > 0:
        dispose.append("未文档化增长：进入审查状态，补充需求/设计/技术决策登记后方可视为正常功能")
    if stats["unverified"] > 0:
        dispose.append("未验证对象：补齐测试与证据链后进入 VERIFIED")
    return {"audit_items": items, "stats": stats, "dispose": dispose,
            "rule": "Canonical Model（规范模型）是唯一真相源；任何对象必须能回答：来自哪里/影响谁/实现在哪里/验证在哪里"}


def consistency_check(check_type, data):
    """一致性引擎四类检查（A 文档↔文档 / B 文档→代码 / C 代码→文档 / D 代码→约束），输出 CONSISTENCY_REPORT。"""
    check_type = (check_type or "all").upper()
    report = {"check_type": check_type, "details": [],
              "summary": {"Aligned": 0, "Stale": 0, "Conflict": 0, "Drifted": 0,
                          "Undocumented": 0, "Orphaned": 0, "Unverified": 0, "ArchitectureErrors": 0}}

    def _bump(key):
        report["summary"][key] = report["summary"].get(key, 0) + 1

    if check_type in ("A", "ALL"):
        # 文档↔文档：同一状态/枚举在各文档中的命名与取值集合一致性
        states = (data or {}).get("states") or {}  # {状态名: {文档: [取值...]}}
        for state, docs in states.items():
            sets = {}
            for doc, values in docs.items():
                sets[doc] = sorted(set(values or []))
            if len(sets) < 2:
                continue
            base = next(iter(sets.values()))
            for doc, vals in sets.items():
                if set(vals) != set(base):
                    drift = sorted(set(vals) - set(base)) + sorted(set(base) - set(vals))
                    report["details"].append({"object": state, "docs": [doc, next(iter(sets))],
                                              "kind": "DRIFTED", "desc": f"{doc} 取值集合不一致，差异: {drift}"})
                    _bump("Drifted")
    if check_type in ("B", "ALL"):
        # 文档→代码：需求是否实现，缺 Test → UNVERIFIED
        reqs = (data or {}).get("requirements") or []
        for r in reqs:
            if not r.get("has_code"):
                report["details"].append({"object": r.get("id", ""), "kind": "UNVERIFIED", "desc": "设计未实现（缺 Code）"})
                _bump("Unverified")
            elif not r.get("has_test"):
                report["details"].append({"object": r.get("id", ""), "kind": "UNVERIFIED", "desc": "实现缺 Test → UNVERIFIED"})
                _bump("Unverified")
    if check_type in ("C", "ALL"):
        # 代码→文档：未登记代码符号 → UNDOCUMENTED_GROWTH
        symbols = (data or {}).get("code_symbols") or []
        known = set((data or {}).get("known_symbols") or [])
        for sym in symbols:
            if sym not in known:
                report["details"].append({"object": sym, "kind": "UNDOCUMENTED_GROWTH",
                                          "desc": "代码符号无模型来源（未文档化增长）"})
                _bump("Undocumented")
    if check_type in ("D", "ALL"):
        # 代码→约束：架构违规/不变量破坏/生长预算超限
        violations = (data or {}).get("violations") or []
        for v in violations:
            report["details"].append({"object": v.get("target", ""), "kind": "ArchitectureErrors", "desc": v.get("desc", "")})
            _bump("ArchitectureErrors")
    summary = report["summary"]
    summary["Aligned"] = max(0, summary["Aligned"])
    return {"consistency_report": report,
            "dispose": ["冲突/漂移按偏差分级处置（deviation_classify）", "未文档化增长进入审查", "架构错误阻断发育直至修复"]}


def quality_gate(evidence):
    """质量门禁 G1~G7 逐级判定：evidence 形如 {G1: true/false} 或 {G1: {passed, note}}。"""
    ev = evidence or {}
    gates = []
    blocked_at = None
    for code, name, desc in QUALITY_GATES:
        item = ev.get(code)
        if isinstance(item, dict):
            passed, note = bool(item.get("passed")), item.get("note", "")
        else:
            passed, note = bool(item), ""
        gates.append({"gate": code, "name": name, "desc": desc, "passed": passed, "note": note})
        if not passed and blocked_at is None:
            blocked_at = code
    all_passed = blocked_at is None
    return {
        "gates": gates,
        "all_passed": all_passed,
        "blocked_at": blocked_at,
        "dispose": "进入下一发育阶段" if all_passed else f"阻断于 {blocked_at}：整改后重新执行对应门禁，禁止越级放行",
        "baseline": "本版本已标记为 Baseline（基线）" if all_passed else "未形成 Baseline",
        "rule": "只有通过 Gate 才允许进入下一阶段；判定以 Evidence（证据）为准，非人工勾选",
    }


def growth_budget(metrics, limits):
    """生长预算校验：控制异常增生（公开类型数/公开方法数/依赖数/循环依赖/架构违规/重复代码/复杂度）。"""
    limits = dict(DEFAULT_BUDGET_LIMITS, **(limits or {}))
    metrics = metrics or {}
    checks = []
    for metric, limit in limits.items():
        value = metrics.get(metric)
        if value is None:
            continue
        passed = value <= limit
        checks.append({"metric": metric, "value": value, "limit": limit, "passed": passed})
    violations = [c for c in checks if not c["passed"]]
    return {
        "checks": checks,
        "violations": violations,
        "overall_passed": len(violations) == 0,
        "dispose": "预算内，允许继续生长" if not violations else f"生长预算超限 {len(violations)} 项：{', '.join(v['metric'] for v in violations)}，必须收敛后再发育",
        "note": "Growth Budget（生长预算）是项目可配置边界，不是绝对真理",
    }


def dev_context_build(task_id, items):
    """构建 Development Context（开发上下文）包：约束 AI 按上下文执行，而非自由编码。"""
    items = items or {}
    required = ["requirements", "features", "contracts", "expectedCode", "tests"]
    missing = [k for k in required if not items.get(k)]
    ctx = {
        "taskId": task_id or "TASK-001",
        "requirements": items.get("requirements", []),
        "features": items.get("features", []),
        "architectureRules": items.get("architectureRules", []),
        "invariants": items.get("invariants", []),
        "contracts": items.get("contracts", []),
        "pages": items.get("pages", []),
        "expectedCode": items.get("expectedCode", []),
        "tests": items.get("tests", []),
    }
    return {
        "development_context": ctx,
        "complete": len(missing) == 0,
        "missing": missing,
        "workflow": ["读取开发上下文", "读取相关代码", "分析影响范围", "形成实现计划", "修改代码",
                     "运行测试", "运行架构检查", "运行契约检查", "运行一致性检查", "生成工作汇报"],
        "ai_prohibited": ["改变核心需求", "改变领域规则", "改变公共 API 语义", "增加未经记录的外部依赖",
                          "引入架构层级", "增加无对应需求的业务能力（须进入 Change/ADR）"],
        "dispose": "缺项时先回 Software Genome（软件基因组）补齐登记，禁止带缺项进入实现阶段",
    }


# ---------------------------------------------------------------------------
# 工具注册表（schema 采用 MCP inputSchema 格式）
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "goal_field_init",
        "description": "初始化全局目标场：输入项目名、需求描述与约束，生成四维目标场快照（目标场层）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "项目名称"},
                "requirements": {"type": "string", "description": "需求描述（PRD 要点）"},
                "constraints": {"type": "string", "description": "架构/技术约束"},
            },
            "required": ["requirements"],
        },
    },
    {
        "name": "goal_gradient",
        "description": "计算某 Agent 当前状态相对全局目标的偏差值与优化方向（getGoalGradient 接口实现）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent 标识"},
                "current": {
                    "type": "object",
                    "properties": {
                        "requirement": {"type": "number", "description": "需求对齐度 0~1"},
                        "architecture": {"type": "number", "description": "架构合规度 0~1"},
                        "quality": {"type": "number", "description": "代码质量分 0~100"},
                        "progress": {"type": "number", "description": "交付进度 0~1"},
                    },
                },
            },
            "required": ["agent_id", "current"],
        },
    },
    {
        "name": "peer_validate",
        "description": "邻域横向校验：校验产出物是否锚定目标场、是否满足至少 2 个邻域节点校验（peerValidate 接口实现）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string", "description": "关联目标场目标 ID"},
                        "type": {"type": "string", "description": "产出类型 design/code/test/doc"},
                        "content": {"type": "string", "description": "产出内容摘要"},
                    },
                    "required": ["goal_id", "type"],
                },
                "neighbor_ids": {"type": "array", "items": {"type": "string"}, "description": "邻域校验节点 ID 列表（至少 2 个）"},
            },
            "required": ["output"],
        },
    },
    {
        "name": "inspect_scan",
        "description": "稳态巡检五类检查：目标追溯/规约合规/架构一致/边界越界/白名单（true 通过，false 或字符串为失败原因）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "targets": {
                    "type": "object",
                    "properties": {
                        "goal_trace": {"type": "boolean"},
                        "spec_compliance": {"type": "boolean"},
                        "arch_consistency": {"type": "boolean"},
                        "boundary_scan": {"type": "boolean"},
                        "whitelist_check": {"type": "boolean"},
                    },
                },
            },
            "required": ["targets"],
        },
    },
    {
        "name": "deviation_classify",
        "description": "偏差分级判定：输入综合偏差值（0~1）或四维状态，输出 L0~L4 等级与对应处置建议（详细设计 §4.1）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deviation": {"type": "number", "description": "综合偏差值 0~1（与 current 二选一）"},
                "current": {
                    "type": "object",
                    "description": "四维状态，自动按公式计算综合偏差",
                    "properties": {
                        "requirement": {"type": "number"},
                        "architecture": {"type": "number"},
                        "quality": {"type": "number"},
                        "progress": {"type": "number"},
                    },
                },
            },
        },
    },
    {
        "name": "check_permission",
        "description": "边界门禁校验：按角色权限矩阵校验动作是否允许（白名单默认拒绝，checkActionPermission 接口实现）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent 角色：requirement_agent/architecture_agent/dev_agent/test_agent/inspect_agent/platform_engine"},
                "action": {"type": "string", "description": "要执行的动作"},
                "target": {"type": "string", "description": "动作目标"},
            },
            "required": ["agent_id", "action", "target"],
        },
    },
    {
        "name": "boundary_rules",
        "description": "查询边界规则：技术栈白名单 / 角色权限矩阵 / 禁止项清单",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "tech_stack / role_permission / forbidden_items / all"},
            },
        },
    },
    {
        "name": "arch_consistency_audit",
        "description": "架构一致性审计：对比当前系统模型与基线四层，输出漂移报告并判定是否触发重构（L4-04 技能落地）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "baseline_version": {"type": "string", "description": "基线版本号"},
                "current_model": {
                    "type": "object",
                    "properties": {
                        "layers": {"type": "object", "description": "四层实现情况 {target_field, self_organizing, stable_inspection, boundary}"},
                        "violations": {"type": "array", "items": {"type": "object"}, "description": "违规项列表 [{layer, desc}]"},
                        "threshold": {"type": "number", "description": "漂移阈值，默认 0.3"},
                    },
                },
            },
            "required": ["current_model"],
        },
    },
    {
        "name": "arch_route",
        "description": "阶段导航：根据已完成技能与任务类型，返回当前阶段、下一步要执行的技能、门禁要求与可用 MCP 工具（对齐 L0 入口技能状态机）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "description": "任务类型关键词：understand/spec/design/dev/consistency 或中文（认知/规约/设计/开发/建模/一致性/门禁）"},
                "current_stage": {"type": "string", "description": "当前阶段 L1~L4（可选，自动推断）"},
                "completed_skills": {"type": "array", "items": {"type": "string"}, "description": "已完成技能名列表（如 [\"l1-arch-cognition\"]）"},
            },
        },
    },
    {
        "name": "genome_relation_audit",
        "description": "发育谱系审计：检查软件基因组对象关系完整性，标记孤儿/未验证/未文档化增长（L3 软件基因组建模落地）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "objects": {
                    "type": "array",
                    "items": {"type": "object", "properties": {
                        "id": {"type": "string"}, "type": {"type": "string", "description": "Requirement/Feature/CodeSymbol 等"},
                    }},
                    "description": "基因组对象列表 [{id, type}]",
                },
                "relations": {
                    "type": "array",
                    "items": {"type": "object", "properties": {
                        "source": {"type": "string"}, "sourceType": {"type": "string"},
                        "relationType": {"type": "string"}, "target": {"type": "string"}, "targetType": {"type": "string"},
                    }},
                    "description": "统一关系列表 [{source, relationType, target}]",
                },
            },
            "required": ["objects", "relations"],
        },
    },
    {
        "name": "consistency_check",
        "description": "一致性引擎四类检查：A 文档↔文档 / B 文档→代码 / C 代码→文档（未文档化增长）/ D 代码→约束，输出 CONSISTENCY_REPORT（L4 一致性引擎落地）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "check_type": {"type": "string", "description": "A/B/C/D 或 ALL，默认 ALL"},
                "data": {
                    "type": "object",
                    "description": "按检查类型传入：A 用 states；B 用 requirements；C 用 code_symbols+known_symbols；D 用 violations",
                },
            },
            "required": ["data"],
        },
    },
    {
        "name": "quality_gate",
        "description": "质量门禁 G1~G7 逐级判定：输入各门禁证据，输出通过/阻断位置与基线结论（L4 质量门禁落地）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "evidence": {
                    "type": "object",
                    "description": "门禁证据 {G1: true/false 或 {passed, note}}，逐级 G1~G7",
                },
            },
            "required": ["evidence"],
        },
    },
    {
        "name": "growth_budget",
        "description": "生长预算校验：公开类型数/公开方法数/依赖数/循环依赖/架构违规/重复代码/复杂度超限检测（Growth Budget 落地）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "object",
                    "description": "当前度量 {public_types, public_methods, direct_deps, cyclic_deps, arch_violations, dup_ratio, complexity}",
                },
                "limits": {"type": "object", "description": "自定义限额（可选），默认 public_types<=20, public_methods<=10, direct_deps<=10, cyclic_deps=0, arch_violations=0, dup_ratio<=0.2, complexity<=10"},
            },
            "required": ["metrics"],
        },
    },
    {
        "name": "dev_context_build",
        "description": "构建 Development Context（开发上下文）包：taskId + 九要素，检查完整性并声明 AI 禁止变更项（L4 受约束编码落地）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "开发任务标识"},
                "items": {
                    "type": "object",
                    "description": "上下文要素 {requirements[], features[], architectureRules[], invariants[], contracts[], pages[], expectedCode[], tests[]}",
                },
            },
            "required": ["task_id", "items"],
        },
    },
]


# ---------------------------------------------------------------------------
# MCP stdio 协议循环（JSON-RPC 2.0）
# ---------------------------------------------------------------------------

def _respond(req_id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _tool_result(text):
    return {"content": [{"type": "text", "text": text}]}


def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        return _respond(rid, {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "stable-homeostasis", "version": "1.3.0"},
        })
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return _respond(rid, {})
    if method == "tools/list":
        return _respond(rid, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "goal_field_init":
                result = goal_field_init(args.get("project_name", ""), args.get("requirements", ""), args.get("constraints", ""))
            elif name == "goal_gradient":
                result = compute_goal_gradient(args.get("agent_id", ""), args.get("current", {}))
            elif name == "peer_validate":
                result = peer_validate(args.get("output", {}), args.get("neighbor_ids", []))
            elif name == "inspect_scan":
                result = inspect_scan(args.get("targets", {}))
            elif name == "deviation_classify":
                if "deviation" in args:
                    result = classify_deviation(args["deviation"])
                elif "current" in args:
                    dim = compute_gradient(args["current"])
                    dev = round(sum(dim[k] * DEV_WEIGHTS[k] for k in dim), 4)
                    lvl = classify_deviation(dev)
                    result = dict(lvl, deviation=dev, dimension_deviation=dim)
                else:
                    result = {"error": "需要 deviation 或 current 参数"}
            elif name == "check_permission":
                result = check_permission(args.get("agent_id", ""), args.get("action", ""), args.get("target", ""))
            elif name == "boundary_rules":
                result = boundary_rules(args.get("category", "all"))
            elif name == "arch_consistency_audit":
                result = arch_consistency_audit(args.get("baseline_version", ""), args.get("current_model", {}))
            elif name == "arch_route":
                result = arch_route(args.get("task_type", ""), args.get("current_stage", ""), args.get("completed_skills", []))
            elif name == "genome_relation_audit":
                result = genome_relation_audit(args.get("objects", []), args.get("relations", []))
            elif name == "consistency_check":
                result = consistency_check(args.get("check_type", "ALL"), args.get("data", {}))
            elif name == "quality_gate":
                result = quality_gate(args.get("evidence", {}))
            elif name == "growth_budget":
                result = growth_budget(args.get("metrics", {}), args.get("limits", {}))
            elif name == "dev_context_build":
                result = dev_context_build(args.get("task_id", ""), args.get("items", {}))
            else:
                return _respond(rid, None, {"code": -32601, "message": f"未知工具: {name}"})
            return _respond(rid, _tool_result(json.dumps(result, ensure_ascii=False, indent=2)))
        except Exception as exc:  # noqa: BLE001
            return _respond(rid, None, {"code": -32603, "message": f"工具执行失败: {exc}"})
    return _respond(rid, None, {"code": -32601, "message": f"未知方法: {method}"})


def main():
    # 幂等防双启动保护（可选）：若环境变量已注入插件根，可用于定位 docs/
    plugin_root = os.environ.get("PLUGIN_ROOT", "")
    if plugin_root:
        sys.stderr.write(f"[stable-homeostasis] plugin root: {plugin_root}\n")
        sys.stderr.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"[stable-homeostasis] 无效 JSON: {exc}\n")
            sys.stderr.flush()
            continue
        try:
            handle_request(req)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[stable-homeostasis] 处理异常: {exc}\n")
            sys.stderr.flush()
            if req.get("id") is not None:
                _respond(req.get("id"), None, {"code": -32603, "message": str(exc)})


if __name__ == "__main__":
    main()
