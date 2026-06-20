import { Routes, Route, NavLink } from 'react-router-dom';
import SturmPage from './pages/SturmPage';
import MatrixPropertiesPage from './pages/MatrixPropertiesPage';
import DecompositionPage from './pages/DecompositionPage';
import JordanPage from './pages/JordanPage';
import LambdaSmithPage from './pages/LambdaSmithPage';

const navItems = [
  { path: '/', label: 'Sturm 序列与求根' },
  { path: '/matrix-properties', label: '矩阵基本性质' },
  { path: '/decomposition', label: '矩阵分解' },
  { path: '/jordan', label: 'Jordan 标准型' },
  { path: '/lambda-smith', label: 'λ-矩阵法' },
];

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>线性代数编程作业</h1>
        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<SturmPage />} />
          <Route path="/matrix-properties" element={<MatrixPropertiesPage />} />
          <Route path="/decomposition" element={<DecompositionPage />} />
          <Route path="/jordan" element={<JordanPage />} />
          <Route path="/lambda-smith" element={<LambdaSmithPage />} />
        </Routes>
      </main>
    </div>
  );
}
