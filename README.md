# 线性代数编程作业

Python + FastAPI 后端与 React 前端，涵盖 Sturm 序列求根、矩阵性质、分解、Jordan 标准型与 λ-矩阵法。

## 环境要求

- Python 3.10+
- Node.js 18+

## 后端启动

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # 填入 DEEPSEEK_API_KEY
uvicorn main:app --reload --port 8000
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:5173

## Docker Compose 部署

使用本地源码构建镜像，不会从 GitHub 拉取代码。默认对外端口 **35001**。

### 首次配置

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
docker compose up --build -d
```

访问：**http://<服务器IP>:35001**

### 复制到服务器

`.env` 被 git 忽略，**不会随仓库提交**，手动拷贝项目时必须带上：

```bash
# 示例：同步代码（保留根目录 .env）
rsync -av --exclude node_modules --exclude backend/venv --exclude frontend/dist \
  ./ user@server:/path/to/Linear-Algebra-Programming-Assignment/

# 若 .env 尚未在服务器上，单独拷贝一次
scp .env user@server:/path/to/Linear-Algebra-Programming-Assignment/.env
```

服务器上启动：

```bash
cd /path/to/Linear-Algebra-Programming-Assignment
docker compose up --build -d
```

`docker-compose.yml` 会依次读取根目录 `.env` 与 `backend/.env`（后者可选，用于本地开发遗留配置）。**至少保证根目录 `.env` 中有 `DEEPSEEK_API_KEY`**。

根目录 `.env` 示例：

```env
APP_PORT=35001
DEEPSEEK_API_KEY=sk-xxxxxxxx
```

常用命令：

```bash
docker compose logs -f
docker compose down
docker compose up --build
```

## API 文档

后端启动后访问 http://localhost:8000/docs

## 功能模块

1. **Sturm 序列与求根** — 多项式库 / DeepSeek 生成
2. **矩阵基本性质** — 秩、行列式、特征值、逆矩阵等
3. **矩阵分解** — 满秩、LU/PLU、LDU、SVD
4. **Jordan 标准型** — 幂零矩阵法
5. **λ-矩阵法** — Smith 标准型、初等因子

## 注意事项

- 不支持手动输入多项式或矩阵
- 不支持复系数多项式或复数矩阵输入
- DeepSeek 生成功能需要配置 `DEEPSEEK_API_KEY` 环境变量
