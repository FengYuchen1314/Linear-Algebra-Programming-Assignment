import { useState, useEffect, useMemo } from 'react';
import { api } from '../api/client';
import MatrixPreview from './MatrixPreview';
import { SelectedBanner } from './ResultBlock';
import Modal from './ui/Modal';
import Button from './ui/Button';

export { MatrixPreview };

export default function MatrixSourceSelector({ onSelect, selected, matrixTypeHint = 'auto', squareOnly = false }) {
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [generateOpen, setGenerateOpen] = useState(false);
  const [requirement, setRequirement] = useState('');
  const [generated, setGenerated] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    const mtype = squareOnly ? 'square' : matrixTypeHint;
    try {
      const resp = await api.generateMatrix(requirement, mtype);
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
      matrix: generated.matrix,
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
        <h3>选择矩阵</h3>
        <p>从矩阵库选取，或根据自然语言描述生成</p>
      </div>

      <div className="source-actions">
        <Button variant="secondary" onClick={() => setLibraryOpen(true)}>
          从矩阵库选择…
        </Button>
        <Button variant="secondary" onClick={() => setGenerateOpen(true)}>
          AI 生成…
        </Button>
      </div>

      {selected && (
        <SelectedBanner>
          <MatrixPreview matrix={selected.matrix || selected.item?.matrix} />
          {selected.item?.name && <p className="selected-name">{selected.item.name}</p>}
        </SelectedBanner>
      )}

      <Modal open={libraryOpen} onClose={() => setLibraryOpen(false)} title="选择矩阵" size="xl">
        <MatrixLibrarySelector
          onSelect={handleLibrarySelect}
          selected={selected}
          squareOnly={squareOnly}
        />
      </Modal>

      <Modal open={generateOpen} onClose={() => setGenerateOpen(false)} title="AI 生成矩阵" size="md">
        <div className="generate-panel">
          <textarea
            placeholder="描述您需要的矩阵，例如：给我一个三阶可逆矩阵"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={4}
          />
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setGenerateOpen(false)}>取消</Button>
            <Button loading={loading} onClick={handleGenerate} disabled={!requirement.trim()}>
              生成矩阵
            </Button>
          </div>
          {error && <div className="error-msg">{error}</div>}
          {generated && (
            <div className="preview-box">
              <MatrixPreview matrix={generated.matrix} />
              <p>{generated.description}</p>
              <Button onClick={confirmGenerated}>确认使用此矩阵</Button>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}

function MatrixLibrarySelector({ onSelect, selected, squareOnly }) {
  const [libType, setLibType] = useState(squareOnly ? 'square' : 'square');
  const [matrices, setMatrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  useEffect(() => {
    setLoading(true);
    const fetcher = libType === 'square' ? api.getSquareMatrices : api.getRectangularMatrices;
    fetcher().then((resp) => {
      setMatrices(resp.matrices || []);
      setLoading(false);
    });
  }, [libType]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return matrices;
    return matrices.filter((m) => {
      const haystack = [
        m.name,
        m.description,
        m.id,
        ...(m.tags || []),
      ].join(' ').toLowerCase();
      return haystack.includes(q);
    });
  }, [matrices, query]);

  return (
    <div className="library-browser">
      <div className="library-toolbar">
        {!squareOnly && (
          <div className="mode-tabs sub-tabs">
            <button type="button" className={libType === 'square' ? 'tab active' : 'tab'} onClick={() => setLibType('square')}>
              方阵库
            </button>
            <button type="button" className={libType === 'rectangular' ? 'tab active' : 'tab'} onClick={() => setLibType('rectangular')}>
              非方阵库
            </button>
          </div>
        )}
        <input
          type="search"
          className="library-search field-input"
          placeholder="搜索名称、标签或描述…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {loading ? (
        <p className="loading-text">加载矩阵库</p>
      ) : filtered.length === 0 ? (
        <p className="roots-empty">没有匹配的矩阵</p>
      ) : (
        <div className="library-grid library-grid--modal">
          {filtered.map((m) => (
            <div
              key={m.id}
              role="button"
              tabIndex={0}
              className={`library-card ${selected?.matrix_id === m.id ? 'selected' : ''}`}
              onClick={() => onSelect({ source: 'library', matrix_id: m.id, item: m, matrix: m.matrix })}
              onKeyDown={(e) => e.key === 'Enter' && onSelect({ source: 'library', matrix_id: m.id, item: m, matrix: m.matrix })}
            >
              <h4>{m.name}</h4>
              <p className="meta">{m.rows}×{m.cols}</p>
              <MatrixPreview matrix={m.matrix} compact />
              <div className="tags">{m.tags?.map((t) => <span key={t} className="tag">{t}</span>)}</div>
              <p className="desc">{m.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
