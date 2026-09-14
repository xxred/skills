#!/usr/bin/env python3
"""
arch-gate：stable-arch-forge 硬约束钩子（PreToolUse）
======================================================
依据「迭代治理规则」实施硬门禁：
  规则：禁止私自修改技能绕过架构约束；必须先更新 docs/ 基线，再同步改技能。
  落地：拦截对插件 skills/ 目录内文件的直接写操作（Write/Edit/NotebookEdit 等）。
       - 目标在 skills/ → block（必须先走「更新 docs/ 基线」流程）
       - 目标在 docs/ → approve（架构基线允许更新，但须同步 arch-version-log.md，由技能约束）
       - 其他 → approve
  若环境变量 STABLE_ARCH_GATE=1，则全部放行（显式门禁通行，用于已走完正式流程的场景）。

协议：Claude Code hook 兼容格式（VS Code Copilot 解析）。
  stdin  : {"session_id": "...", "tool_name": "Edit", "tool_input": {"file_path": "..."}, "cwd": "..."}
  stdout : {"hookSpecificOutput": {"hookEventName": "PreToolUse", "decision": "block|approve", "reason": "..."}}
"""

import json
import os
import sys

# 需要拦截的写工具（工具名因客户端而异，覆盖常见命名）
WRITE_TOOLS = {"write", "edit", "notebookedit", "create", "mcpwritefile", "createfile"}

# 受保护的相对目录（相对插件根 PLUGIN_ROOT）
PROTECTED_DIRS = ("skills",)


def _plugin_root():
    root = os.environ.get("PLUGIN_ROOT", "") or os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not root:
        # 兜底：脚本所在目录向上两级（com.github.copilot/hooks → 插件根）
        root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    return root


def _extract_target(tool_input):
    """从工具输入中提取目标路径。"""
    if not isinstance(tool_input, dict):
        return None
    for key in ("file_path", "filePath", "path", "filepath", "filename"):
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            return val
    return None


def _decide(tool_name, target, plugin_root):
    if tool_name not in WRITE_TOOLS:
        return "approve", "非写操作，放行"
    if not target:
        return "approve", "未解析到目标路径，放行"
    try:
        abs_target = os.path.abspath(target)
    except Exception:  # noqa: BLE001
        return "approve", "目标路径解析失败，放行"
    if not abs_target.startswith(plugin_root):
        return "approve", "目标不在插件目录内，放行"
    rel = os.path.relpath(abs_target, plugin_root).replace("\\", "/")
    top = rel.split("/", 1)[0] if "/" in rel else rel
    if top in PROTECTED_DIRS:
        if os.environ.get("STABLE_ARCH_GATE") == "1":
            return "approve", "已通过正式门禁（STABLE_ARCH_GATE=1），允许修改技能"
        return "block", (
            f"硬门禁拦截：禁止直接修改插件 skills/ 目录（{rel}）。"
            "必须先更新 docs/ 架构基线（docs/03_full_detail_design.md 等）并记录 arch-version-log.md，"
            "再经正式流程同步修改技能；如需紧急放行请设置 STABLE_ARCH_GATE=1。"
        )
    return "approve", "目标不在保护目录内，放行"


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "decision": "approve", "reason": "空输入，放行"}}))
            return
        event = json.loads(raw)
        tool_name = str(event.get("tool_name", "")).lower()
        tool_input = event.get("tool_input") or {}
        target = _extract_target(tool_input)
        decision, reason = _decide(tool_name, target, _plugin_root())
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "decision": decision,
            "reason": reason,
        }}, ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001
        # 钩子自身异常不得阻塞正常流程
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "decision": "approve",
            "reason": f"arch-gate 自身异常，放行（{exc}）",
        }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
