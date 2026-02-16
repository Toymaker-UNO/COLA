# COLA 요구사항 정의서 (requirement.md)

버전: v0.1 (MVP)
작성일: 2026-02-15
목적: ChatGPT(리더)와 CursorAI 및 GitHub Copilot(개발자/실행자)이 협업할 수 있도록 “중간 매개체” COLA를 구현한다.
단기 목표: ChatGPT(리더)와 GitHub Copilot 간 협업 할 수 있는 COLA 구현.
최종 목표: ChatGPT(리더)와 Cursor AI간 동일한 방식으로 협업에 참여시키는 구조로 확장한다.

---

## 1. 배경 및 문제 정의

대형/복잡한 개발 작업에서 “리더(의사결정/완료판정)”와 “개발자(구현/실행)” 역할을 분리하면 생산성과 품질이 증가한다.
그러나 ChatGPT(리더)는 IDE/파일시스템을 직접 조작하지 못하고, Copilot/Cursor(개발자)는 중간에 결정을 요구하거나 진행 상태를 체계적으로 보고하지 않아 작업이 끊긴다.

COLA는 다음을 해결한다.
- 리더가 목표를 작업(Task)으로 분해하고, 완료 기준(AC/DoD)을 정의한다.
- 개발자가 다음 작업을 가져가 구현한다.
- 개발 중 의사결정이 필요할 때 리더에게 질문하고, 답을 받아 계속 진행한다.
- 결과(코드 변경, 테스트 로그 등)를 제출하면 리더가 완료 여부를 판정한다.

---

## 2. 목표(Goals)

### 2.1 MVP 목표 (ChatGPT + GitHub Copilot 협업)
1) 문서 기반 프로젝트 정의를 읽고(예: `목표.md`, `chatgpt_role.md`, `copilot_role.md`),
2) 작업(Task) 큐를 만들고,
3) 개발자가 “다음 작업”을 조회하고,
4) 개발 중 질문을 리더에게 전달하고,
5) 결과를 제출하면 리더가 완료/수정을 판정하는
양방향 협업 루프를 제공한다.

### 2.2 최종 목표 (ChatGPT + Cursor AI 협업)
- MVP 구조를 유지한 채, 개발자 역할을 GitHub Copilot뿐 아니라 Cursor AI가 수행할 수 있도록 확장한다.
- 확장 방식은 “MCP(Server) 지원”을 우선 고려한다. (MVP에서는 MCP는 선택)

---

## 3. 비목표(Non-Goals)

- COLA가 IDE의 “프롬프트 입력창에 텍스트를 강제로 주입”하는 기능은 구현하지 않는다.
- COLA가 임의 명령을 무제한 실행하는 “원격 실행 봇”이 되는 것을 목표로 하지 않는다(보안 위험).
- 다중 사용자/클라우드 멀티테넌트는 MVP 범위에서 제외한다(단일 로컬 사용자 기준).

---

## 4. 사용 시나리오(Use Cases)

### UC-1: 목표 문서로 프로젝트 시작
- 사용자는 `project/` 폴더에 다음 파일을 준비한다.
  - `goal.md` (프로젝트 목표/제약/완료기준/빌드·테스트 명령 포함)
  - `role_leader.md` (ChatGPT 리더 역할)
  - `role_dev.md` (Copilot 개발자 역할)
- 사용자는 `cola init` 실행
- COLA는 문서를 읽고 프로젝트 상태 저장소를 생성한다.

### UC-2: 개발자가 다음 작업을 조회
- 개발자가 `cola get-next` 또는 API 호출로 다음 작업을 받는다.
- 응답에는 Task 설명, AC/DoD, 주의사항, 관련 파일/링크(있으면)가 포함된다.

### UC-3: 개발 중 의사결정 질문
- 개발자가 `cola ask`로 질문 + 선택지/제안/영향을 제출한다.
- COLA는 리더(ChatGPT)에게 질문을 전달하고 답을 반환한다.
- 개발자는 답을 반영해 계속 구현한다.

### UC-4: 결과 제출 및 완료 판정
- 개발자가 `cola submit`으로 diff/로그/노트를 제출한다.
- COLA는 리더(ChatGPT)에게 “완료 판정”을 요청한다.
- 리더는 PASS/FAIL + 사유/다음 액션을 반환한다.
- PASS면 다음 Task로 이동, FAIL이면 수정 Task를 생성하거나 기존 Task를 재오픈한다.

---

## 5. 시스템 아키텍처(권장)

MVP 권장 구성(로컬):
- COLA Core (Python)
  - 문서 로더/파서
  - 상태 저장소(파일 기반)
  - Task 엔진(상태 머신)
  - Leader Gateway (OpenAI API 호출)
  - CLI + (선택) HTTP API

