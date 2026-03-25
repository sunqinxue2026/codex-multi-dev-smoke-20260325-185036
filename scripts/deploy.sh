#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-$(cd "$(dirname "$0")/.." && pwd)}"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"
DEPLOY_SUDO_PASSWORD="${DEPLOY_SUDO_PASSWORD:-}"

cd "$DEPLOY_PATH"

run_sudo() {
  if [ -n "$DEPLOY_SUDO_PASSWORD" ]; then
    printf '%s\n' "$DEPLOY_SUDO_PASSWORD" | sudo -S "$@"
    return
  fi
  sudo "$@"
}

if ! python3 -m venv .venv; then
  if ! python3 -m pip --version >/dev/null 2>&1; then
    run_sudo apt-get update
    run_sudo apt-get install -y python3-pip python3-venv
  fi

  if ! python3 -m venv .venv; then
    python3 -m pip install --user virtualenv
    python3 -m virtualenv .venv
  fi
fi
. .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .

if [ ! -f frontend/dist/index.html ]; then
  echo "frontend/dist/index.html 不存在，前端构建产物未上传成功。"
  exit 1
fi

mkdir -p logs run

if [ -f run/app.pid ] && kill -0 "$(cat run/app.pid)" 2>/dev/null; then
  kill "$(cat run/app.pid)"
  sleep 2
fi

nohup .venv/bin/python -m uvicorn snack_store.app:app --app-dir src --host "$APP_HOST" --port "$APP_PORT" > logs/app.log 2>&1 &
echo $! > run/app.pid

for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsS "http://127.0.0.1:${APP_PORT}/health" >/dev/null; then
    echo "部署成功，服务已启动。"
    exit 0
  fi
  sleep 2
done

echo "部署失败，健康检查未通过。"
exit 1
