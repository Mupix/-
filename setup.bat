@echo off
REM setup.bat - 初回セットアップ: 仮想環境作成と依存インストール（Windows）

REM 1) Python の確認
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python が見つかりません。Python 3.12+ をインストールして PATH に追加してください。
    pause
    exit /b 1
)

REM 2) 仮想環境作成
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM 3) pip 更新と依存インストール
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 4) データベース用ディレクトリ
if not exist "database" mkdir database
echo Setup complete.
pause
