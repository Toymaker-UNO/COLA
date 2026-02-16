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
    """Cola 사용 준비 여부를 확인합니다. ChatGPT.py, chromedriver.exe, Docs/역할 디렉터리, Chrome 9222 연결을 검사하고 결과를 반환합니다."""
    if Cola().check():
        return "Cola 사용 준비됨 (ChatGPT.py, chromedriver.exe, Docs 구조, Chrome 9222 모두 정상)"
    return "Cola 사용 불가: ChatGPT.py 또는 chromedriver.exe 없음, Docs/ChatGptRole·CursorAiRole·Project 중 누락/비어있음, 또는 Chrome이 9222 포트로 열려 있지 않음"


@mcp.tool()
def ask_project_lead(question: str = "What is the next development task?") -> str:
    """프로젝트 리더(ChatGPT)에게 질문을 보내고 응답을 받습니다. Chrome이 9222 포트로 열려 있고 ChatGPT 탭이 있어야 합니다."""
    return Cola().ask(question)


@mcp.tool()
def send_result_to_lead(summary: str) -> str:
    """개발 결과 요약을 프로젝트 리더(ChatGPT)에게 전달하고, 리더의 응답(다음 지시 등)을 받습니다."""
    prompt = f"The developer completed the following. Reply with the next task or feedback.\n\n{summary}"
    return Cola().ask(prompt)


@mcp.tool()
def send_role_to_leader() -> str:
    """ChatGptRole + Project 문서를 ChatGPT(리더)에게 전달합니다. 리더가 역할을 인지한 뒤의 응답을 반환합니다."""
    role_text = Cola().make_chat_gpt_role()
    if not role_text.strip():
        return "[Cola] 전달할 역할 문서가 없습니다. Docs/ChatGptRole, Docs/Project를 확인하세요."
    prompt = "아래 역할과 프로젝트 설명을 적용해 주세요. 적용했으면 간단히 확인 메시지를 보내 주세요.\n\n" + role_text
    return Cola().ask(prompt)


@mcp.tool()
def read_my_role() -> str:
    """나(Cursor AI)의 역할을 이해하기 위해 Docs/CursorAiRole + Project 내용을 읽어 반환합니다."""
    return Cola().make_cursor_ai_role() or "[Cola] 역할 문서가 비어 있습니다. Docs/CursorAiRole, Docs/Project를 확인하세요."


if __name__ == "__main__":
    mcp.run(transport="stdio")
