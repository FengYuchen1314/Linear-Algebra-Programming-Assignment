export default function ErrorBlock({ errors }) {
  if (!errors?.length) return null;
  return (
    <div className="error-block">
      {errors.map((e, i) => (
        <p key={i}>{e}</p>
      ))}
    </div>
  );
}

export function WarningBlock({ warnings }) {
  if (!warnings?.length) return null;
  return (
    <div className="warning-block">
      {warnings.map((w, i) => (
        <p key={i}>{w}</p>
      ))}
    </div>
  );
}
