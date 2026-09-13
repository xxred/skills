#!/usr/bin/env python3
"""
stable-homeostasis MCP Server
=============================
为 `stable-arch-forge` Agent Plugin 提供配套 MCP 工具，将「发育稳态」四层架构
（目标场层 / 自组织协同层 / 稳态巡检层 / 边界约束层）的能力落地为可调用工具。

实现约束：
- 零第三方依赖，基于 MCP 协议（JSON-RPC 2.0 over stdio）实现。
- 所有工具的判定规则严格对齐插件 docs/ 架构基线：
  * 偏差分级阈值与综合偏差公式：docs/03_full_detail_design.md §4.1
  * 技术栈白名单 / 角色权限矩阵：docs/03_full_detail_design.md §1.1
  * 巡检五类检查项：docs/03_full_detail_design.md §4.2
  * 门禁默认拒绝原则：docs/02_agent_dev_architecture.md

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
    """计算综合偏差（详细设计 §4.1 公式）。"""
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
    if not output.get("goal_id"):
        issues.append({"level": "error", "field": "goal_id", "desc": "产出物未锚定目标场目标（违反目标锚定原则）"})
    if not output.get("type"):
        issues.append({"level": "error", "field": "type", "desc": "产出物缺少类型声明（design/code/test/doc）"})
    if not output.get("content"):
        issues.append({"level": "warning", "field": "content", "desc": "产出物内容为空"})
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
            "serverInfo": {"name": "stable-homeostasis", "version": "1.0.0"},
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
            else:
                return _respond(rid, None, {"code": -32601, "message": f"未知工具: {name}"})
            return _respond(rid, _tool_result(json.dumps(result, ensure_ascii=False, indent=2)))
        except Exception as exc:  # noqa: BLE001
            return _respond(rid, None, {"code": -32603, "message": f"工具执行失败: {exc}"})
    return _respond(rid, None, {"code": -32601, "message": f"未知方法: {method}"})


def main():
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
