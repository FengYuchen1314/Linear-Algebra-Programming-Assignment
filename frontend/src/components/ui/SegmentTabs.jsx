import { LayoutGroup, motion, useReducedMotion } from 'framer-motion';
import { pressableTap, springNav } from '../../motion/presets';

export default function SegmentTabs({ value, onChange, options, layoutId = 'segment-tabs' }) {
  const reduceMotion = useReducedMotion();

  return (
    <LayoutGroup id={layoutId}>
      <div className="segment-tabs" role="tablist">
        {options.map((option) => {
          const isActive = value === option.value;
          return (
            <motion.button
              key={option.value}
              type="button"
              role="tab"
              aria-selected={isActive}
              className={`segment-tabs__tab${isActive ? ' is-active' : ''}`}
              onClick={() => onChange(option.value)}
              whileTap={pressableTap(reduceMotion)}
            >
              {isActive && (
                <motion.span
                  layoutId={`${layoutId}-indicator`}
                  className="segment-tabs__indicator"
                  transition={reduceMotion ? { duration: 0 } : springNav}
                />
              )}
              <span className="segment-tabs__label">{option.label}</span>
            </motion.button>
          );
        })}
      </div>
    </LayoutGroup>
  );
}
