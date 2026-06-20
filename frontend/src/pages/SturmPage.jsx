import { useState } from 'react';
import { api } from '../api/client';
import PolynomialSourceSelector from '../components/PolynomialSourceSelector';
import PolynomialPreview from '../components/PolynomialPreview';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import { intervalToLatex, rootApproxLatex } from '../utils/latex';

export default function SturmPage() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompute = async () => {
    if (!selected) return;
    setLoading(true);
    setResult(null);
    const body = {
      source: selected.source,
      polynomial_id: selected.polynomial_id,
      requirement: selected.requirement,
    };
    const resp = await api.computeSturm(body);
    setResult(resp);
    setLoading(false);
  };

  const r = result?.result;

  return (
    <div className="page">
      <h2>Sturm 序列与求根</h2>
      <PolynomialSourceSelector onSelect={setSelected} selected={selected} />
      <button className="compute-btn" onClick={handleCompute} disabled={!selected || loading}>
        {loading ? '计算中...' : '开始 Sturm 分析'}
      </button>

      {result && (
        <div className="results">
          <ErrorBlock errors={result.errors} />
          <WarningBlock warnings={result.warnings} />
          {result.success && r && (
            <>
              <ResultBlock title="当前多项式">
                <PolynomialPreview expr={r.polynomial} label="f(x)" />
                <PolynomialPreview expr={r.derivative} label="f'(x)" />
                <PolynomialPreview expr={r.gcd_f_fprime} label={"\\gcd(f,f')"} />
                <MathLine tex={r.has_multiple_roots ? "\\gcd(f,f') \\neq 1" : "\\gcd(f,f') = 1"} />
                {r.squarefree_polynomial && (
                  <PolynomialPreview expr={r.squarefree_polynomial} label={'f_{\\mathrm{sf}}(x)'} />
                )}
              </ResultBlock>

              <ResultBlock title="Sturm 序列">
                {r.sturm_sequence_latex?.map((l, i) => (
                  <MathLine key={i} tex={`g_{${i}}(x)=${l}`} />
                ))}
              </ResultBlock>

              <ResultBlock title="根的上下界">
                <MathLine tex={`L=${r.root_bounds?.L},\\quad R=${r.root_bounds?.R}`} />
                <MathLine tex={intervalToLatex(r.root_bounds?.L, r.root_bounds?.R)} />
              </ResultBlock>

              <ResultBlock title="实根隔离区间">
                {r.isolated_intervals?.map((interval, i) => (
                  <MathLine key={i} tex={intervalToLatex(interval[0], interval[1])} />
                ))}
              </ResultBlock>

              <ResultBlock title="近似根">
                {r.approx_roots?.map((root, i) => (
                  <MathLine key={i} tex={rootApproxLatex(root)} />
                ))}
              </ResultBlock>

              <StepBlock steps={result.steps} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
