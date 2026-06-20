/** Shared motion presets — spring-first for fluid interactions */

export const springNav = { type: 'spring', stiffness: 400, damping: 36, mass: 0.75 };
export const springSnappy = { type: 'spring', stiffness: 480, damping: 32, mass: 0.7 };
export const springSoft = { type: 'spring', stiffness: 280, damping: 28, mass: 0.9 };
export const springGentle = { type: 'spring', stiffness: 220, damping: 26, mass: 1 };

export const tweenOut = { duration: 0.22, ease: [0.4, 0, 1, 1] };
export const tweenIn = { duration: 0.42, ease: [0.22, 1, 0.36, 1] };

export const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: springSoft,
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: tweenOut,
  },
};

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, transition: tweenOut },
};

export const revealItem = {
  hidden: { opacity: 0, y: 16, scale: 0.985 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: springSoft,
  },
  exit: {
    opacity: 0,
    y: -8,
    scale: 0.99,
    transition: tweenOut,
  },
};

export const staggerResults = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.065, delayChildren: 0.04 },
  },
};

export const modalBackdrop = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.28, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

export const modalPanel = {
  hidden: { opacity: 0, y: 28, scale: 0.94 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: springSoft,
  },
  exit: {
    opacity: 0,
    y: 16,
    scale: 0.97,
    transition: tweenOut,
  },
};

export const pressableHover = (reduceMotion) => (
  reduceMotion ? undefined : { y: -2, transition: springSnappy }
);

export const pressableTap = (reduceMotion) => (
  reduceMotion ? undefined : { scale: 0.96, y: 0, transition: { duration: 0.1 } }
);

export const cardHover = (reduceMotion) => (
  reduceMotion ? undefined : { y: -4, scale: 1.012, transition: springSnappy }
);

export const cardTap = (reduceMotion) => (
  reduceMotion ? undefined : { scale: 0.985, y: -1, transition: { duration: 0.1 } }
);
