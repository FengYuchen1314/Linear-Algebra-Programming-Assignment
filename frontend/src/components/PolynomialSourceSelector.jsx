import { useState, useEffect, useMemo } from 'react';
import { api } from '../api/client';
import PolynomialPreview from './PolynomialPreview';
import { SelectedBanner } from './ResultBlock';
import Modal from './ui/Modal';
import Button from './ui/Button';

export default function PolynomialSourceSelector({ onSelect, selected }) {
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [generateOpen, setGenerateOpen] = useState(false);
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
    setGenerateOpen(false);
    setGenerated(null);
  };

  const handleLibrarySelect = (item) => {
    onSelect(item);
    setLibraryOpen(false);
  };

  return (
    <div className="source-selector">
      <div className="source-selector-header">
        <h3>选择多项式</h3>
        <p>从多项式库选取，或根据自然语言描述生成</p>
      </div>

      <div className="source-actions">
        <Button variant="secondary" onClick={() => setLibraryOpen(true)}>
          从多项式库选择…
        </Button>
        <Button variant="secondary" onClick={() => setGenerateOpen(true)}>
          AI 生成…
        </Button>
      </div>

      {selected && (
        <SelectedBanner>
          <PolynomialPreview expr={selected.polynomial || selected.item?.polynomial} label="f(x)" />
          {selected.item?.name && <p className="selected-name">{selected.item.name}</p>}
        </SelectedBanner>
      )}

      <Modal open={libraryOpen} onClose={() => setLibraryOpen(false)} title="选择多项式" size="xl">
        <PolynomialLibrarySelector onSelect={handleLibrarySelect} selected={selected} />
      </Modal>

      <Modal open={generateOpen} onClose={() => setGenerateOpen(false)} title="AI 生成多项式" size="md">
        <div className="generate-panel">
          <textarea
            placeholder="描述您需要的多项式，例如：给我一个三次无重根多项式"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={4}
          />
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setGenerateOpen(false)}>取消</Button>
            <Button loading={loading} onClick={handleGenerate} disabled={!requirement.trim()}>
              生成多项式
            </Button>
          </div>
          {error && <div className="error-msg">{error}</div>}
          {generated && (
            <div className="preview-box">
              <PolynomialPreview expr={generated.polynomial} label="f(x)" />
              <p>{generated.description}</p>
              {generated.warnings?.map((w, i) => (
                <p key={i} className="warning-msg">{w}</p>
              ))}
              <Button onClick={confirmGenerated}>确认使用此多项式</Button>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}

function PolynomialLibrarySelector({ onSelect, selected }) {
  const [polynomials, setPolynomials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  useEffect(() => {
    api.getPolynomialLibrary().then((resp) => {
      setPolynomials(resp.polynomials || []);
      setLoading(false);
    });
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return polynomials;
    return polynomials.filter((p) => {
      const haystack = [
        p.name,
        p.description,
        p.id,
        String(p.degree),
        ...(p.tags || []),
      ].join(' ').toLowerCase();
      return haystack.includes(q);
    });
  }, [polynomials, query]);

  if (loading) return <p className="loading-text">加载多项式库</p>;

  return (
    <div className="library-browser">
      <div className="library-toolbar">
        <input
          type="search"
          className="library-search field-input"
          placeholder="搜索名称、次数、标签或描述…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {filtered.length === 0 ? (
        <p className="roots-empty">没有匹配的多项式</p>
      ) : (
        <div className="library-grid library-grid--modal">
          {filtered.map((p) => (
            <div
              key={p.id}
              role="button"
              tabIndex={0}
              className={`library-card ${selected?.polynomial_id === p.id ? 'selected' : ''}`}
              onClick={() => onSelect({ source: 'library', polynomial_id: p.id, item: p, polynomial: p.polynomial })}
              onKeyDown={(e) => e.key === 'Enter' && onSelect({ source: 'library', polynomial_id: p.id, item: p, polynomial: p.polynomial })}
            >
              <h4>{p.name}</h4>
              <p className="meta">次数 {p.degree}</p>
              <PolynomialPreview expr={p.polynomial} label="f(x)" />
              <div className="tags">{p.tags?.map((t) => <span key={t} className="tag">{t}</span>)}</div>
              <p className="desc">{p.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
