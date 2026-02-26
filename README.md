# fastService

基于 FastAPI 的高性能 Web 服务框架。

## 特性

- ⚡ 高性能 - 基于 FastAPI + Uvicorn
- 🔍 数据查询 - 支持多种数据源查询
- 📚 自动文档 - 内置 Swagger / ReDoc API 文档
- 🚀 异步支持 - 原生异步处理

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

或

```bash
uvicorn main:app --reload
```

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
fastService/
├── main.py              # 应用入口
├── requirements.txt     # 依赖
├── README.md           # 说明文档
├── app/
│   ├── __init__.py
│   ├── routes/         # 路由
│   ├── models/         # 数据模型
│   └── services/       # 业务逻辑
└── .gitignore
```

## License

MIT
