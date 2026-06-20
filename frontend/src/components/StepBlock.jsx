import MathJaxDisplay from './MathJax';
import { IconSteps } from './ui/Icons';

export default function StepBlock({ steps }) {
  if (!steps?.length) return null;
  return (
    <section className="card card--muted steps-section">
      <header className="steps-section-header">
        <IconSteps aria-hidden />
        <h3 className="text-h4">计算步骤</h3>
      </header>
      <ol className="steps-list">
        {steps.map((step, i) => (
          <li key={i} className="step-block">
            <span className="step-number" aria-hidden>{i + 1}</span>
            <div className="step-body">
              <h4 className="text-h4">{step.title}</h4>
              {step.latex ? (
                <div className="latex-block">
                  <MathJaxDisplay tex={step.latex} />
                </div>
              ) : (
                step.content && <p className="text-body">{step.content}</p>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
