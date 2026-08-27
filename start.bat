@echo off
REM start.bat - Start PriceTracker on Windows

REM 1) 仮想環境が無ければ案内
if not exist ".venv\Scripts\python.exe" (
    echo 仮想環境が見つかりません。.venv がない場合は setup.bat を先に実行してください。
) else (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM 2) 依存関係の確認（インストール済みか簡易チェック）
python -c "import pkgutil,sys; reqs=['fastapi','uvicorn','sqlalchemy','jinja2']; missing=[r for r in reqs if not pkgutil.find_loader(r)]; sys.exit(0 if not missing else 1)"
if %ERRORLEVEL% neq 0 (
    echo 依存パッケージが見つかりません。setup.bat を実行してから再度お試しください。
    pause
    exit /b 1
)

REM 3) Uvicorn 起動（新しいコンソールで起動）
start "" cmd /k "call .venv\Scripts\activate.bat && uvicorn main:app --host 127.0.0.1 --port 8000"

REM 4) ブラウザで開く
start "" "http://localhost:8000"
exit /b 0
