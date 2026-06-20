import { createContext, useContext, useEffect, useState } from 'react';
import {
  DEFAULT_DISPLAY_PRECISION,
  setGlobalDisplayPrecision,
} from '../utils/displayPrecision';

const DisplayPrecisionContext = createContext({
  precision: DEFAULT_DISPLAY_PRECISION,
  setPrecision: () => {},
});

const STORAGE_KEY = 'displayPrecision';

export function DisplayPrecisionProvider({ children }) {
  const [precision, setPrecisionState] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const parsed = saved != null ? Number(saved) : DEFAULT_DISPLAY_PRECISION;
    return Number.isFinite(parsed) && parsed > 0 ? parsed : DEFAULT_DISPLAY_PRECISION;
  });

  const setPrecision = (value) => {
    const next = Number(value);
    if (Number.isFinite(next) && next > 0) {
      setPrecisionState(next);
      localStorage.setItem(STORAGE_KEY, String(next));
    }
  };

  useEffect(() => {
    setGlobalDisplayPrecision(precision);
  }, [precision]);

  return (
    <DisplayPrecisionContext.Provider value={{ precision, setPrecision }}>
      {children}
    </DisplayPrecisionContext.Provider>
  );
}

export function useDisplayPrecision() {
  return useContext(DisplayPrecisionContext);
}
