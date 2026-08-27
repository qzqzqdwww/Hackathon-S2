"""MCP Server — "Surprise-Plan" Track 03 Plugin.

Exposes one tool: generate_surprise_plan

Communication: JSON-RPC 2.0 over stdio (stdin/stdout).
Compatible with Claude Desktop, Claude Code, and any MCP client.

Usage with Claude Desktop:
    Add to claude_desktop_config.json:
    {
      "mcpServers": {
        "surprise-plan": {
          "command": "python",
          "args": ["-m", "surprise_plan.backend.mcp_server"],
          "env": {
            "LLM_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "sk-..."
          }
        }
      }
    }

Supports any AI provider via LLM_PROVIDER env var:
  anthropic, openai, deepseek, zhipu, stepfun, doubao, siliconflow, custom
"""

import sys
import json
import asyncio
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "surprise-plan"
SERVER_VERSION = "1.0.0"

TOOLS = [
    {
        "name": "generate_surprise_plan",
        "description": (
            "Generate a surprise learning plan that breaks the user out of "
            "their algorithmic filter bubble. The user provides their current "
            "interests; the tool randomly picks an UNRELATED domain and uses "
            "Claude API to create a structured 4-week learning path with "
            "creative bridges back to the user's stated interests."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "interests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "User's current areas of interest (e.g. ['AI', 'music', 'photography']). The tool will pick a domain NOT in this list.",
                    "minItems": 1,
                },
                "custom_animation": {
                    "type": "string",
                    "description": "Optional: URL or base64 of a custom whip animation (CSS/SVG/Lottie). If omitted, the default CSS whip animation is used.",
                },
            },
            "required": ["interests"],
        },
    }
]


def _make_response(req_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _make_error(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


async def handle_initialize(req_id: Any, params: dict) -> dict:
    return _make_response(req_id, {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
    })


async def handle_tools_list(req_id: Any, params: dict) -> dict:
    return _make_response(req_id, {"tools": TOOLS})


from ..backend.provider import generate_plan
from ..backend.domain_picker import pick_domain


async def handle_tools_call(req_id: Any, params: dict) -> dict:
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if tool_name != "generate_surprise_plan":
        return _make_error(req_id, -32601, f"Unknown tool: {tool_name}")

    interests = arguments.get("interests", [])
    if not interests:
        return _make_error(req_id, -32602, "interests must be a non-empty array")

    try:
        pick = pick_domain(interests)
        picked_domain = pick["domain"]
        plan = generate_plan(interests, picked_domain)

        return _make_response(req_id, {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "success",
                    "surprise_domain": picked_domain,
                    "surprise_score": pick["surprise_score"],
                    "plan": plan,
                    "animation_note": (
                        arguments.get("custom_animation") or "Default animation applies."
                    ),
                }, ensure_ascii=False, indent=2),
            }]
        })
    except Exception as e:
        return _make_response(req_id, {
            "content": [{
                "type": "text",
                "text": json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False),
                "isError": True,
            }]
        })


async def handle_notification(method: str) -> None:
    pass


METHOD_HANDLERS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


async def run_server() -> None:
    while True:
        try:
            loop = asyncio.get_running_loop()
            line = await loop.run_in_executor(None, sys.stdin.readline)
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        if req_id is None:
            await handle_notification(method)
            continue

        handler = METHOD_HANDLERS.get(method)
        response = await handler(req_id, params) if handler else _make_error(req_id, -32601, f"Method not found: {method}")

        print(json.dumps(response, ensure_ascii=False), flush=True)


def main() -> None:
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
