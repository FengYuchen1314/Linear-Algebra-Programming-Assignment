# 线性代数编程作业

基于 Python + FastAPI 与 React 的线性代数计算 Web 应用，提供 Sturm 序列求根、矩阵性质分析、矩阵分解、Jordan 标准型与 λ-矩阵法等模块。通过 Docker Compose 一键构建部署。

## 功能模块

| 模块 | 说明 |
|------|------|
| Sturm 序列与求根 | 多项式库选取或 DeepSeek AI 生成，Sturm 序列隔离实根并数值求解 |
| 矩阵基本性质 | 秩、行列式、特征值、逆矩阵等 |
| 矩阵分解 | 满秩分解、LU / PLU、LDU、SVD |
| Jordan 标准型 | 幂零矩阵法求 Jordan 形 |
| λ-矩阵法 | Smith 标准型、初等因子 |

## 技术栈

- **后端**：FastAPI、SymPy、NumPy、SciPy
- **前端**：React、Vite、Framer Motion、MathJax
- **部署**：Docker Compose（Nginx 反向代理 + 前后端容器）

## 项目结构

```
.
├── backend/              # FastAPI 后端
│   ├── app/              # 路由、服务、数据
│   ├── Dockerfile
│   ├── pip.conf          # pip 清华镜像（构建时使用）
│   └── requirements.txt
├── frontend/             # React 前端
│   ├── src/
│   ├── Dockerfile
│   └── .npmrc            # npm 国内镜像
├── docker-compose.yml
├── .env                  # 部署配置（随仓库提交，部署前填入 API Key）
└── scripts/check-env.sh  # 检查 .env 是否已配置
```

## 环境要求

- Docker 20.10+
- Docker Compose v2+

## 部署

### 1. 获取代码

```bash
git clone <repo-url> Linear-Algebra-Programming-Assignment
cd Linear-Algebra-Programming-Assignment
```

### 2. 配置环境变量

编辑根目录 `.env`：

```env
APP_PORT=35001
DEEPSEEK_API_KEY=your_api_key_here
PIP_INDEX=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `APP_PORT` | 否 | 前端对外端口，默认 `35001` |
| `DEEPSEEK_API_KEY` | 是* | DeepSeek API Key，AI 生成矩阵/多项式时需要 |
| `PIP_INDEX` | 否 | 后端 Docker 构建时的 PyPI 镜像，默认清华源 |

\* 不使用 AI 生成功能时可保留占位符，但相关功能将不可用。

可选：启动前运行检查脚本：

```bash
sh scripts/check-env.sh
```

`docker-compose.yml` 会依次读取根目录 `.env` 与 `backend/.env`（后者可选）。

### 3. 构建并启动

```bash
docker compose up --build -d
```

首次构建会拉取基础镜像并安装依赖，国内环境已通过镜像加速。

### 4. 访问

浏览器打开：

```
http://<服务器IP>:35001
```

前端 Nginx 将 `/api/` 请求代理至后端容器，后端不直接对外暴露。

健康检查：

```
http://<服务器IP>:35001/api/health
```

### 常用命令

```bash
# 查看日志
docker compose logs -f

# 仅查看某一服务
docker compose logs -f backend
docker compose logs -f frontend

# 重新构建并启动
docker compose up --build -d

# 停止并移除容器
docker compose down

# 停止并移除容器、镜像、卷
docker compose down --rmi local
```

## 镜像源

构建阶段默认使用国内镜像加速依赖下载：

| 类型 | 地址 | 说明 |
|------|------|------|
| PyPI | `https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple` | 后端 pip 安装，由 `PIP_INDEX` 控制 |
| npm | `https://registry.npmmirror.com` | 前端 npm 安装，见 `frontend/.npmrc` |

> 清华镜像站不提供 npm registry，前端使用 npmmirror。

## 注意事项

- 不支持手动输入多项式或矩阵，需从内置库或 AI 生成选取
- 不支持复系数多项式或复数矩阵输入
- DeepSeek 生成功能需配置有效的 `DEEPSEEK_API_KEY`
- `.env` 已纳入版本控制，**请勿将真实 API Key 提交到公开仓库**

## License

见 [LICENSE](LICENSE)。
