import { IconAlert } from './ui/Icons';

export default function ErrorBlock({ errors }) {
  if (!errors?.length) return null;
  return (
    <div className="error-block alert--error">
      <span className="alert-icon"><IconAlert /></span>
      <div className="alert-content">
        {errors.map((e, i) => (
          <p key={i}>{e}</p>
        ))}
      </div>
    </div>
  );
}

export function WarningBlock({ warnings }) {
  if (!warnings?.length) return null;
  return (
    <div className="warning-block alert--warning">
      <span className="alert-icon"><IconAlert /></span>
      <div className="alert-content">
        {warnings.map((w, i) => (
          <p key={i}>{w}</p>
        ))}
      </div>
    </div>
  );
}
