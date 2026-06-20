import { useState } from 'react';
import { api } from '../api/client';
import MatrixSourceSelector, { MatrixPreview } from '../components/MatrixSourceSelector';
import PolynomialPreview from '../components/PolynomialPreview';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import { eigenvalueLineLatex, valueToLatex } from '../utils/latex';

export default function JordanPage() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompute = async () => {
    if (!selected) return;
    setLoading(true);
    setResult(null);
    try {
      const resp = await api.computeJordan({
        source: selected.source,
        matrix_id: selected.matrix_id,
        requirement: selected.requirement,
      });
      setResult(resp);
    } catch (e) {
      setResult({ success: false, errors: [e.message] });
    } finally {
      setLoading(false);
    }
  };

  const r = result?.result;

  return (
    <div className="page">
      <h2>Jordan 标准型（幂零矩阵法）</h2>
      <MatrixSourceSelector onSelect={setSelected} selected={selected} squareOnly />
      <button className="compute-btn" onClick={handleCompute} disabled={!selected || loading}>
        {loading ? '计算中...' : '计算 Jordan 标准型'}
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
              <ResultBlock title="特征值分析">
                <PolynomialPreview
                  expr={r.characteristic_polynomial_latex || r.characteristic_polynomial}
                  label={'\\det(\\lambda I - A)'}
                />
                {r.eigenvalues?.map((ev, i) => (
                  <MathLine key={i} tex={`${eigenvalueLineLatex(ev)},\\ t=${ev.nilpotent_index}`} />
                ))}
              </ResultBlock>
              <ResultBlock title="dim ker(B^k) 表格">
                {Object.entries(r.nilpotent_tables || {}).map(([lam, data]) => (
                  <div key={lam}>
                    <MathLine tex={`\\lambda = ${data.eigenvalue_latex || lam}`} />
                    <MatrixPreview matrix={data.B_matrix} label={`B=A-\\lambda I`} />
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th><MathLine inline tex={'k'} /></th>
                          <th><MathLine inline tex={'\\dim\\ker(B^{k})'} /></th>
                          <th><MathLine inline tex={'d_{k} - d_{k-1}'} /></th>
                          <th>Jordan 块信息</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.table?.map((row, i) => (
                          <tr key={i}>
                            <td>{row.k}</td>
                            <td>{row.dim_ker_Bk}</td>
                            <td>{row.dk_diff}</td>
                            <td>{row.jordan_block_info}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </ResultBlock>
              <ResultBlock title="Jordan 标准型">
                <p>约定: {r.convention}</p>
                <MatrixPreview matrix={r.P} label="P" />
                <MatrixPreview matrix={r.J} label="J" />
                <MathLine tex={r.verification_exact
                  ? 'P^{-1}AP = J \\text{（精确验证）}'
                  : valueToLatex('\\text{验证误差}', r.verification_error)} />
              </ResultBlock>
              <StepBlock steps={result.steps} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
