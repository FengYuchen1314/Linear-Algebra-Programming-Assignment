import { useState, useEffect, useMemo } from 'react';
import { api } from '../api/client';
import MatrixPreview from './MatrixPreview';
import { SelectedBanner } from './ResultBlock';
import Modal from './ui/Modal';
import Button from './ui/Button';
import GenerateStatus from './ui/GenerateStatus';

export { MatrixPreview };

export default function MatrixSourceSelector({
  onSelect,
  onConfirmAndAnalyze,
  selected,
  matrixTypeHint = 'auto',
  squareOnly = false,
}) {
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
    const mtype = squareOnly ? 'square' : matrixTypeHint;
    try {
      const resp = await api.generateMatrix(requirement, mtype);
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
    matrix: generated.matrix,
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

  const canGenerate = requirement.trim().length > 0;

  return (
    <div className="source-selector">
      <div className="source-selector-header">
        <h3 className="text-h4">选择矩阵</h3>
        <p className="text-body">从矩阵库选取，或使用 DeepSeek 根据描述生成</p>
      </div>

      <div className="source-actions">
        <Button variant="tonal" onClick={() => setLibraryOpen(true)}>
          从矩阵库选择…
        </Button>
        <Button variant="outlined" onClick={() => setGenerateOpen(true)}>
          AI 生成…
        </Button>
      </div>

      {selected && (
        <SelectedBanner>
          <MatrixPreview matrix={selected.matrix || selected.item?.matrix} />
          {selected.item?.name && <p className="selected-name text-muted">{selected.item.name}</p>}
          {selected.description && !selected.item?.name && (
            <p className="selected-name text-muted">{selected.description}</p>
          )}
        </SelectedBanner>
      )}

      <Modal open={libraryOpen} onClose={() => setLibraryOpen(false)} title="选择矩阵" size="xl">
        <MatrixLibrarySelector
          onSelect={handleLibrarySelect}
          selected={selected}
          squareOnly={squareOnly}
        />
      </Modal>

      <Modal open={generateOpen} onClose={closeGenerateModal} title="AI 生成矩阵" size="md">
        <div className="generate-panel">
          <p className="text-body generate-panel-hint">
            用自然语言描述矩阵特征，例如维度、可逆性、Jordan 结构等。
          </p>
          <textarea
            className="input"
            placeholder="例如：给我一个三阶可对角化、特征值为 1,2,3 的矩阵"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={4}
            disabled={loading}
          />
          <GenerateStatus loading={loading} error={error && !generated ? error : null} entityLabel="矩阵" />
          {generated && !loading && (
            <div className="preview-box">
              <p className="text-label preview-box-label">生成预览</p>
              <MatrixPreview matrix={generated.matrix} />
              <p className="text-body">{generated.description}</p>
            </div>
          )}
          <div className="generate-panel__footer modal-actions">
            {generated && !loading ? (
              <>
                <Button variant="ghost" onClick={() => { setGenerated(null); setError(null); }}>
                  重新生成
                </Button>
                <Button onClick={confirmGenerated}>确认使用并分析</Button>
              </>
            ) : (
              <>
                <Button variant="ghost" onClick={closeGenerateModal} disabled={loading}>
                  取消
                </Button>
                <Button
                  onClick={handleGenerate}
                  loading={loading}
                  disabled={!canGenerate}
                  title={canGenerate ? undefined : '请先输入描述'}
                >
                  开始生成
                </Button>
              </>
            )}
          </div>
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
      const haystack = [m.name, m.description, m.id, ...(m.tags || [])].join(' ').toLowerCase();
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
          className="library-search input"
          placeholder="搜索名称、标签或描述…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {loading ? (
        <p className="loading-text text-muted">加载矩阵库…</p>
      ) : filtered.length === 0 ? (
        <p className="roots-empty text-muted">没有匹配的矩阵</p>
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
              <h4 className="text-h4">{m.name}</h4>
              <p className="meta text-label">{m.rows}×{m.cols}</p>
              <MatrixPreview matrix={m.matrix} compact />
              <div className="tags">{m.tags?.map((t) => <span key={t} className="tag">{t}</span>)}</div>
              <p className="desc text-muted">{m.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
