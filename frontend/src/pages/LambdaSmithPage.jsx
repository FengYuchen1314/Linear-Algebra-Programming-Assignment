import { useState } from 'react';
import { api } from '../api/client';
import MatrixSourceSelector, { MatrixPreview } from '../components/MatrixSourceSelector';
import PolynomialPreview from '../components/PolynomialPreview';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import { exprToLatex, numberToLatex } from '../utils/latex';

export default function LambdaSmithPage() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompute = async () => {
    if (!selected) return;
    setLoading(true);
    setResult(null);
    const resp = await api.computeLambdaSmith({
      source: selected.source,
      matrix_id: selected.matrix_id,
      requirement: selected.requirement,
    });
    setResult(resp);
    setLoading(false);
  };

  const r = result?.result;

  return (
    <div className="page">
      <h2>λ-矩阵法与 Smith 标准型</h2>
      <MatrixSourceSelector onSelect={setSelected} selected={selected} squareOnly />
      <button className="compute-btn" onClick={handleCompute} disabled={!selected || loading}>
        {loading ? '计算中...' : '计算 Smith 标准型'}
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
              <ResultBlock title="特征矩阵 λI-A">
                <PolynomialPreview expr={r.characteristic_polynomial} label={'\\det(\\lambda I - A)'} />
                <PolynomialPreview expr={r.minimal_polynomial} label={'m_A(\\lambda)'} />
              </ResultBlock>
              <ResultBlock title="Smith 标准型">
                <MatrixPreview matrix={r.smith_form} label="S" />
              </ResultBlock>
              <ResultBlock title="行列式因子">
                {Object.entries(r.determinant_factors || {}).map(([k, v]) => (
                  <MathLine key={k} tex={`${k}(\\lambda)=${exprToLatex(v)}`} />
                ))}
              </ResultBlock>
              <ResultBlock title="不变因子">
                {r.invariant_factors?.map((f, i) => (
                  <MathLine key={i} tex={`d_{${i + 1}}(\\lambda)=${exprToLatex(f)}`} />
                ))}
              </ResultBlock>
              <ResultBlock title="初等因子组">
                {r.elementary_divisors?.map((e, i) => (
                  <MathLine key={i} tex={exprToLatex(e.factor)} />
                ))}
              </ResultBlock>
              <ResultBlock title="Jordan 块（由初等因子）">
                {r.jordan_blocks_from_elementary?.map((b, i) => (
                  <MathLine
                    key={i}
                    tex={`${exprToLatex(b.elementary_divisor)} \\rightarrow J_{${b.block_size}}(${numberToLatex(b.eigenvalue)})`}
                  />
                ))}
                <MathLine tex={`\\text{可对角化：${r.is_diagonalizable ? '是' : '否'}}`} />
                <MatrixPreview matrix={r.jordan_form_J} label="J" />
              </ResultBlock>
              <StepBlock steps={result.steps} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
