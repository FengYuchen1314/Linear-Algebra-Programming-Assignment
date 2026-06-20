import MathJaxDisplay from './MathJax';
import { IconSteps } from './ui/Icons';

export default function StepBlock({ steps }) {
  if (!steps?.length) return null;
  return (
    <section className="md-card md-card--filled steps-section">
      <header className="steps-section-header">
        <IconSteps aria-hidden />
        <h3 className="md-title-medium">计算步骤</h3>
      </header>
      <ol className="steps-list">
        {steps.map((step, i) => (
          <li key={i} className="step-block">
            <span className="step-number md-label-medium" aria-hidden>{i + 1}</span>
            <div className="step-body">
              <h4 className="md-title-small">{step.title}</h4>
              {step.latex ? (
                <div className="latex-block">
                  <MathJaxDisplay tex={step.latex} />
                </div>
              ) : (
                step.content && <p className="md-body-medium">{step.content}</p>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