확장(최종 Cursor 포함):
- COLA MCP Server (선택 모듈)
  - Cursor/Copilot이 Tool 호출로 COLA 기능을 사용하도록 제공

---

## 6. 기능 요구사항(Functional Requirements)

### 6.1 프로젝트 초기화
- FR-INIT-1: `goal.md`, `role_leader.md`, `role_dev.md`를 읽어 프로젝트를 초기화할 수 있어야 한다.
- FR-INIT-2: 프로젝트 상태 디렉토리(예: `.cola/`)를 생성하고 다음을 저장한다.
  - tasks(작업 목록)
  - decisions(의사결정 기록)
  - events(질문/응답/제출/판정 이벤트 로그)
  - config(경로/명령 allowlist 등)
- FR-INIT-3: 초기화 시 리더에게 “작업 분해”를 요청해 초기 Task 백로그를 생성할 수 있어야 한다.
  - 단, `goal.md`에 “이미 작업 목록이 제공된 경우”에는 리더 분해 없이 그대로 사용 가능해야 한다(옵션).

### 6.2 Task 관리(필수)
- FR-TASK-1: Task는 최소 다음 필드를 가져야 한다.
  - id, title, description, acceptance_criteria, status, priority, created_at, updated_at
  - optional: related_files, risk_level, estimated_scope, dependencies
- FR-TASK-2: 상태 머신을 지원해야 한다.
  - READY → IN_PROGRESS → (BLOCKED | NEEDS_REVIEW) → (DONE | READY/IN_PROGRESS)
- FR-TASK-3: “다음 작업”을 반환하는 기능이 있어야 한다.
  - 우선순위/의존성/상태를 고려한다.
- FR-TASK-4: 작업을 재오픈(rollback)하거나 수정 Task를 생성할 수 있어야 한다.

### 6.3 질문/결정 루프(양방향 핵심)
- FR-ASK-1: 개발자는 질문을 제출할 수 있어야 한다.
  - question (필수)
  - options (선택)
  - proposal (선택: 개발자의 추천)
  - impact (선택: 변경 영향/리스크/파일)
  - context (선택: 관련 diff/로그/파일 경로)
- FR-ASK-2: COLA는 질문을 리더에게 전달하고, 리더 답변을 개발자에게 반환해야 한다.
- FR-ASK-3: 모든 질문/답변은 decisions/events 로그로 저장되어야 한다.

### 6.4 결과 제출/완료 판정
- FR-SUB-1: 개발자는 작업 결과를 제출할 수 있어야 한다.
  - task_id
  - summary (무엇을 했는지)
  - diff (텍스트 또는 git diff 출력)
  - test_log (가능하면)
  - run_log (선택)
  - notes (선택)
- FR-REV-1: COLA는 제출물을 바탕으로 리더에게 완료 판정을 요청해야 한다.
- FR-REV-2: 리더의 판정 결과는 다음 중 하나여야 한다.
  - PASS: DONE 처리 + 다음 작업 진행
  - FAIL: 사유 + 구체적 수정 지시(필수) + 상태 갱신(READY/IN_PROGRESS) 또는 수정 Task 생성

### 6.5 빌드/테스트 실행(선택이지만 강력 권장)
- FR-RUN-1: `cola run-tests` 또는 API로 테스트/빌드 명령을 실행하고 로그를 수집할 수 있어야 한다.
- FR-RUN-2: 보안을 위해 명령 실행은 allowlist 기반이어야 한다.
  - 예: `pytest`, `ctest`, `cmake --build`, `ninja`, `gradle test` 등
- FR-RUN-3: 실행 결과는 exit_code, stdout, stderr, duration을 포함해야 한다.

### 6.6 인터페이스
MVP는 CLI 필수, HTTP API 선택.

#### CLI (필수)
- `cola init --project ./project --repo ./repo`
- `cola plan` (작업 목록/상태 출력)
- `cola get-next`
- `cola start <task_id>`
- `cola ask --task <task_id> --question "..."`
- `cola submit --task <task_id> --diff-file ... --test-log ...`
- `cola run-tests` (선택)
- `cola status` (현재 상태/최근 이벤트 출력)

#### HTTP API (선택)
- `POST /init`
- `GET /tasks/next`
- `POST /tasks/{id}/start`
- `POST /ask`
- `POST /submit`
- `POST /run-tests`
- `GET /status`

#### MCP Server (후순위/확장)
- Tool: `get_next_task`, `ask_leader`, `submit_result`, `run_tests`, `get_project_status`

---

## 7. 리더(Leader) 동작 요구사항 (ChatGPT 역할)

