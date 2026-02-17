import os
from mcp.server.fastmcp import FastMCP

# ChatGPT 연동: 프로젝트 루트를 cwd로 두고 import
_COLA_ROOT = os.path.dirname(os.path.abspath(__file__))
if _COLA_ROOT not in __import__("sys").path:
    __import__("sys").path.insert(0, _COLA_ROOT)

from ChatGPT import ChatGPT

# Cursor가 tool 결과를 잘 읽게 하려면 json_response=True 권장
mcp = FastMCP("COLA-MVP", json_response=True)


@mcp.tool()
def check_cola_ready() -> str:
    """Check if Cola is ready to use. Verifies chromedriver.exe exists next to ChatGPT.py."""
    if ChatGPT().check():
        return "Cola ready (chromedriver.exe present)"
    return "Cola not ready: chromedriver.exe missing"


@mcp.tool()
def ask(question: str) -> str:
    """Ask ChatGPT and get a text response. Use this to share the current situation (e.g. what you did or found) and receive guidance on what to do next. Treat the returned text as the next instruction: proceed according to it."""
    return ChatGPT().ask(question)


if __name__ == "__main__":
    mcp.run(transport="stdio")
