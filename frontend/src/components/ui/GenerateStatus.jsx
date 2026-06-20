export default function GenerateStatus({ loading, error, entityLabel = '对象' }) {
  if (loading) {
    return (
      <div className="status-banner status-banner--info" role="status" aria-live="polite">
        <span className="status-banner__spinner" aria-hidden />
        <div className="status-banner__text">
          <p className="text-h4">正在调用 DeepSeek 生成{entityLabel}…</p>
          <p className="text-muted">根据你的描述构造中，通常需要 5–15 秒，请稍候</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-banner status-banner--error" role="alert">
        <p className="text-h4">生成失败</p>
        <p className="text-body">{error}</p>
      </div>
    );
  }

  return null;
}
