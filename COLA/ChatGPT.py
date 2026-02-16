import socket
import os
import sys
import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChatGPT:
    DEFAULT_DEBUG_PORT = 9222
    CONNECT_TIMEOUT_SEC = 180
    PROMPT_SELECTOR = "#prompt-textarea"
    WAIT_TIMEOUT = 180
    POLL_INTERVAL_SEC = 1
    WAIT_BEFORE_FIRST_CLICK_SEC = 1.5  # 새 버튼 감지 후 가림 레이어 안정화 대기
    WAIT_AFTER_CLICK_SEC = 2
    POLL_TIMEOUT_SEC = 180
    TEMP_HTML_PATTERN = "ZZZZ_CHATGPT_TEMP_%04d.html"  # 0000, 0001, ...
    PRINT_FLAG = False

    def __init__(self):
        self._driver = None
        self._work_dir = None
        self._temp_html_files = []
        self._temp_counter = 0

    def _stdout_print(self, *args, **kwargs) -> None:
        if self.PRINT_FLAG:
            print(*args, **kwargs)

    def check_browser(self, port: int | None = None) -> bool:
        """지정 포트에 Chrome 디버깅이 떠 있으면 True, 없으면 False. port 생략 시 DEFAULT_DEBUG_PORT 사용."""
        if port is None:
            port = self.DEFAULT_DEBUG_PORT
        try:
            with socket.create_connection(("localhost", port), timeout=2):
                return True
        except (socket.error, OSError):
            return False

    def _save_html_to(self, a_path: str) -> None:
        """현재 페이지 소스를 a_path 에 저장한다."""
        with open(a_path, "w", encoding="utf-8") as f:
            f.write(self._driver.page_source)

    def _get_copy_buttons_with_good_response_right(self):
        """오른쪽에 '좋은 응답' 버튼이 있는 복사 버튼만 반환한다 (순서 유지)."""
        copy_buttons = self._driver.find_elements(
            By.CSS_SELECTOR, "button[data-testid='copy-turn-action-button']"
        )
        result = []
        for btn in copy_buttons:
            try:
                next_btn = btn.find_element(By.XPATH, "./following-sibling::button[1]")
                aria = next_btn.get_attribute("aria-label") or ""
                if "좋은 응답" in aria:
                    result.append(btn)
            except Exception:
                continue
        return result

    def _count_copy_buttons_with_good_response_right(self) -> int:
        """오른쪽에 '좋은 응답'이 있는 복사 버튼 개수를 반환한다."""
        return len(self._get_copy_buttons_with_good_response_right())

    def _get_response_text_from_turn(self, a_copy_button) -> str:
        """
        복사 버튼이 속한 턴(assistant 응답)에서 응답 텍스트를 DOM으로 추출한다.
        클릭/클립보드 없이 사용하므로 가림·isTrusted 문제를 피한다.
        """
        try:
            return self._driver.execute_script(
                """
                var btn = arguments[0];
                var turn = btn.closest('[data-turn="assistant"]') || btn.closest('.agent-turn');
                if (!turn) return '';
                var content = turn.querySelector('.markdown') || turn.querySelector('.prose')
                    || turn.querySelector('[data-message-author-role="assistant"]')
                    || turn.querySelector('[class*="markdown"]');
                if (!content) {
                    var textBlock = turn.querySelector('[class*="flex"][class*="flex-col"]');
                    if (textBlock) content = textBlock;
                    else content = turn;
                }
                return (content && content.innerText) ? content.innerText.trim() : '';
                """,
                a_copy_button,
            ) or ""
        except Exception:
            return ""

    def _get_clipboard_text(self) -> str:
        """시스템 클립보드 텍스트를 반환한다."""
        try:
            from tkinter import Tk
            r = Tk()
            r.withdraw()
            r.update()
            s = r.clipboard_get()
            r.destroy()
            return s or ""
        except Exception:
            return ""

    def _next_temp_html(self) -> str:
        path = os.path.join(self._work_dir, self.TEMP_HTML_PATTERN % self._temp_counter)
        self._temp_counter += 1
        return path

    def _delete_temp_files(self) -> None:
        """수집한 임시 HTML 파일들을 삭제한다."""
        for p in self._temp_html_files:
            try:
                if os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass

    def _connect_driver(self) -> None:
        """디버깅 포트로 Chrome에 연결하고 self._driver에 설정한다. 실패 시 sys.exit(1)."""
        port = self.DEFAULT_DEBUG_PORT
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{port}")

        self._stdout_print("이미 열린 Chrome에 연결 중... (포트 %d)" % port, flush=True)
        result = [None]

        def connect() -> None:
            try:
                result[0] = webdriver.Chrome(options=chrome_options)
            except Exception as a_e:
                result[0] = a_e

        t = threading.Thread(target=connect, daemon=True)
        t.start()
        t.join(timeout=self.CONNECT_TIMEOUT_SEC)

        if t.is_alive():
            self._stdout_print(
                "연결 시간 초과(%d초). Chrome이 포트 %d로 실행 중인지 확인하세요."
                % (self.CONNECT_TIMEOUT_SEC, port),
                file=sys.stderr,
            )
            sys.exit(1)
        if isinstance(result[0], Exception):
            self._stdout_print("Chrome 연결 실패: %s" % result[0], file=sys.stderr)
            sys.exit(1)

        self._driver = result[0]
        self._stdout_print("Chrome 연결됨. 현재 탭에서 입력창을 찾는 중...", flush=True)

    def _ensure_prompt_ready(self) -> None:
        """입력창이 보이고 클릭 가능할 때까지 대기한다. 실패 시 sys.exit(1)."""
        wait = WebDriverWait(self._driver, self.WAIT_TIMEOUT)
        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.PROMPT_SELECTOR))
            )
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.PROMPT_SELECTOR)))
        except Exception as a_e:
            self._stdout_print(
                "입력창을 찾지 못했습니다. 현재 탭이 ChatGPT 페이지인지 확인하세요. (%s)" % a_e,
                file=sys.stderr,
            )
            sys.exit(1)

    def _send_question_and_wait_response(
        self, a_text_to_send: str, a_response_path: str
    ) -> None:
        """질문 전송 후 새 응답이 나올 때까지 폴링하고, 응답을 a_response_path에 저장한다."""
        prompt_el = self._driver.find_element(By.CSS_SELECTOR, self.PROMPT_SELECTOR)

        path_before = self._next_temp_html()
        self._save_html_to(path_before)
        self._temp_html_files.append(path_before)
        prev_count = self._count_copy_buttons_with_good_response_right()
        self._stdout_print("전송 전 '복사(오른쪽에 좋은 응답)' 버튼 개수: %d" % prev_count, flush=True)

        preview = a_text_to_send[:50] + ("..." if len(a_text_to_send) > 50 else "")
        self._stdout_print('"%s" 입력 및 전송...' % preview, flush=True)
        prompt_el.click()
        prompt_el.send_keys(a_text_to_send)
        prompt_el.send_keys(Keys.ENTER)

        deadline = time.time() + self.POLL_TIMEOUT_SEC
        while time.time() < deadline:
            time.sleep(self.POLL_INTERVAL_SEC)
            path = self._next_temp_html()
            self._save_html_to(path)
            self._temp_html_files.append(path)
            curr_count = self._count_copy_buttons_with_good_response_right()
            if curr_count != prev_count + 1:
                continue

            text = ""
            buttons = self._get_copy_buttons_with_good_response_right()
            if buttons:
                new_btn = buttons[-1]
                time.sleep(self.WAIT_BEFORE_FIRST_CLICK_SEC)
                text = self._get_response_text_from_turn(new_btn)
                if not text:
                    try:
                        self._driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", new_btn
                        )
                        time.sleep(0.3)
                        self._driver.execute_script("arguments[0].click();", new_btn)
                        time.sleep(self.WAIT_AFTER_CLICK_SEC)
                        text = self._get_clipboard_text()
                    except Exception as a_e:
                        self._stdout_print("클립보드 폴백 실패: %s" % a_e, file=sys.stderr)

            with open(a_response_path, "w", encoding="utf-8") as f:
                f.write(text)
            self._stdout_print("응답 내용을 %s 에 저장했습니다." % a_response_path, flush=True)
            self._stdout_print("임시 HTML 파일을 삭제했습니다.", flush=True)
            self._delete_temp_files()
            return

        self._stdout_print(
            "시간 초과: 새 복사 버튼이 %d초 안에 나타나지 않았습니다." % self.POLL_TIMEOUT_SEC,
            file=sys.stderr,
        )
        self._delete_temp_files()

    def get(self, a_question: str, a_response: str) -> None:
        """
        질문 파일을 읽어 전송하고, 응답을 지정한 파일에 저장한다.

        :param a_question: 질문 내용이 들어 있는 텍스트 파일 경로
        :param a_response: 응답을 저장할 텍스트 파일 경로
        """
        question_path = os.path.abspath(a_question)
        response_path = os.path.abspath(a_response)

        if not os.path.isfile(question_path):
            self._stdout_print("질문 파일을 찾을 수 없습니다: %s" % question_path, file=sys.stderr)
            sys.exit(1)

        with open(question_path, "r", encoding="utf-8") as f:
            text_to_send = f.read().strip()
        # ChatGPT 입력창에 넣을 때 모든 엔터 제거 (한 줄로 전송)
        text_to_send = text_to_send.replace("\r\n", "\n").replace("\n", "").replace("\r", "")

        if not text_to_send:
            self._stdout_print("질문 파일이 비어 있습니다: %s" % question_path, file=sys.stderr)
            sys.exit(1)

        # 응답 파일을 없으면 생성, 있으면 비우기
        with open(response_path, "w", encoding="utf-8"):
            pass

        self._work_dir = os.path.dirname(os.path.abspath(__file__))
        self._temp_html_files = []
        self._temp_counter = 0

        self._connect_driver()
        self._ensure_prompt_ready()
        self._send_question_and_wait_response(text_to_send, response_path)


def main() -> None:
    """ChatGPT 인스턴스를 만들고, 질문/응답 파일 경로로 get()을 호출한다."""
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) >= 3:
        question_path = sys.argv[1]
        response_path = sys.argv[2]
    else:
        question_path = os.path.join(_script_dir, "ZZZZ_CHATGPT_QUESTION.txt")
        response_path = os.path.join(_script_dir, "ZZZZ_CHATGPT_RESPONSE.txt")
    chatgpt = ChatGPT()
    if False == chatgpt.check_browser():
        print(f"브라우저 연결 상태: False")
    chatgpt.get(question_path, response_path)


if __name__ == "__main__":
    main()
