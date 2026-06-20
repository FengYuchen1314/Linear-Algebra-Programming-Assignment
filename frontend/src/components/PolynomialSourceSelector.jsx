import { useState, useEffect } from 'react';
import { api } from '../api/client';
import PolynomialPreview from './PolynomialPreview';

export default function PolynomialSourceSelector({ onSelect, selected }) {
  const [mode, setMode] = useState('library');
  const [requirement, setRequirement] = useState('');
  const [generated, setGenerated] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await api.generatePolynomial(requirement);
      if (!resp.success) {
        setError(resp.errors?.[0] || '生成失败');
        setGenerated(null);
      } else {
        setGenerated(resp);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const confirmGenerated = () => {
    onSelect({
      source: 'generated',
      requirement,
      polynomial: generated.polynomial,
      description: generated.description,
    });
  };

  return (
    <div className="source-selector">
      <div className="mode-tabs">
        <button
          className={mode === 'library' ? 'tab active' : 'tab'}
          onClick={() => setMode('library')}
        >
          从多项式库选择
        </button>
        <button
          className={mode === 'generate' ? 'tab active' : 'tab'}
          onClick={() => setMode('generate')}
        >
          根据要求生成
        </button>
      </div>

      {mode === 'generate' && (
        <div className="generate-panel">
          <textarea
            placeholder="描述您需要的多项式，例如：给我一个三次无重根多项式"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={3}
          />
          <button onClick={handleGenerate} disabled={loading || !requirement.trim()}>
            {loading ? '生成中...' : '生成多项式'}
          </button>
          {error && <div className="error-msg">{error}</div>}
          {generated && (
            <div className="preview-box">
              <p><strong>生成结果：</strong></p>
              <PolynomialPreview expr={generated.polynomial} label="f(x)" />
              <p>{generated.description}</p>
              {generated.warnings?.map((w, i) => (
                <p key={i} className="warning-msg">{w}</p>
              ))}
              <button onClick={confirmGenerated}>确认使用此多项式</button>
            </div>
          )}
        </div>
      )}

      {mode === 'library' && (
        <PolynomialLibrarySelector onSelect={onSelect} selected={selected} />
      )}

      {selected && (
        <div className="selected-info">
          <strong>已选择：</strong>
          <PolynomialPreview expr={selected.polynomial || selected.item?.polynomial} label="f(x)" />
        </div>
      )}
    </div>
  );
}

function PolynomialLibrarySelector({ onSelect, selected }) {
  const [polynomials, setPolynomials] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPolynomialLibrary().then((resp) => {
      setPolynomials(resp.polynomials || []);
      setLoading(false);
    });
  }, []);

  if (loading) return <p>加载多项式库...</p>;

  return (
    <div className="library-grid">
      {polynomials.map((p) => (
        <div
          key={p.id}
          className={`library-card ${selected?.polynomial_id === p.id ? 'selected' : ''}`}
          onClick={() => onSelect({ source: 'library', polynomial_id: p.id, item: p, polynomial: p.polynomial })}
        >
          <h4>{p.name}</h4>
          <p className="meta">次数: {p.degree}</p>
          <PolynomialPreview expr={p.polynomial} label="f(x)" />
          <div className="tags">{p.tags?.map((t) => <span key={t} className="tag">{t}</span>)}</div>
          <p className="desc">{p.description}</p>
        </div>
      ))}
    </div>
  );
}
