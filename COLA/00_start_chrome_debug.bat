@echo off
chcp 65001 >nul
REM Chrome을 원격 디버깅 포트 9222로 실행합니다.
REM --user-data-dir 으로 별도 프로필 사용 → 새 프로세스가 반드시 9222 포트를 엽니다.

set CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe
set USER_DATA=%TEMP%\chrome_debug_9222

if not exist "%CHROME_EXE%" (
    echo 오류: Chrome을 찾을 수 없습니다. %CHROME_EXE%
    pause
    exit /b 1
)

echo 기존 Chrome 종료 중...
taskkill /IM chrome.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul

echo Chrome 실행 중 (포트 9222, 프로필: %USER_DATA%)...
start "" "%CHROME_EXE%" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%"
timeout /t 3 /nobreak >nul

echo 포트 9222 확인 중...
netstat -an | findstr 9222
if errorlevel 1 (
    echo 9222가 보이지 않습니다. 잠시 후 다시 netstat -an ^| findstr 9222 로 확인하세요.
) else (
    echo 위에 9222가 보이면 성공입니다. python auto.py 를 실행하세요.
)
pause