### 7.1 리더 입력
- 리더 호출 시 항상 다음 컨텍스트를 포함해야 한다.
  - `goal.md` 핵심 요약
  - `role_leader.md` 내용(시스템 프롬프트로 사용)
  - 현재 Task 상태/최근 이벤트
  - (질문/검토 시) 개발자 제출물(diff/log)

### 7.2 리더 출력 형식(구조화)
- 리더 응답은 반드시 “구조화된 JSON” 또는 “명확히 파싱 가능한 마크업”으로 받는다.
- 최소 스키마 예:
  - 계획(plan): tasks[]
  - 질문응답(decision): answer, rationale, next_steps
  - 완료판정(review): verdict(PASS/FAIL), reasons[], required_changes[]

### 7.3 리더 품질 규칙
- 완료 판정은 “증거 기반”이어야 한다(diff/log/AC).
- 모호하면 질문을 되돌려야 한다(추가 정보 요청).
- 큰 변경은 단계적으로 쪼개도록 지시해야 한다.

---

## 8. 개발자(Developer) 동작 요구사항 (Copilot 역할)

- “다음 작업”을 시작하기 전에 항상 AC/DoD를 확인한다.
- 다음 상황이면 반드시 질문을 올린다(ask):
  1) 아키텍처/프레임워크 선택
  2) 요구사항 불명확
  3) 대규모 삭제/리팩토링
  4) 테스트 실패 원인 불명확
  5) 보안/권한/외부 네트워크 접근 필요
- 제출물은 항상 diff + (가능하면) test_log를 포함한다.

---

## 9. 데이터/저장소 요구사항

### 9.1 저장 방식
- MVP는 파일 기반(로컬) 저장소를 사용한다.
- 기본 경로: `<repo>/.cola/`
- 포맷 권장:
  - `tasks.json` 또는 `tasks.jsonl`
  - `events.jsonl`
  - `decisions.jsonl`
  - `config.json`

### 9.2 감사/추적성
- 모든 상태 변경은 event로 남아야 한다(누가/언제/무엇을).

---

## 10. 보안 요구사항

- OpenAI API Key는 환경변수로만 읽는다(코드/로그에 노출 금지).
- `run_cmd`는 allowlist 기반, 작업 디렉토리 샌드박스(허용 경로 제한) 적용.
- diff/log에 비밀정보가 섞일 수 있으므로, 옵션으로 “민감정보 마스킹 규칙”을 둘 수 있어야 한다(후순위).

---

## 11. 비기능 요구사항(Non-Functional)

- NFR-1: Windows 11에서 실행 가능해야 한다(사용자 환경 기준).
- NFR-2: 실패해도 상태가 깨지지 않아야 한다(중단 후 재시작 가능).
- NFR-3: 응답 지연/에러 시 재시도 정책이 있어야 한다(예: OpenAI API 오류).
- NFR-4: 로그는 디버깅 가능 수준으로 남기되, 키/민감정보는 남기지 않는다.

---

## 12. 테스트 요구사항

- 최소 단위 테스트:
  - 문서 파싱/로드 테스트
  - 상태 머신 전이 테스트
  - Task selection(get-next) 로직 테스트
- 통합 테스트(로컬):
  - “질문→리더→응답” 루프(모킹 가능)
  - “제출→완료판정” 루프(모킹 가능)
- E2E(수동) 시나리오:
  - 샘플 `goal.md`로 init → get-next → ask → submit → pass/fail 확인

---

## 13. MVP 산출물(Deliverables)

- Python 소스코드(패키지 구조)
- 실행 가능한 CLI
- 샘플 프로젝트 폴더 템플릿:
  - `project/goal.md`
  - `project/role_leader.md`
  - `project/role_dev.md`
- README:
  - 설치/실행 방법
  - 예시 워크플로우(계산기 예제 등)
  - 보안 주의사항(run_cmd allowlist)

---

## 14. 단계별 로드맵

### Phase 1 (MVP)
- CLI + 파일 기반 상태 저장소
- OpenAI API Leader Gateway
- 핵심 루프: init / get-next / ask / submit / review

### Phase 2
- run-tests(allowlist) 추가
- HTTP API 추가(옵션)

### Phase 3 (Cursor 확장)
- MCP Server 모듈 추가
- Cursor에서 MCP로 get_next_task/ask_leader/submit_result 사용

---

## 15. 용어 정의(Glossary)

- Leader: 목표 설정/작업 분해/의사결정/완료 판정 역할(ChatGPT)
- Developer: 구현/실행/질문/보고 역할(GitHub Copilot 또는 Cursor)
- Task: 수행 단위 작업(AC/DoD 포함)
- AC/DoD: Acceptance Criteria / Definition of Done (검증 가능한 완료 기준)
- COLA: Leader와 Developer 사이의 협업 버스 및 도구 서버
- MCP: Model Context Protocol(확장 단계에서 사용)

---
