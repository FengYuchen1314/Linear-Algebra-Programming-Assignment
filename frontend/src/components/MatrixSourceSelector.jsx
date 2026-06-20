import { useState, useEffect } from 'react';
import { api } from '../api/client';
import MatrixPreview from './MatrixPreview';

export { MatrixPreview };

export default function MatrixSourceSelector({ onSelect, selected, matrixTypeHint = 'auto', squareOnly = false }) {
  const [mode, setMode] = useState('library');
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
  };

  return (
    <div className="source-selector">
      <div className="mode-tabs">
        <button className={mode === 'library' ? 'tab active' : 'tab'} onClick={() => setMode('library')}>
          从矩阵库选择
        </button>
        <button className={mode === 'generate' ? 'tab active' : 'tab'} onClick={() => setMode('generate')}>
          根据要求生成
        </button>
      </div>

      {mode === 'generate' && (
        <div className="generate-panel">
          <textarea
            placeholder="描述您需要的矩阵，例如：给我一个三阶可逆矩阵"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={3}
          />
          <button onClick={handleGenerate} disabled={loading || !requirement.trim()}>
            {loading ? '生成中...' : '生成矩阵'}
          </button>
          {error && <div className="error-msg">{error}</div>}
          {generated && (
            <div className="preview-box">
              <MatrixPreview matrix={generated.matrix} />
              <p>{generated.description}</p>
              <button onClick={confirmGenerated}>确认使用此矩阵</button>
            </div>
          )}
        </div>
      )}

      {mode === 'library' && (
        <MatrixLibrarySelector onSelect={onSelect} selected={selected} squareOnly={squareOnly} />
      )}

      {selected && (
        <div className="selected-info">
          <strong>已选择：</strong>
          <MatrixPreview matrix={selected.matrix || selected.item?.matrix} />
        </div>
      )}
    </div>
  );
}

function MatrixLibrarySelector({ onSelect, selected, squareOnly }) {
  const [libType, setLibType] = useState(squareOnly ? 'square' : 'square');
  const [matrices, setMatrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const fetcher = libType === 'square' ? api.getSquareMatrices : api.getRectangularMatrices;
    fetcher().then((resp) => {
      setMatrices(resp.matrices || []);
      setLoading(false);
    });
  }, [libType]);

  return (
    <div>
      {!squareOnly && (
        <div className="mode-tabs sub-tabs">
          <button className={libType === 'square' ? 'tab active' : 'tab'} onClick={() => setLibType('square')}>
            方阵库
          </button>
          <button className={libType === 'rectangular' ? 'tab active' : 'tab'} onClick={() => setLibType('rectangular')}>
            非方阵库
          </button>
        </div>
      )}
      {loading ? <p>加载矩阵库...</p> : (
        <div className="library-grid">
          {matrices.map((m) => (
            <div
              key={m.id}
              className={`library-card ${selected?.matrix_id === m.id ? 'selected' : ''}`}
              onClick={() => onSelect({ source: 'library', matrix_id: m.id, item: m, matrix: m.matrix })}
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
