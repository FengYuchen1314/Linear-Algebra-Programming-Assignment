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
import { numberToLatex, pickLatex, subscriptLatex } from '../utils/latex';

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
    <PageLayout
      title="λ-矩阵法与 Smith 标准型"
      description="对 λI−A 做 Smith 分解，求不变因子、初等因子与 Jordan 块。"
    >
      <MatrixSourceSelector onSelect={setSelected} selected={selected} squareOnly />

      <ActionPanel>
        <Button
          icon={<IconCompute />}
          loading={loading}
          onClick={handleCompute}
          disabled={!selected}
        >
          计算 Smith 标准型
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
              <ResultBlock title="特征矩阵 λI − A">
                <MatrixPreview matrix={r.lambda_I_minus_A} label={'\\lambda I - A'} />
                <PolynomialPreview
                  expr={r.characteristic_polynomial}
                  latex={r.characteristic_polynomial_latex}
                  label={'\\det(\\lambda I - A)'}
                />
                <PolynomialPreview
                  expr={r.minimal_polynomial}
                  latex={r.minimal_polynomial_latex}
                  label={'m_A(\\lambda)'}
                />
              </ResultBlock>
              <ResultBlock title="Smith 标准型">
                <MatrixPreview matrix={r.smith_form} label="S" />
              </ResultBlock>
              <ResultBlock title="行列式因子">
                {Object.entries(r.determinant_factors || {}).map(([k, v]) => (
                  <MathLine
                    key={k}
                    tex={`${subscriptLatex(k)}(\\lambda)=${pickLatex(r.determinant_factors_latex?.[k], v)}`}
                  />
                ))}
              </ResultBlock>
              <ResultBlock title="不变因子">
                {r.invariant_factors?.map((f, i) => (
                  <MathLine
                    key={i}
                    tex={`d_{${i + 1}}(\\lambda)=${pickLatex(r.invariant_factors_latex?.[i], f)}`}
                  />
                ))}
              </ResultBlock>
              <ResultBlock title="初等因子组">
                {r.elementary_divisors?.map((e, i) => (
                  <MathLine key={i} tex={pickLatex(e.factor_latex, e.factor)} />
                ))}
              </ResultBlock>
              <ResultBlock title="Jordan 块（由初等因子）">
                {r.jordan_blocks_from_elementary?.map((b, i) => (
                  <MathLine
                    key={i}
                    tex={`${pickLatex(b.elementary_divisor_latex, b.elementary_divisor)} \\rightarrow J_{${b.block_size}}(${numberToLatex(b.eigenvalue)})`}
                  />
                ))}
                <MathLine tex={r.is_diagonalizable ? '\\text{可对角化：是}' : '\\text{可对角化：否}'} />
                <MatrixPreview matrix={r.jordan_form_J} label="J" />
              </ResultBlock>
              <StepBlock steps={result.steps} />
            </>
          )}
        </ResultsSection>
      )}
    </PageLayout>
  );
}
