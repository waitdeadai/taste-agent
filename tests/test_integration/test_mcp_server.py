"""tests/test_integration/test_mcp_server.py — MCP server JSON-RPC integration tests."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from taste_agent.integration.mcp_server import MCPSTDIOServer


@pytest.fixture
def mcp_server():
    return MCPSTDIOServer("taste")


class TestMCPInitialize:
    @pytest.mark.asyncio
    async def test_initialize_returns_protocol_version(self, mcp_server):
        result = await mcp_server._handle_initialize({})
        assert result["protocolVersion"] == "2024-11-05"
        assert result["serverInfo"]["name"] == "taste"
        assert "capabilities" in result


class TestMCPToolsList:
    @pytest.mark.asyncio
    async def test_tools_list_returns_tools(self, mcp_server):
        result = await mcp_server._handle_tools_list({})
        tools = result["tools"]
        tool_names = [t["name"] for t in tools]
        assert "taste__evaluate" in tool_names
        assert "taste__lint" in tool_names
        assert "taste__explain" in tool_names


class TestMCPToolsCall:
    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self, mcp_server):
        with pytest.raises(Exception):  # MCPError
            await mcp_server._handle_tools_call({"name": "unknown_tool", "arguments": {}})

    @pytest.mark.asyncio
    async def test_lint_returns_validation_result(self, mcp_server, tmp_path):
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n\n## 1. Visual Theme\nDark.\n\n## 6. Copy Voice\nDirect.\n\n## 7. Non-Negotiables\n1. No placeholder copy\n"
        )
        result = mcp_server._tool_lint({"project_root": str(tmp_path)})
        assert "valid" in result
        assert isinstance(result["issues"], list)

    @pytest.mark.asyncio
    async def test_explain_returns_mentor_guidance(self, mcp_server):
        result = mcp_server._tool_explain({"issue": "placeholder copy", "dimension": "copy"})
        assert "why_this_matters" in result
        assert len(result["why_this_matters"]) > 10

    @pytest.mark.asyncio
    async def test_explain_unknown_issue_fallback(self, mcp_server):
        result = mcp_server._tool_explain({"issue": "xyzzy unknown", "dimension": "copy"})
        assert "why_this_matters" in result
        assert "deviation" in result["why_this_matters"] or len(result["why_this_matters"]) > 0


class TestMCPProtocol:
    def test_jsonrpc_request_constant(self):
        from taste_agent.integration.mcp_server import JSONRPC_REQUEST
        assert JSONRPC_REQUEST == "2.0"

    def test_mcp_version_constant(self):
        from taste_agent.integration.mcp_server import MCP_VERSION
        assert MCP_VERSION == "2024-11-05"


class TestMCPJSONRPCErrors:
    @pytest.mark.asyncio
    async def test_unknown_method_returns_error(self, mcp_server):
        result = await mcp_server._handle({"jsonrpc": "2.0", "method": "unknown", "id": 1})
        assert "error" in result
        assert result["error"]["code"] == -32601

    @pytest.mark.asyncio
    async def test_missing_method_returns_error(self, mcp_server):
        result = await mcp_server._handle({"jsonrpc": "2.0", "params": {}, "id": 1})
        assert "error" in result

    @pytest.mark.asyncio
    async def test_empty_json_object(self, mcp_server):
        result = await mcp_server._handle({})
        assert "error" in result

    @pytest.mark.asyncio
    async def test_null_id_notification(self, mcp_server):
        # Notification with null id — returns None (no response per JSON-RPC spec)
        result = await mcp_server._handle({"jsonrpc": "2.0", "method": "initialize", "id": None})
        assert result is None


class TestMCPToolEvaluate:
    @pytest.mark.skip(reason="requires real LLM API credentials")
    @pytest.mark.asyncio
    async def test_evaluate_with_empty_task(self, mcp_server, tmp_path):
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n\n## 6. Copy Voice\nDirect.\n\n## 7. Non-Negotiables\n1. No placeholder copy\n"
        )
        result = await mcp_server._tool_evaluate({"task": "", "project_root": str(tmp_path)})
        assert "scores" in result or "issues" in result


class TestMCPLintInvalidInputs:
    @pytest.mark.asyncio
    async def test_lint_with_invalid_hex(self, mcp_server, tmp_path):
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n\n## 1. Visual Theme\nDark.\n\n## 6. Copy Voice\nDirect.\n\n## 7. Non-Negotiables\n1. No placeholder copy\n\n## Color Palette\n- primary: #GGGGGG (Background)\n"
        )
        result = mcp_server._tool_lint({"project_root": str(tmp_path)})
        assert isinstance(result, dict)
        assert "issues" in result
