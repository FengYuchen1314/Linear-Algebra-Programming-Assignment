import MathJaxDisplay from './MathJax';

export default function StepBlock({ steps }) {
  if (!steps?.length) return null;
  return (
    <div className="steps-section">
      <h3>计算步骤</h3>
      {steps.map((step, i) => (
        <div key={i} className="step-block">
          <h4>{step.title}</h4>
          {step.latex ? (
            <div className="latex-block">
              <MathJaxDisplay tex={step.latex} />
            </div>
          ) : (
            step.content && <p>{step.content}</p>
          )}
        </div>
      ))}
    </div>
  );
}
