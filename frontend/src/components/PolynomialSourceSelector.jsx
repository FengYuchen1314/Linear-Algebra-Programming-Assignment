import { useState, useEffect, useMemo } from 'react';
import { api } from '../api/client';
import PolynomialPreview from './PolynomialPreview';
import { SelectedBanner } from './ResultBlock';
import Modal from './ui/Modal';
import Button from './ui/Button';
import GenerateStatus from './ui/GenerateStatus';

export default function PolynomialSourceSelector({ onSelect, onConfirmAndAnalyze, selected }) {
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [generateOpen, setGenerateOpen] = useState(false);
  const [requirement, setRequirement] = useState('');
  const [generated, setGenerated] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setGenerated(null);
    try {
      const resp = await api.generatePolynomial(requirement);
      if (!resp.success) {
        setError(resp.errors?.[0] || '生成失败');
      } else {
        setGenerated(resp);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const buildSelection = () => ({
    source: 'generated',
    requirement,
    polynomial: generated.polynomial,
    description: generated.description,
  });

  const confirmGenerated = () => {
    const item = buildSelection();
    if (onConfirmAndAnalyze) {
      onConfirmAndAnalyze(item);
    } else {
      onSelect(item);
    }
    setGenerateOpen(false);
    setGenerated(null);
    setError(null);
  };

  const handleLibrarySelect = (item) => {
    onSelect(item);
    setLibraryOpen(false);
  };

  const closeGenerateModal = () => {
    if (loading) return;
    setGenerateOpen(false);
    setGenerated(null);
    setError(null);
  };

  return (
    <div className="source-selector">
      <div className="source-selector-header">
        <h3 className="md-title-medium">选择多项式</h3>
        <p className="md-body-medium">从多项式库选取，或使用 DeepSeek 根据描述生成</p>
      </div>

      <div className="source-actions">
        <Button variant="tonal" onClick={() => setLibraryOpen(true)}>
          从多项式库选择…
        </Button>
        <Button variant="outlined" onClick={() => setGenerateOpen(true)}>
          AI 生成…
        </Button>
      </div>

      {selected && (
        <SelectedBanner>
          <PolynomialPreview expr={selected.polynomial || selected.item?.polynomial} label="f(x)" />
          {selected.item?.name && <p className="selected-name md-body-small">{selected.item.name}</p>}
          {selected.description && !selected.item?.name && (
            <p className="selected-name md-body-small">{selected.description}</p>
          )}
        </SelectedBanner>
      )}

      <Modal open={libraryOpen} onClose={() => setLibraryOpen(false)} title="选择多项式" size="xl">
        <PolynomialLibrarySelector onSelect={handleLibrarySelect} selected={selected} />
      </Modal>

      <Modal open={generateOpen} onClose={closeGenerateModal} title="AI 生成多项式" size="md">
        <div className="generate-panel">
          <p className="md-body-medium generate-panel-hint">
            用自然语言描述多项式特征，例如次数、实根个数、是否有重根等。
          </p>
          <textarea
            className="md-outlined-input"
            placeholder="例如：给我一个三次无重根、有三个不同实根的多项式"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={4}
            disabled={loading}
          />
          <GenerateStatus loading={loading} error={error && !generated ? error : null} entityLabel="多项式" />
          {!loading && (
            <div className="modal-actions">
              <Button variant="text" onClick={closeGenerateModal}>取消</Button>
              <Button loading={loading} onClick={handleGenerate} disabled={!requirement.trim()}>
                开始生成
              </Button>
            </div>
          )}
          {generated && !loading && (
            <div className="preview-box">
              <p className="md-label-medium preview-box-label">生成预览</p>
              <PolynomialPreview expr={generated.polynomial} label="f(x)" />
              <p className="md-body-medium">{generated.description}</p>
              {generated.warnings?.map((w, i) => (
                <p key={i} className="warning-msg md-body-small">{w}</p>
              ))}
              <Button onClick={confirmGenerated}>确认使用并分析</Button>
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
      const haystack = [p.name, p.description, p.id, String(p.degree), ...(p.tags || [])].join(' ').toLowerCase();
      return haystack.includes(q);
    });
  }, [polynomials, query]);

  if (loading) return <p className="loading-text md-body-medium">加载多项式库…</p>;

  return (
    <div className="library-browser">
      <div className="library-toolbar">
        <input
          type="search"
          className="library-search md-outlined-input"
          placeholder="搜索名称、次数、标签或描述…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {filtered.length === 0 ? (
        <p className="roots-empty md-body-medium">没有匹配的多项式</p>
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
              <h4 className="md-title-small">{p.name}</h4>
              <p className="meta md-label-medium">次数 {p.degree}</p>
              <PolynomialPreview expr={p.polynomial} label="f(x)" />
              <div className="tags">{p.tags?.map((t) => <span key={t} className="tag">{t}</span>)}</div>
              <p className="desc md-body-small">{p.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
