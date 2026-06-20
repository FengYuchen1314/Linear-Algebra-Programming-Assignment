import MathJaxDisplay from './MathJax';
import { IconSteps } from './ui/Icons';

export default function StepBlock({ steps }) {
  if (!steps?.length) return null;
  return (
    <div className="steps-section">
      <div className="steps-section-header">
        <IconSteps />
        <h3>计算步骤</h3>
      </div>
      <div className="steps-list">
        {steps.map((step, i) => (
          <div key={i} className="step-block">
            <span className="step-number">{i + 1}</span>
            <div className="step-body">
              <h4>{step.title}</h4>
              {step.latex ? (
                <div className="latex-block">
                  <MathJaxDisplay tex={step.latex} />
                </div>
              ) : (
                step.content && <p>{step.content}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
