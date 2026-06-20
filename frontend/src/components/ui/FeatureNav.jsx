import { NavLink, useLocation } from 'react-router-dom';
import { LayoutGroup, motion, useReducedMotion } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { springNav } from '../../motion/presets';

function matchPath(path, pathname) {
  return path === '/' ? pathname === '/' : pathname === path;
}

export default function FeatureNav({ items }) {
  const { pathname } = useLocation();
  const pillRef = useRef(null);
  const tabRefs = useRef({});
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    const activePath = items.find((item) => matchPath(item.path, pathname))?.path;
    const tab = activePath ? tabRefs.current[activePath] : null;
    if (!tab) return undefined;

    const timer = window.setTimeout(() => {
      tab.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', inline: 'center', block: 'nearest' });
    }, reduceMotion ? 0 : 180);

    return () => window.clearTimeout(timer);
  }, [items, pathname, reduceMotion]);

  return (
    <nav className="feature-nav" aria-label="功能选择">
      <LayoutGroup id="feature-nav">
        <div className="feature-nav__pill glass-pill" ref={pillRef}>
          {items.map(({ path, label, Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              ref={(el) => {
                tabRefs.current[path] = el;
              }}
              className="feature-nav__tab"
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span
                      layoutId="feature-nav-indicator"
                      className="feature-nav__indicator"
                      transition={reduceMotion ? { duration: 0 } : springNav}
                    />
                  )}
                  <span className={`feature-nav__tab-inner${isActive ? ' is-active' : ''}`}>
                    <motion.span
                      className="feature-nav__tab-icon"
                      animate={isActive ? { scale: 1.08 } : { scale: 1 }}
                      transition={springNav}
                    >
                      <Icon aria-hidden />
                    </motion.span>
                    <span>{label}</span>
                  </span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </LayoutGroup>
    </nav>
  );
}
