export default function Button({
  children,
  variant = 'filled',
  size = 'md',
  icon,
  loading,
  className = '',
  ...props
}) {
  const resolved = variant === 'primary' ? 'filled'
    : variant === 'secondary' ? 'tonal'
      : variant;

  const cls = [
    'md-button',
    `md-button--${resolved}`,
    size === 'sm' ? 'md-button--sm' : '',
    'md-state-layer',
    loading ? 'md-button--loading' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button type="button" className={cls} disabled={loading || props.disabled} {...props}>
      {loading ? <span className="md-button__spinner" aria-hidden /> : icon && (
        <span className="md-button__icon" aria-hidden>{icon}</span>
      )}
      <span className="md-button__label">{loading ? '计算中…' : children}</span>
    </button>
  );
}
