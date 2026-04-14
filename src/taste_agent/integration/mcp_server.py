"""MCP stdio server — Model Context Protocol integration for Claude Code."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

# MCP protocol types
JSONRPC_REQUEST = "2.0"
MCP_VERSION = "2024-11-05"


class MCPError(Exception):
    """MCP protocol error."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class MCPSTDIOServer:
    """MCP server using stdio transport.

    Implements the JSON-RPC 2.0 message protocol over stdin/stdout.
    Claude Code's MCP integration communicates via this protocol.
    """

    def __init__(self, name: str = "taste"):
        self.name = name
        self.logger = logging.getLogger(f"mcp.{name}")
        self._handlers: dict[str, callable] = {}
        self._tools: dict[str, dict] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register the MCP protocol request handlers."""
        self._handlers["initialize"] = self._handle_initialize
        self._handlers["tools/list"] = self._handle_tools_list
        self._handlers["tools/call"] = self._handle_tools_call
        self._handlers["shutdown"] = self._handle_shutdown

    def _register_tools(self) -> None:
        """Register available MCP tools."""

        self._tools = {
            "taste__evaluate": {
                "name": "taste__evaluate",
                "description": "Evaluate AI-generated output against taste.md standards. "
                              "Returns APPROVE / REVISE / REJECT verdict with specific feedback.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Description of the task that generated this output.",
                        },
                        "output_files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths that were generated.",
                        },
                        "file_contents": {
                            "type": "object",
                            "description": "Map of filename to file content.",
                        },
                        "diff": {
                            "type": "string",
                            "description": "Optional diff of changes.",
                        },
                    },
                    "required": ["task", "output_files"],
                },
            },
            "taste__lint": {
                "name": "taste__lint",
                "description": "Validate a taste.md file for contradictions and missing sections.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_root": {
                            "type": "string",
                            "description": "Path to the project root (default: cwd).",
                        },
                    },
                },
            },
            "taste__explain": {
                "name": "taste__explain",
                "description": "Mentor mode: explain WHY a specific issue matters.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "issue": {
                            "type": "string",
                            "description": "The issue description to explain.",
                        },
                        "dimension": {
                            "type": "string",
                            "description": "The taste dimension (aesthetic, ux, copy, etc.).",
                        },
                    },
                    "required": ["issue"],
                },
            },
        }

    async def _handle_initialize(self, params: dict) -> dict:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": MCP_VERSION,
            "serverInfo": {
                "name": self.name,
                "version": "0.2.0",
            },
            "capabilities": {
                "tools": {},
            },
        }

    async def _handle_tools_list(self, params: dict) -> dict:
        """Handle tools/list request."""
        self._register_tools()
        tools = [
            {"name": name, **tool}
            for name, tool in self._tools.items()
        ]
        return {"tools": tools}

    async def _handle_tools_call(self, params: dict) -> dict:
        """Handle tools/call request."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "taste__evaluate":
            result = await self._tool_evaluate(arguments)
        elif tool_name == "taste__lint":
            result = self._tool_lint(arguments)
        elif tool_name == "taste__explain":
            result = self._tool_explain(arguments)
        else:
            raise MCPError(-32602, f"Unknown tool: {tool_name}")

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str),
                }
            ]
        }

    async def _tool_evaluate(self, args: dict) -> dict:
        """Run taste evaluation via MCP tool."""

        from taste_agent import TasteAgent, TasteConfig

        project_root = Path(args.get("project_root", ".")).resolve()
        config = TasteConfig(enabled=True, require_taste_md=False)
        agent = TasteAgent(config, project_root=project_root)

        result = await agent.evaluate(
            task=args.get("task", "MCP evaluation"),
            output_files=args.get("output_files", []),
            file_contents=args.get("file_contents", {}),
            diff=args.get("diff", ""),
        )
        return {
            "verdict": result.verdict,
            "overall_score": result.overall_score,
            "reasoning": result.reasoning,
            "scores": result.scores,
            "issues": [
                {
                    "severity": i.severity.value,
                    "dimension": i.dimension,
                    "location": i.location,
                    "problem": i.problem,
                    "fix_required": i.fix_required,
                    "why_this_matters": i.why_this_matters,
                }
                for i in result.issues
            ],
            "revision_guidance": result.revision_guidance,
        }

    def _tool_lint(self, args: dict) -> dict:
        """Lint taste.md via MCP tool."""
        import re

        from taste_agent.models.taste_spec import TasteSpec

        project_root = Path(args.get("project_root", ".")).resolve()
        spec_path = project_root / "taste.md"

        if not spec_path.exists():
            return {"valid": False, "issues": ["taste.md not found"]}

        try:
            content = spec_path.read_text(encoding="utf-8", errors="replace")
            spec = TasteSpec.from_markdown(content)
        except Exception as e:
            return {"valid": False, "issues": [str(e)]}

        issues = []
        for attr in ["aesthetic_direction", "copy_voice", "non_negotiables"]:
            if not getattr(spec, attr, "").strip():
                issues.append(f"Section '{attr}' is empty or missing")

        for token in spec.color_tokens:
            if not re.match(r"^#[0-9a-fA-F]{6,8}$", token.hex):
                issues.append(f"Invalid hex color: {token.name}={token.hex}")

        return {"valid": len(issues) == 0, "issues": issues}

    def _tool_explain(self, args: dict) -> dict:
        """Mentor explain via MCP tool."""
        issue_text = args.get("issue", "")
        dimension = args.get("dimension")
        # Simple canned explanations
        explanations = {
            "aesthetic:placeholder copy": "Placeholder copy signals you haven't thought about who you're talking to. Enterprise buyers read every word — vague copy erodes trust immediately.",
            "aesthetic:generic": "Generic copy like 'Welcome to our platform' could describe any product. Specific copy signals that you understand your audience.",
            "ux:missing error state": "Error states are the moment users need most. Invisible errors cause users to distrust the system entirely.",
            "copy:hedging": "Words like 'maybe', 'might', 'could' undermine authority. Enterprise buyers need confidence.",
            "architecture:circular import": "Circular imports are a tax on the entire team. Every developer who touches this file pays it until the cycle is broken.",
            "naming:generic name": "Names like 'data', 'info', 'temp' carry no meaning. They force readers to decode the implementation to understand what's stored.",
            "adherence:spec violation": "The spec exists so the human doesn't repeat themselves. Violating it wastes the design investment.",
        }
        key = f"{dimension or 'adherence'}:{issue_text.lower()[:50]}"
        explanation = explanations.get(key, "This deviation from standards compounds over time. Address it before it becomes technical debt.")
        return {
            "dimension": dimension or "adherence",
            "why_this_matters": explanation,
            "issue": issue_text,
        }

    async def _handle_shutdown(self, params: dict) -> dict:
        """Handle shutdown request."""
        return {"success": True}

    async def run(self) -> None:
        """Run the MCP stdio server loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                self._send_error(-32700, "Parse error")
                continue

            method = request.get("method", "")
            params = request.get("params", {})
            msg_id = request.get("id")

            handler = self._handlers.get(method)
            if not handler:
                self._send_error(-32601, f"Method not found: {method}", msg_id)
                continue

            try:
                result = await handler(params)
                if msg_id is not None:
                    self._send_response(msg_id, result)
            except MCPError as e:
                self._send_error(e.code, e.message, msg_id, e.data)
            except Exception as e:
                self.logger.exception("Handler error")
                self._send_error(-32603, f"Internal error: {e}", msg_id)

    def _send_response(self, msg_id: Any, result: Any) -> None:
        """Send a JSON-RPC response."""
        response = {
            "jsonrpc": JSONRPC_REQUEST,
            "id": msg_id,
            "result": result,
        }
        print(json.dumps(response), flush=True)

    def _send_error(self, code: int, message: str, msg_id: Any = None, data: Any = None) -> None:
        """Send a JSON-RPC error."""
        response = {
            "jsonrpc": JSONRPC_REQUEST,
            "id": msg_id,
            "error": {
                "code": code,
                "message": message,
                "data": data,
            },
        }
        print(json.dumps(response), flush=True)


def main() -> None:
    """Entry point for MCP server."""
    logging.basicConfig(level=logging.WARNING)
    server = MCPSTDIOServer("taste")
    import asyncio
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
