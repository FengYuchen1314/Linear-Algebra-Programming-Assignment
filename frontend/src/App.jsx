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
  { path: '/', label: 'Sturm 序列', desc: '多项式实根隔离与近似', Icon: IconSturm },
  { path: '/matrix-properties', label: '矩阵性质', desc: '秩、行列式、特征值', Icon: IconMatrix },
  { path: '/decomposition', label: '矩阵分解', desc: 'LU、LDU、SVD 等', Icon: IconDecompose },
  { path: '/jordan', label: 'Jordan 标准型', desc: '幂零矩阵法', Icon: IconJordan },
  { path: '/lambda-smith', label: 'λ-矩阵法', desc: 'Smith 标准型', Icon: IconLambda },
];

function DisplayPrecisionControl() {
  const { precision, setPrecision } = useDisplayPrecision();
  const valid = Number.isFinite(Number(precision)) && Number(precision) > 0;

  return (
    <div className="md-text-field md-text-field--compact display-precision-control">
      <label className="md-label-medium" htmlFor="global-display-precision">显示精度</label>
      <input
        id="global-display-precision"
        className="md-outlined-input"
        type="number"
        min="1e-12"
        step="any"
        value={precision}
        onChange={(e) => setPrecision(e.target.value)}
        title="仅影响浮点近似值的显示；分数、根号等精确值不变"
      />
      {!valid && <span className="precision-hint md-body-small">须为正数</span>}
    </div>
  );
}

function NavigationDrawer({ open, onClose }) {
  return (
    <>
      <div
        className={`md-scrim md-navigation-drawer__scrim ${open ? 'is-visible' : ''}`}
        onClick={onClose}
        aria-hidden={!open}
      />
      <aside className={`md-navigation-drawer ${open ? 'is-open' : ''}`} aria-label="导航抽屉">
        <div className="md-navigation-drawer__header">
          <span className="md-label-medium md-navigation-drawer__overline">Linear Algebra</span>
          <h1 className="md-headline-small">线性代数编程作业</h1>
          <p className="md-body-medium md-navigation-drawer__subtitle">符号计算与数值分析</p>
        </div>
        <nav className="md-navigation-drawer__content" aria-label="主导航">
          {navItems.map(({ path, label, desc, Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `md-navigation-drawer__item md-state-layer${isActive ? ' is-active' : ''}`
              }
              onClick={onClose}
            >
              <span className="md-navigation-drawer__item-icon" aria-hidden><Icon /></span>
              <span className="md-navigation-drawer__item-text">
                <span className="md-label-large">{label}</span>
                <span className="md-body-small md-navigation-drawer__item-desc">{desc}</span>
              </span>
            </NavLink>
          ))}
        </nav>
        <div className="md-navigation-drawer__footer md-body-small">SymPy · MathJax · React</div>
      </aside>
    </>
  );
}

function TopAppBar({ onMenuToggle, sidebarOpen }) {
  const location = useLocation();
  const current = navItems.find((item) => (
    item.path === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(item.path)
  ));

  return (
    <header className="md-top-app-bar">
      <div className="md-top-app-bar__leading">
        <button
          type="button"
          className="md-icon-button md-state-layer md-top-app-bar__menu"
          onClick={onMenuToggle}
          aria-label={sidebarOpen ? '关闭导航' : '打开导航'}
        >
          {sidebarOpen ? <IconClose /> : <IconMenu />}
        </button>
        <h2 className="md-title-medium md-top-app-bar__title">{current?.label}</h2>
      </div>
      <div className="md-top-app-bar__trailing">
        <DisplayPrecisionControl />
      </div>
    </header>
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

export default function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <DisplayPrecisionProvider>
      <div className="app">
        <NavigationDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
        <div className="app-content">
          <TopAppBar
            onMenuToggle={() => setDrawerOpen((v) => !v)}
            sidebarOpen={drawerOpen}
          />
          <AppRoutes />
        </div>
      </div>
    </DisplayPrecisionProvider>
  );
}
