export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  loading,
  className = '',
  ...props
}) {
  const cls = [
    'btn',
    `btn--${variant}`,
    size === 'sm' ? 'btn--sm' : '',
    loading ? 'btn--loading' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button type="button" className={cls} disabled={loading || props.disabled} {...props}>
      {loading ? <span className="btn-spinner" aria-hidden /> : icon && <span className="btn-icon">{icon}</span>}
      <span>{loading ? '计算中…' : children}</span>
    </button>
  );
}
