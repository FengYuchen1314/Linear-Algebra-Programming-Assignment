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
