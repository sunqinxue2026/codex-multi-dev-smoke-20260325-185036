# Snack Store

一个使用 FastAPI + React 构建的零食商城 MVP。

## Backend

```bash
uv sync
uv run uvicorn snack_store.app:app --app-dir src --reload --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

前端默认通过 Vite 代理访问 `http://127.0.0.1:8000`。
