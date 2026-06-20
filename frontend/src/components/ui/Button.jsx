export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  loading = false,
  disabled = false,
  className = '',
  type = 'button',
  ...props
}) {
  const resolved = variant === 'filled' ? 'primary'
    : variant === 'tonal' ? 'secondary'
      : variant === 'outlined' ? 'outline'
        : variant === 'text' ? 'ghost'
          : variant;

  const cls = [
    'btn',
    `btn--${resolved}`,
    size === 'sm' ? 'btn--sm' : '',
    loading ? 'btn--loading' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={cls}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? <span className="btn__spinner" aria-hidden /> : icon && (
        <span className="btn__icon" aria-hidden>{icon}</span>
      )}
      <span className="btn__label">{loading ? '计算中…' : children}</span>
    </button>
  );
}
