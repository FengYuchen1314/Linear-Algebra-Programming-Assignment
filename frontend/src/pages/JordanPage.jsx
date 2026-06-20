import { useState } from 'react';
import { api } from '../api/client';
import MatrixSourceSelector, { MatrixPreview } from '../components/MatrixSourceSelector';
import PolynomialPreview from '../components/PolynomialPreview';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import PageLayout, { ActionPanel, ResultsSection, WorkflowSection } from '../components/ui/PageLayout';
import Button from '../components/ui/Button';
import { IconCompute } from '../components/ui/Icons';
import { eigenvalueLineLatex, valueToLatex } from '../utils/latex';
import { displayEigenvalueLatex } from '../utils/displayPrecision';

export default function JordanPage() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runAnalysis = async (selection) => {
    const item = selection ?? selected;
    if (!item) return;
    setSelected(item);
    setLoading(true);
    setResult(null);
    try {
      const resp = await api.computeJordan({
        source: item.source,
        matrix_id: item.matrix_id,
        requirement: item.requirement,
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
    <PageLayout
      title="Jordan 标准型"
      description="基于幂零矩阵法求 Jordan 块结构，并构造变换矩阵 P。"
    >
      <WorkflowSection>
        <MatrixSourceSelector
          onSelect={setSelected}
          onConfirmAndAnalyze={runAnalysis}
          selected={selected}
          squareOnly
        />

        <ActionPanel>
          <Button
            icon={<IconCompute />}
            loading={loading}
            onClick={() => runAnalysis()}
            disabled={!selected}
          >
            计算 Jordan 标准型
          </Button>
        </ActionPanel>
      </WorkflowSection>

      {result && (
        <ResultsSection>
          <ErrorBlock errors={result.errors} />
          <WarningBlock warnings={result.warnings} />
          {result.success && r && (
            <>
              <ResultBlock title="当前矩阵">
                <MatrixPreview matrix={result.matrix} label="A" />
              </ResultBlock>
              <ResultBlock title="特征值分析">
                <PolynomialPreview
                  expr={r.characteristic_polynomial}
                  latex={r.characteristic_polynomial_latex}
                  label={'\\det(\\lambda I - A)'}
                />
                {r.eigenvalues?.map((ev, i) => (
                  <MathLine key={i} tex={`${eigenvalueLineLatex(ev)},\\ t=${ev.nilpotent_index}`} />
                ))}
              </ResultBlock>
              <ResultBlock title="幂零矩阵分析">
                {Object.entries(r.nilpotent_tables || {}).map(([lam, data]) => (
                  <div key={lam} className="nilpotent-section">
                    <MathLine tex={`\\lambda = ${displayEigenvalueLatex({ eigenvalue: lam, eigenvalue_latex: data.eigenvalue_latex })}`} />
                    <MatrixPreview matrix={data.B_matrix} label={'B = A - \\lambda I'} />
                    <div className="data-table-wrap">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th><MathLine inline tex={'k'} /></th>
                            <th><MathLine inline tex={'\\dim\\ker(B^{k})'} /></th>
                            <th><MathLine inline tex={'d_k - d_{k-1}'} /></th>
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
                  </div>
                ))}
              </ResultBlock>
              <ResultBlock title="Jordan 标准型">
                <MathLine tex={'\\text{约定：上 Jordan 块}'} />
                <MatrixPreview matrix={r.P} label="P" />
                <MatrixPreview matrix={r.J} label="J" />
                <MathLine tex={r.verification_exact
                  ? 'P^{-1}AP = J \\quad (\\text{精确验证})'
                  : valueToLatex('\\text{验证误差}', r.verification_error)} />
              </ResultBlock>
              <StepBlock steps={result.steps} />
            </>
          )}
        </ResultsSection>
      )}
    </PageLayout>
  );
}
