import { useState } from 'react';
import { api } from '../api/client';
import MatrixSourceSelector, { MatrixPreview } from '../components/MatrixSourceSelector';
import PolynomialPreview from '../components/PolynomialPreview';
import MathLine from '../components/MathLine';
import ResultBlock from '../components/ResultBlock';
import StepBlock from '../components/StepBlock';
import ErrorBlock, { WarningBlock } from '../components/ErrorBlock';
import PageLayout, { ActionPanel, ResultsSection } from '../components/ui/PageLayout';
import Button from '../components/ui/Button';
import { IconCompute } from '../components/ui/Icons';
import { eigenvalueLineLatex } from '../utils/latex';

export default function MatrixPropertiesPage() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompute = async () => {
    if (!selected) return;
    setLoading(true);
    setResult(null);
    const resp = await api.computeMatrixProperties({
      source: selected.source,
      matrix_id: selected.matrix_id,
      requirement: selected.requirement,
    });
    setResult(resp);
    setLoading(false);
  };

  const r = result?.result;

  return (
    <PageLayout
      title="矩阵基本性质"
      description="分析矩阵的秩、行列式、迹、可逆性、特征值与可对角化性。"
    >
      <MatrixSourceSelector onSelect={setSelected} selected={selected} />

      <ActionPanel>
        <Button
          icon={<IconCompute />}
          loading={loading}
          onClick={handleCompute}
          disabled={!selected}
        >
          分析矩阵性质
        </Button>
      </ActionPanel>

      {result && (
        <ResultsSection>
          <ErrorBlock errors={result.errors} />
          <WarningBlock warnings={result.warnings} />
          {result.success && r && (
            <>
              <ResultBlock title="当前矩阵">
                <MatrixPreview matrix={result.matrix} label="A" />
              </ResultBlock>

              <ResultBlock title="基本性质">
                <MathLine tex={`A \\in \\mathbb{R}^{${r.rows}\\times ${r.cols}},\\ \\mathrm{rank}(A)=${r.rank}`} />
                {r.is_square ? (
                  <>
                    <MathLine tex={`\\det(A)=${r.det_latex || r.det},\\ \\mathrm{tr}(A)=${r.trace_latex || r.trace}`} />
                    <MathLine tex={r.is_invertible ? 'A \\text{ 可逆}' : 'A \\text{ 不可逆}'} />
                    {r.inverse && <MatrixPreview matrix={r.inverse} label={'A^{-1}'} />}
                    <PolynomialPreview
                      expr={r.characteristic_polynomial_latex || r.characteristic_polynomial}
                      label={'\\det(\\lambda I - A)'}
                    />
                    <h4>特征值分析</h4>
                    {r.eigenvalues?.map((ev, i) => (
                      <MathLine key={i} tex={eigenvalueLineLatex(ev)} />
                    ))}
                    <MathLine tex={r.is_diagonalizable ? '\\text{可对角化：是}' : '\\text{可对角化：否}'} />
                    <p>{r.diagonalizable_reason}</p>
                  </>
                ) : (
                  <>
                    <MathLine tex={r.has_left_inverse ? '\\exists\\, A_L:\\ A_L A = I' : '\\nexists\\, \\text{左逆}'} />
                    {r.left_inverse && <MatrixPreview matrix={r.left_inverse} label="A_L" />}
                    <MathLine tex={r.has_right_inverse ? '\\exists\\, A_R:\\ A A_R = I' : '\\nexists\\, \\text{右逆}'} />
                    {r.right_inverse && <MatrixPreview matrix={r.right_inverse} label="A_R" />}
                  </>
                )}
              </ResultBlock>
              <StepBlock steps={result.steps} />
            </>
          )}
        </ResultsSection>
      )}
    </PageLayout>
  );
}
