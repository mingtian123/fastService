# fastService

基于 FastAPI + SQLite 的高性能 Web 数据服务。

## 特性

- ⚡ 高性能 - 基于 FastAPI + Uvicorn
- 🗄️ SQLite 数据库 - 轻量级，无需额外配置
- 🔍 完整 CRUD - 用户/订单/产品的增删改查
- 📊 数据统计 - 内置统计接口
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
├── .gitignore
├── fastservice.db      # SQLite 数据库（自动生成）
└── app/
    ├── __init__.py
    ├── database.py     # 数据库配置和模型
    ├── routes/         # 路由
    │   ├── health.py   # 健康检查
    │   └── crud.py     # CRUD接口
    └── models/         # 数据模型
        └── schemas.py  # Pydantic模型
```

## API 接口

### 健康检查
- `GET /api/v1/health` - 服务健康状态

### 用户管理
- `GET /api/v1/users` - 用户列表（支持搜索）
- `GET /api/v1/users/{id}` - 获取单个用户
- `POST /api/v1/users` - 创建用户
- `PUT /api/v1/users/{id}` - 更新用户
- `DELETE /api/v1/users/{id}` - 删除用户

### 订单管理
- `GET /api/v1/orders` - 订单列表（支持筛选）
- `GET /api/v1/orders/{id}` - 获取单个订单
- `POST /api/v1/orders` - 创建订单
- `PUT /api/v1/orders/{id}` - 更新订单
- `DELETE /api/v1/orders/{id}` - 删除订单

### 产品管理
- `GET /api/v1/products` - 产品列表（支持价格筛选）
- `GET /api/v1/products/{id}` - 获取单个产品
- `POST /api/v1/products` - 创建产品
- `PUT /api/v1/products/{id}` - 更新产品
- `DELETE /api/v1/products/{id}` - 删除产品

### 统计
- `GET /api/v1/stats` - 数据统计（用户数/订单数/总金额/产品数）

## 使用示例

### 创建用户
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "email": "zhangsan@example.com"}'
```

### 创建产品
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{"name": "产品A", "price": 99.9, "stock": 100}'
```

### 创建订单
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{"order_no": "A001", "user_id": 1, "amount": 199.9}'
```

### 查询统计
```bash
curl "http://localhost:8000/api/v1/stats"
```

## 环境变量

- `DATABASE_URL` - 数据库连接地址，默认 `sqlite+aiosqlite:///./fastservice.db`

## License

MIT
