import { useState } from 'react';
import { api } from '../api/client';
import MatrixSourceSelector, { MatrixPreview } from '../components/MatrixSourceSelector';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import { valueToLatex, numberToLatex } from '../utils/latex';

const DECOMP_TYPES = [
  { key: 'full-rank', label: '满秩分解', fn: api.computeFullRank },
  { key: 'lu', label: 'LU / PLU 分解', fn: api.computeLU },
  { key: 'ldu', label: 'LDU 分解', fn: api.computeLDU },
  { key: 'svd', label: 'SVD 分解', fn: api.computeSVD },
];

export default function DecompositionPage() {
  const [selected, setSelected] = useState(null);
  const [decompType, setDecompType] = useState('full-rank');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompute = async () => {
    if (!selected) return;
    setLoading(true);
    setResult(null);
    const item = DECOMP_TYPES.find((d) => d.key === decompType);
    const body = {
      source: selected.source,
      matrix_id: selected.matrix_id,
      requirement: selected.requirement,
    };
    const resp = await item.fn(body);
    setResult(resp);
    setLoading(false);
  };

  const r = result?.result;

  return (
    <div className="page">
      <h2>矩阵的各种分解</h2>
      <MatrixSourceSelector onSelect={setSelected} selected={selected} />

      <div className="decomp-selector">
        <label>分解类型：</label>
        <select value={decompType} onChange={(e) => setDecompType(e.target.value)}>
          {DECOMP_TYPES.map((d) => (
            <option key={d.key} value={d.key}>{d.label}</option>
          ))}
        </select>
      </div>

      <button className="compute-btn" onClick={handleCompute} disabled={!selected || loading}>
        {loading ? '计算中...' : '开始分解'}
      </button>

      {result && (
        <div className="results">
          <ErrorBlock errors={result.errors} />
          <WarningBlock warnings={result.warnings} />
          {result.success && r && (
            <>
              <ResultBlock title="当前矩阵">
                <MatrixPreview matrix={result.matrix} label="A" />
              </ResultBlock>
              <ResultBlock title="分解结果">
                {r.rank != null && <MathLine tex={`\\mathrm{rank}(A)=${r.rank}`} />}
                {r.B && <MatrixPreview matrix={r.B} label="B" />}
                {r.C && <MatrixPreview matrix={r.C} label="C" />}
                {r.P && <MatrixPreview matrix={r.P} label="P" />}
                {r.L && <MatrixPreview matrix={r.L} label="L" />}
                {r.U && !r.Sigma && <MatrixPreview matrix={r.U} label="U" />}
                {r.D && <MatrixPreview matrix={r.D} label="D" />}
                {r.U1 && <MatrixPreview matrix={r.U1} label={'U_{1}'} />}
                {r.Sigma && <MatrixPreview matrix={r.U} label="U" />}
                {r.Sigma && <MatrixPreview matrix={r.Sigma} label={'\\Sigma'} />}
                {r.V_transpose && <MatrixPreview matrix={r.V_transpose} label={'V^{\\mathsf T}'} />}
                {r.singular_values && (
                  <MathLine tex={`\\sigma_i \\in \\{${r.singular_values.map((s) => numberToLatex(s)).join(',\\ ')}\\}`} />
                )}
                {r.verification_error != null && (
                  <MathLine tex={r.verification_exact
                    ? '\\text{验证：恒等（精确）}'
                    : valueToLatex('\\text{验证误差}', r.verification_error)} />
                )}
                {r.method === 'numeric' && <MathLine tex={'\\text{（数值方法）}'} />}
              </ResultBlock>
              <StepBlock steps={result.steps} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
