import { useState } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import SturmPage from './pages/SturmPage';
import MatrixPropertiesPage from './pages/MatrixPropertiesPage';
import DecompositionPage from './pages/DecompositionPage';
import JordanPage from './pages/JordanPage';
import LambdaSmithPage from './pages/LambdaSmithPage';
import {
  DisplayPrecisionProvider,
  useDisplayPrecision,
} from './context/DisplayPrecisionContext';
import {
  IconSturm,
  IconMatrix,
  IconDecompose,
  IconJordan,
  IconLambda,
  IconMenu,
  IconClose,
} from './components/ui/Icons';

const navItems = [
  {
    path: '/',
    label: 'Sturm 序列',
    desc: '多项式实根隔离与近似',
    Icon: IconSturm,
  },
  {
    path: '/matrix-properties',
    label: '矩阵性质',
    desc: '秩、行列式、特征值',
    Icon: IconMatrix,
  },
  {
    path: '/decomposition',
    label: '矩阵分解',
    desc: 'LU、LDU、SVD 等',
    Icon: IconDecompose,
  },
  {
    path: '/jordan',
    label: 'Jordan 标准型',
    desc: '幂零矩阵法',
    Icon: IconJordan,
  },
  {
    path: '/lambda-smith',
    label: 'λ-矩阵法',
    desc: 'Smith 标准型',
    Icon: IconLambda,
  },
];

function DisplayPrecisionControl() {
  const { precision, setPrecision } = useDisplayPrecision();
  const valid = Number.isFinite(Number(precision)) && Number(precision) > 0;

  return (
    <div className="display-precision-control">
      <label htmlFor="global-display-precision">显示精度</label>
      <input
        id="global-display-precision"
        type="number"
        min="1e-12"
        step="any"
        value={precision}
        onChange={(e) => setPrecision(e.target.value)}
        title="仅影响浮点近似值的显示；分数、根号等精确值不变"
      />
      {!valid && <span className="precision-hint">须为正数</span>}
    </div>
  );
}

function Sidebar({ open, onClose }) {
  return (
    <>
      <div
        className={`sidebar-backdrop ${open ? 'visible' : ''}`}
        onClick={onClose}
        aria-hidden={!open}
      />
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="sidebar-brand-badge">Linear Algebra</div>
          <h1>线性代数编程作业</h1>
          <p>符号计算与数值分析工具集</p>
        </div>
        <nav className="sidebar-nav" aria-label="主导航">
          <div className="sidebar-nav-label">功能模块</div>
          {navItems.map(({ path, label, desc, Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
              onClick={onClose}
            >
              <span className="nav-item-icon"><Icon /></span>
              <span className="nav-item-text">
                <span className="nav-item-label">{label}</span>
                <span className="nav-item-desc">{desc}</span>
              </span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">SymPy · MathJax · React</div>
      </aside>
    </>
  );
}

function AppRoutes() {
  useDisplayPrecision();

  return (
    <main className="app-main">
      <Routes>
        <Route path="/" element={<SturmPage />} />
        <Route path="/matrix-properties" element={<MatrixPropertiesPage />} />
        <Route path="/decomposition" element={<DecompositionPage />} />
        <Route path="/jordan" element={<JordanPage />} />
        <Route path="/lambda-smith" element={<LambdaSmithPage />} />
      </Routes>
    </main>
  );
}

function TopBar({ onMenuToggle, sidebarOpen }) {
  const location = useLocation();
  const current = navItems.find((item) => (
    item.path === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(item.path)
  ));

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          type="button"
          className="menu-toggle"
          onClick={onMenuToggle}
          aria-label={sidebarOpen ? '关闭菜单' : '打开菜单'}
        >
          {sidebarOpen ? <IconClose /> : <IconMenu />}
        </button>
        <span className="topbar-title">{current?.label}</span>
      </div>
      <DisplayPrecisionControl />
    </header>
  );
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <DisplayPrecisionProvider>
      <div className="app">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="app-content">
          <TopBar
            onMenuToggle={() => setSidebarOpen((v) => !v)}
            sidebarOpen={sidebarOpen}
          />
          <AppRoutes />
        </div>
      </div>
    </DisplayPrecisionProvider>
  );
}
