import {
  DisplayPrecisionProvider,
  useDisplayPrecision,
} from './context/DisplayPrecisionContext';
import FeatureNav from './components/ui/FeatureNav';
import AnimatedRoutes from './components/ui/AnimatedRoutes';
import {
  IconSturm,
  IconMatrix,
  IconDecompose,
  IconJordan,
  IconLambda,
} from './components/ui/Icons';

const navItems = [
  { path: '/', label: 'Sturm 序列', Icon: IconSturm },
  { path: '/matrix-properties', label: '矩阵性质', Icon: IconMatrix },
  { path: '/decomposition', label: '矩阵分解', Icon: IconDecompose },
  { path: '/jordan', label: 'Jordan 标准型', Icon: IconJordan },
  { path: '/lambda-smith', label: 'λ-矩阵法', Icon: IconLambda },
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

function AppToolbar() {
  return (
    <header className="app-toolbar">
      <div className="app-toolbar__brand glass-pill">
        <div className="app-toolbar__logo">LA</div>
        <div>
          <span className="app-toolbar__title">Linear Algebra</span>
          <p className="app-toolbar__subtitle text-muted">fyc编程作业</p>
        </div>
      </div>

      <FeatureNav items={navItems} />

      <div className="app-toolbar__utility glass-pill">
        <DisplayPrecisionControl />
      </div>
    </header>
  );
}

export default function App() {
  return (
    <DisplayPrecisionProvider>
      <div className="app">
        <div className="app-shell">
          <AppToolbar />
          <AnimatedRoutes />
        </div>
      </div>
    </DisplayPrecisionProvider>
  );
}
