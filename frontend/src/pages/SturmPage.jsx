import { useState } from 'react';
import { api } from '../api/client';
import PolynomialSourceSelector from '../components/PolynomialSourceSelector';
import PolynomialPreview from '../components/PolynomialPreview';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import PageLayout, { ActionPanel, ResultsSection, WorkflowSection } from '../components/ui/PageLayout';
import Button from '../components/ui/Button';
import { IconCompute } from '../components/ui/Icons';
import ApproxRootsPanel from '../components/ApproxRootsPanel';
import IsolatedIntervalsPanel from '../components/IsolatedIntervalsPanel';
import { intervalToLatex } from '../utils/latex';

export default function SturmPage() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [precision, setPrecision] = useState('0.01');

  const runAnalysis = async (selection) => {
    const item = selection ?? selected;
    if (!item) return;
    const eps = Number(precision);
    if (!Number.isFinite(eps) || eps <= 0) return;
    setSelected(item);
    setLoading(true);
    setResult(null);
    const body = {
      source: item.source,
      polynomial_id: item.polynomial_id,
      requirement: item.requirement,
      precision: eps,
    };
    const resp = await api.computeSturm(body);
    setResult(resp);
    setLoading(false);
  };

  const epsValid = Number.isFinite(Number(precision)) && Number(precision) > 0;
  const r = result?.result;

  return (
    <PageLayout
      title="Sturm 序列与求根"
      description="构造 Sturm 序列，隔离实根区间并用二分法求近似根。"
    >
      <WorkflowSection>
        <PolynomialSourceSelector
          onSelect={setSelected}
          onConfirmAndAnalyze={runAnalysis}
          selected={selected}
        />

        <ActionPanel>
          <div className="field-group precision-control">
            <label htmlFor="sturm-precision">求根精度 ε</label>
            <input
              id="sturm-precision"
              className="field-input"
              type="number"
              min="1e-12"
              step="any"
              value={precision}
              onChange={(e) => setPrecision(e.target.value)}
            />
            {!epsValid && precision !== '' && (
              <span className="error-msg">须为正数</span>
            )}
          </div>
          <Button
            icon={<IconCompute />}
            loading={loading}
            onClick={() => runAnalysis()}
            disabled={!selected || !epsValid}
          >
            开始 Sturm 分析
          </Button>
        </ActionPanel>
      </WorkflowSection>

      {result && (
        <ResultsSection>
          <ErrorBlock errors={result.errors} />
          <WarningBlock warnings={result.warnings} />
          {result.success && r && (
            <>
              <ResultBlock title="当前多项式">
                <PolynomialPreview expr={r.polynomial} label="f(x)" />
                <PolynomialPreview expr={r.derivative} label="f'(x)" />
                <PolynomialPreview expr={r.gcd_f_fprime} label={"\\gcd(f,f')"} />
                {r.has_multiple_roots && (
                  <MathLine tex={"\\gcd(f,f') \\neq 1"} />
                )}
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
                <IsolatedIntervalsPanel intervals={r.isolated_intervals} />
              </ResultBlock>

              <ResultBlock title="近似根">
                <ApproxRootsPanel roots={r.approx_roots} precision={r.precision ?? precision} />
              </ResultBlock>

              <StepBlock steps={result.steps} />
            </>
          )}
        </ResultsSection>
      )}
    </PageLayout>
  );
}
