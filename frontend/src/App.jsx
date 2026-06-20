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
    <div className="field-inline display-precision-control">
      <label className="text-label" htmlFor="global-display-precision">显示精度</label>
      <input
        id="global-display-precision"
        className="input input--sm"
        type="number"
        min="1e-12"
        step="any"
        value={precision}
        onChange={(e) => setPrecision(e.target.value)}
        title="仅影响浮点近似值的显示；分数、根号等精确值不变"
      />
      {!valid && <span className="precision-hint text-muted">须为正数</span>}
    </div>
  );
}

function Sidebar() {
  return (
    <aside className="sidebar" aria-label="主导航">
      <div className="sidebar__brand">
        <div className="sidebar__logo">LA</div>
        <div>
          <h1 className="sidebar__title">Linear Algebra</h1>
          <p className="sidebar__tagline text-muted">符号计算工作台</p>
        </div>
      </div>
      <nav className="sidebar__nav" aria-label="页面导航">
        {navItems.map(({ path, label, desc, Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) => `sidebar__link${isActive ? ' is-active' : ''}`}
          >
            <span className="sidebar__link-icon" aria-hidden><Icon /></span>
            <span className="sidebar__link-text">
              <span className="sidebar__link-label">{label}</span>
              <span className="sidebar__link-desc">{desc}</span>
            </span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar__footer text-muted">SymPy · MathJax · React</div>
    </aside>
  );
}

function Topbar() {
  const location = useLocation();
  const current = navItems.find((item) => (
    item.path === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(item.path)
  ));

  return (
    <header className="topbar">
      <div className="topbar__leading">
        <h2 className="topbar__title">{current?.label}</h2>
      </div>
      <div className="topbar__trailing">
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
  return (
    <DisplayPrecisionProvider>
      <div className="app">
        <Sidebar />
        <div className="app-content">
          <Topbar />
          <AppRoutes />
        </div>
      </div>
    </DisplayPrecisionProvider>
  );
}
