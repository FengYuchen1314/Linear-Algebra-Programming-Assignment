# 线性代数编程作业

Python + FastAPI 后端与 React 前端，涵盖 Sturm 序列求根、矩阵性质、分解、Jordan 标准型与 λ-矩阵法。

## 环境要求

- Python 3.10+
- Node.js 18+

## 镜像源

项目默认使用国内镜像加速依赖下载：

| 类型 | 地址 | 说明 |
|------|------|------|
| PyPI | `https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple` | 清华镜像，后端 pip / Docker 构建 |
| npm | `https://registry.npmmirror.com` | 清华不提供 npm registry，前端使用 npmmirror |
| Node.js 二进制 | `https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/` | 仅在使用 nvm/fnm 等安装 Node 时适用 |

本地 pip 配置见 `backend/pip.conf`，前端 npm 配置见 `frontend/.npmrc`。Docker 构建通过 `.env` 中的 `PIP_INDEX` 传入后端镜像地址。

## 后端启动

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
PIP_CONFIG_FILE=./pip.conf pip install -r requirements.txt
# 编辑 backend/.env 或根目录 .env，填入 DEEPSEEK_API_KEY
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
# 编辑根目录 .env，填入 DEEPSEEK_API_KEY
docker compose up --build -d
```

访问：**http://<服务器IP>:35001**

### 复制到服务器

```bash
git clone <repo-url> /path/to/Linear-Algebra-Programming-Assignment
cd /path/to/Linear-Algebra-Programming-Assignment
# 编辑 .env，填入 DEEPSEEK_API_KEY
docker compose up --build -d
```

`docker-compose.yml` 会依次读取根目录 `.env` 与 `backend/.env`（后者可选，用于本地开发遗留配置）。**至少保证根目录 `.env` 中有 `DEEPSEEK_API_KEY`**。

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
