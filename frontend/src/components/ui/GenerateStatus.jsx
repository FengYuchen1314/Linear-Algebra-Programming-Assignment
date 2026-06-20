export default function GenerateStatus({ loading, error, entityLabel = '对象' }) {
  if (loading) {
    return (
      <div className="generate-status generate-status--loading" role="status" aria-live="polite">
        <span className="generate-status__spinner" aria-hidden />
        <div className="generate-status__text">
          <p className="md-title-small">正在调用 DeepSeek 生成{entityLabel}…</p>
          <p className="md-body-small">根据你的描述构造中，通常需要 5–15 秒，请稍候</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="generate-status generate-status--error" role="alert">
        <p className="md-title-small">生成失败</p>
        <p className="md-body-medium">{error}</p>
      </div>
    );
  }

  return null;
}
