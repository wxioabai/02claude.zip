# 1024 游戏（Flask 后端 + 排行榜）

一个 2048 变体小游戏，前端为单文件 `1024-game.html`，后端为 `app.py`（Flask + SQLite），实现分数存储与排行榜。

## 运行

```bash
# 1. 安装依赖（建议用虚拟环境）
python -m venv venv
venv\Scripts\activate          # Windows；macOS/Linux 用 source venv/bin/activate
pip install -r requirements.txt

# 2. 启动后端
python app.py
```

浏览器打开 <http://localhost:5000> 即可玩。首次访问会自动创建 `scores.db`。

## 接口

| 方法 | 路径          | 说明                                   |
| ---- | ------------- | -------------------------------------- |
| GET  | `/api/scores` | 返回 Top 10 排行榜                      |
| POST | `/api/scores` | 提交分数，请求体 `{"name":"昵称","score":123}` |

后端自带交互式接口文档：<http://localhost:5000/../> 之外可用 `curl` 快速测试：

```bash
curl -X POST http://localhost:5000/api/scores \
  -H "Content-Type: application/json" \
  -d '{"name":"小明","score":512}'

curl http://localhost:5000/api/scores
```

## 说明

- 前端默认从「同源」调用接口（由 Flask 托管页面）；如果直接用浏览器双击 `1024-game.html`（`file://` 协议），会自动回退到 `http://localhost:5000`，后端已开启 CORS 支持。
- 数据存在本地 `scores.db`（SQLite），删除该文件即清空排行榜。
