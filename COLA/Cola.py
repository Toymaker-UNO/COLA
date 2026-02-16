"""
Cola: COLA 오케스트레이션 진입점.
ChatGPT(브라우저)에 질문을 보내고 응답을 받아 반환한다.
MCP·CLI·다른 스크립트에서 공통으로 사용한다.

사용 전: 00_start_chrome_debug.bat 으로 Chrome을 9222 포트로 띄우고,
        chatgpt.com 탭을 연 뒤 사용하세요.
"""

import os

# 프로젝트 루트 기준 경로 (이 파일 위치 기준 상대 경로)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DOCS_DIR = os.path.join(_THIS_DIR, "Docs")
_DEFAULT_QUESTION_PATH = os.path.join(_THIS_DIR, "ZZZZ_CHATGPT_QUESTION.txt")
_DEFAULT_RESPONSE_PATH = os.path.join(_THIS_DIR, "ZZZZ_CHATGPT_RESPONSE.txt")


def _read_dir_files_sorted(dir_path: str) -> str:
    """디렉터리 내 모든 파일을 이름 순으로 읽어 합친 텍스트를 반환한다. 디렉터리가 없으면 빈 문자열."""
    if not os.path.isdir(dir_path):
        return ""
    parts = []
    names = sorted(f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
    for name in names:
        path = os.path.join(dir_path, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
        except OSError:
            pass
    return "\n".join(parts)


class Cola:
    """ChatGPT 브라우저에 질문을 보내고 응답 텍스트를 반환하는 진입점."""

    def __init__(
        self,
        question_path: str | None = None,
        response_path: str | None = None,
    ):
        self._question_path = question_path or _DEFAULT_QUESTION_PATH
        self._response_path = response_path or _DEFAULT_RESPONSE_PATH

    def make_chat_gpt_role(self) -> str:
        """Docs/ChatGptRole 전체 + Docs/Project 전체를 이름 순으로 읽어 합친 텍스트를 반환한다."""
        chatgpt_role = _read_dir_files_sorted(os.path.join(_DOCS_DIR, "ChatGptRole"))
        project = _read_dir_files_sorted(os.path.join(_DOCS_DIR, "Project"))
        return "\n".join(filter(None, [chatgpt_role, project]))

    def make_cursor_ai_role(self) -> str:
        """Docs/CursorAiRole 전체 + Docs/Project 전체를 이름 순으로 읽어 합친 텍스트를 반환한다."""
        cursor_role = _read_dir_files_sorted(os.path.join(_DOCS_DIR, "CursorAiRole"))
        project = _read_dir_files_sorted(os.path.join(_DOCS_DIR, "Project"))
        return "\n".join(filter(None, [cursor_role, project]))

    def check(self) -> bool:
        """
        실행 환경이 갖춰졌는지 확인한다.
        - 현재 디렉터리(Cola.py 기준)에 ChatGPT.py 존재
        - 현재 디렉터리에 chromedriver.exe 존재
        - ChatGPT().check_browser() 가 True
        - Docs 디렉터리 존재
        - Docs 아래 ChatGptRole, CursorAiRole, Project 디렉터리 존재 및 각각 파일 1개 이상
        모두 만족하면 True, 하나라도 아니면 False.
        """
        chatgpt_py = os.path.join(_THIS_DIR, "ChatGPT.py")
        chromedriver = os.path.join(_THIS_DIR, "chromedriver.exe")
        if not os.path.isfile(chatgpt_py):
            return False
        if not os.path.isfile(chromedriver):
            return False
        if not os.path.isdir(_DOCS_DIR):
            return False
        for subdir in ("ChatGptRole", "CursorAiRole", "Project"):
            path = os.path.join(_DOCS_DIR, subdir)
            if not os.path.isdir(path):
                return False
            has_file = any(
                os.path.isfile(os.path.join(path, f)) for f in os.listdir(path)
            )
            if not has_file:
                return False
        try:
            from ChatGPT import ChatGPT
            if not ChatGPT().check_browser():
                return False
        except Exception:
            return False
        return True

    def ask(self, question: str) -> str:
        """
        질문을 ChatGPT(브라우저)에 보내고, 응답 텍스트를 반환한다.
        Chrome이 9222 디버깅 포트로 열려 있고 ChatGPT 탭이 있어야 한다.

        :param question: ChatGPT에 보낼 질문 문자열
        :return: ChatGPT 응답 전체 텍스트 (실패 시 빈 문자열 또는 에러 메시지)
        """
        question = (question or "").strip()
        if not question:
            return ""

        from ChatGPT import ChatGPT

        qpath = os.path.abspath(self._question_path)
        rpath = os.path.abspath(self._response_path)

        try:
            with open(qpath, "w", encoding="utf-8") as f:
                f.write(question)
        except OSError as e:
            return f"[Cola] Failed to write question file: {e}"

        try:
            chatgpt = ChatGPT()
            chatgpt.get(qpath, rpath)
        except SystemExit:
            return "[Cola] ChatGPT run error (connection failed/timeout etc). Check Chrome and ChatGPT tab."
        except Exception as e:
            return f"[Cola] Error: {e}"

        try:
            with open(rpath, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            return f"[Cola] Failed to read response file: {e}"
