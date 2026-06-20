import { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import SturmPage from '../../pages/SturmPage';
import MatrixPropertiesPage from '../../pages/MatrixPropertiesPage';
import DecompositionPage from '../../pages/DecompositionPage';
import JordanPage from '../../pages/JordanPage';
import LambdaSmithPage from '../../pages/LambdaSmithPage';
import { useDisplayPrecision } from '../../context/DisplayPrecisionContext';
import { fadeUp } from '../../motion/presets';

export default function AnimatedRoutes() {
  useDisplayPrecision();
  const location = useLocation();
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <main className="app-main">
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={location.pathname}
          className="route-transition"
          variants={fadeUp}
          initial={reduceMotion ? false : 'hidden'}
          animate="visible"
          exit={reduceMotion ? undefined : 'exit'}
        >
          <Routes location={location}>
            <Route path="/" element={<SturmPage />} />
            <Route path="/matrix-properties" element={<MatrixPropertiesPage />} />
            <Route path="/decomposition" element={<DecompositionPage />} />
            <Route path="/jordan" element={<JordanPage />} />
            <Route path="/lambda-smith" element={<LambdaSmithPage />} />
          </Routes>
        </motion.div>
      </AnimatePresence>
    </main>
  );
}
