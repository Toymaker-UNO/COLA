import os
from mcp.server.fastmcp import FastMCP

# Cola 연동: 프로젝트 루트를 cwd로 두고 import
_COLA_ROOT = os.path.dirname(os.path.abspath(__file__))
if _COLA_ROOT not in __import__("sys").path:
    __import__("sys").path.insert(0, _COLA_ROOT)

from Cola import Cola

# Cursor가 tool 결과를 잘 읽게 하려면 json_response=True 권장
mcp = FastMCP("COLA-MVP", json_response=True)


@mcp.tool()
def check_cola_ready() -> str:
    """Check if Cola is ready to use. Verifies ChatGPT.py, chromedriver.exe, Docs/role dirs, and Chrome 9222 connection."""
    if Cola().check():
        return "Cola ready (ChatGPT.py, chromedriver.exe, Docs layout, Chrome 9222 all OK)"
    return "Cola not ready: missing ChatGPT.py or chromedriver.exe, or Docs/ChatGptRole·CursorAiRole·Project missing/empty, or Chrome not open on port 9222"


@mcp.tool()
def ask_project_leader(question: str = "What is the next development task?") -> str:
    """Send a question to the project leader (ChatGPT) and get a response. Chrome must be open on port 9222 with a ChatGPT tab."""
    return Cola().ask(question)


@mcp.tool()
def send_result_to_leader(summary: str) -> str:
    """Send a development result summary to the project leader (ChatGPT) and get the leader's response (next task or feedback)."""
    prompt = f"The developer completed the following. Reply with the next task or feedback.\n\n{summary}"
    return Cola().ask(prompt)


@mcp.tool()
def send_role_to_leader() -> str:
    """Send ChatGptRole + Project docs to ChatGPT (leader). Returns the leader's response after acknowledging the role."""
    role_text = Cola().make_chat_gpt_role()
    if not role_text.strip():
        return "[Cola] No role docs to send. Check Docs/ChatGptRole and Docs/Project."
    prompt = "Please apply the role and project description below. Reply briefly to confirm once applied.\n\n" + role_text
    return Cola().ask(prompt)


@mcp.tool()
def read_my_role() -> str:
    """Read and return Docs/CursorAiRole + Project content for the Cursor AI's role."""
    return Cola().make_cursor_ai_role() or "[Cola] Role docs are empty. Check Docs/CursorAiRole and Docs/Project."


if __name__ == "__main__":
    mcp.run(transport="stdio")
