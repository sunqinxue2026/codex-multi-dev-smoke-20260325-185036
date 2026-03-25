# Snack Store

一个使用 FastAPI + React 构建的零食商城 MVP。

## 功能

- 商品列表卡片
- 购物车
- 下单按钮
- FastAPI 接口与 React 页面联通
- 前端构建后可由 FastAPI 直接对外提供页面

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

## CI/CD

- `CI`：GitHub Actions 在 PR / push 时执行后端测试与前端构建
- `Deploy`：`main` 更新后自动上传到部署机，并重启应用进程

需要在 GitHub repository secrets 中配置：

- `DEPLOY_HOST`
- `DEPLOY_PORT`
- `DEPLOY_USER`
- `DEPLOY_PATH`
- `DEPLOY_SSH_PRIVATE_KEY`
