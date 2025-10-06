// ============================================================================
// Motion Design Tokens - Animation and Transition System
// ============================================================================
//
// @file motion.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Scientific motion system with duration scales and easing functions
//
// Etymology: Latin "motio" = movement, action
// Methodology: Decimal-based duration progression with semantic easing curves
// ============================================================================

/**
 * Duration scale for animations and transitions
 * Etymology: Latin "durare" = to last, endure
 * Decimal progression in milliseconds for systematic timing relationships
 */
export const duration = {
  // Micro durations (sub-100ms)
  instant: 0,         // 0ms - immediate, no animation
  swift: 75,          // 75ms - micro-interactions, hover states
  quick: 100,         // 100ms - quick feedback, button presses
  
  // Base durations (100-500ms)
  fast: 150,          // 150ms - fast transitions, tooltips
  moderate: 250,      // 250ms - standard transitions, modals
  deliberate: 350,    // 350ms - emphasized changes, page transitions
  slow: 500,          // 500ms - dramatic effects, loading states
  
  // Extended durations (500ms+)
  extended: 750,      // 750ms - complex animations, reveals
  prolonged: 1000,    // 1000ms - hero animations, onboarding
  marathon: 1500,     // 1500ms - extended sequences, storytelling
  
  // Semantic aliases for common use cases
  hover: 75,          // swift - hover state changes
  focus: 150,         // fast - focus indicator transitions
  button: 100,        // quick - button press feedback
  tooltip: 150,       // fast - tooltip show/hide
  modal: 250,         // moderate - modal open/close
  page: 350,          // deliberate - page transitions
  loading: 500,       // slow - loading state changes
} as const;

/**
 * Easing functions for natural motion curves
 * Etymology: "ease" = comfort, natural flow
 * CSS cubic-bezier functions optimized for different motion types
 */
export const easing = {
  /**
   * Linear easing - constant speed throughout
   * Use for: Progress indicators, mechanical movements
   */
  linear: 'linear',
  
  /**
   * Ease-in curves - slow start, fast finish
   * Use for: Elements leaving the screen, fade-outs
   */
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  easeInQuad: 'cubic-bezier(0.55, 0.085, 0.68, 0.53)',
  easeInCubic: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',
  easeInQuart: 'cubic-bezier(0.895, 0.03, 0.685, 0.22)',
  easeInQuint: 'cubic-bezier(0.755, 0.05, 0.855, 0.06)',
  
  /**
   * Ease-out curves - fast start, slow finish
   * Use for: Elements entering the screen, fade-ins
   */
  easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  easeOutQuad: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  easeOutCubic: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
  easeOutQuart: 'cubic-bezier(0.165, 0.84, 0.44, 1)',
  easeOutQuint: 'cubic-bezier(0.23, 1, 0.32, 1)',
  
  /**
   * Ease-in-out curves - slow start and finish, fast middle
   * Use for: State changes, transformations, most UI animations
   */
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  easeInOutQuad: 'cubic-bezier(0.455, 0.03, 0.515, 0.955)',
  easeInOutCubic: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
  easeInOutQuart: 'cubic-bezier(0.77, 0, 0.175, 1)',
  easeInOutQuint: 'cubic-bezier(0.86, 0, 0.07, 1)',
  
  /**
   * Bounce and elastic curves for playful interactions
   * Use for: Success states, playful feedback, attention-grabbing
   */
  easeOutBounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  easeOutBack: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  easeInOutBack: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  
  /**
   * Semantic aliases for common interaction patterns
   */
  entrance: 'cubic-bezier(0, 0, 0.2, 1)',        // easeOut - elements entering
  exit: 'cubic-bezier(0.4, 0, 1, 1)',            // easeIn - elements leaving
  transition: 'cubic-bezier(0.4, 0, 0.2, 1)',    // easeInOut - state changes
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)', // playful feedback
} as const;

/**
 * Animation presets for common UI patterns
 * Etymology: "preset" = pre-established setting
 * Complete animation configurations for typical use cases
 */
export const animationPresets = {
  /**
   * Fade animations for opacity changes
   */
  fade: {
    in: {
      duration: duration.moderate,
      easing: easing.entrance,
      keyframes: 'fadeIn',
    },
    out: {
      duration: duration.fast,
      easing: easing.exit,
      keyframes: 'fadeOut',
    },
  },
  
  /**
   * Slide animations for spatial movement
   */
  slide: {
    up: {
      duration: duration.moderate,
      easing: easing.entrance,
      keyframes: 'slideUp',
    },
    down: {
      duration: duration.moderate,
      easing: easing.entrance,
      keyframes: 'slideDown',
    },
    left: {
      duration: duration.moderate,
      easing: easing.entrance,
      keyframes: 'slideLeft',
    },
    right: {
      duration: duration.moderate,
      easing: easing.entrance,
      keyframes: 'slideRight',
    },
  },
  
  /**
   * Scale animations for size changes
   */
  scale: {
    in: {
      duration: duration.moderate,
      easing: easing.bounce,
      keyframes: 'scaleIn',
    },
    out: {
      duration: duration.fast,
      easing: easing.exit,
      keyframes: 'scaleOut',
    },
  },
  
  /**
   * Rotation animations for spinning elements
   */
  rotate: {
    clockwise: {
      duration: duration.prolonged,
      easing: easing.linear,
      keyframes: 'rotateClockwise',
    },
    counterclockwise: {
      duration: duration.prolonged,
      easing: easing.linear,
      keyframes: 'rotateCounterclockwise',
    },
  },
  
  /**
   * Pulse animations for attention-grabbing
   */
  pulse: {
    subtle: {
      duration: duration.prolonged,
      easing: easing.easeInOut,
      keyframes: 'pulseSubtle',
    },
    strong: {
      duration: duration.slow,
      easing: easing.easeInOut,
      keyframes: 'pulseStrong',
    },
  },
} as const;

/**
 * CSS keyframe definitions for animation presets
 * These can be injected into styled-components or CSS
 */
export const keyframes = {
  fadeIn: `
    from { opacity: 0; }
    to { opacity: 1; }
  `,
  
  fadeOut: `
    from { opacity: 1; }
    to { opacity: 0; }
  `,
  
  slideUp: `
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
  
  slideDown: `
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
  
  slideLeft: `
    from { transform: translateX(20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `,
  
  slideRight: `
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `,
  
  scaleIn: `
    from { transform: scale(0.8); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  `,
  
  scaleOut: `
    from { transform: scale(1); opacity: 1; }
    to { transform: scale(0.8); opacity: 0; }
  `,
  
  rotateClockwise: `
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  `,
  
  rotateCounterclockwise: `
    from { transform: rotate(0deg); }
    to { transform: rotate(-360deg); }
  `,
  
  pulseSubtle: `
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  `,
  
  pulseStrong: `
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  `,
} as const;

/**
 * Reduced motion preferences
 * Respects user's accessibility preferences for motion
 */
export const reducedMotion = {
  // Reduced duration for users who prefer less motion
  duration: {
    instant: 0,
    swift: 0,
    quick: 0,
    fast: 0,
    moderate: 0,
    deliberate: 0,
    slow: 0,
  },
  
  // Simplified easing for reduced motion
  easing: {
    all: 'linear',
  },
  
  // CSS media query for reduced motion preference
  mediaQuery: '@media (prefers-reduced-motion: reduce)',
} as const;

/**
 * Type definitions for motion tokens
 * Ensures type safety across the design system
 */
export type DurationScale = keyof typeof duration;
export type EasingScale = keyof typeof easing;
export type AnimationPresetScale = keyof typeof animationPresets;
export type KeyframeScale = keyof typeof keyframes;

/**
 * Utility functions for motion calculations
 */

/**
 * Convert duration scale to milliseconds
 * @param scale - Duration scale key
 * @returns Duration in milliseconds as string
 */
export const getDuration = (scale: DurationScale): string => 
  `${duration[scale]}ms`;

/**
 * Create CSS transition property
 * @param property - CSS property to transition
 * @param durationScale - Duration scale key
 * @param easingScale - Easing scale key
 * @returns Complete CSS transition string
 */
export const transition = (
  property: string = 'all',
  durationScale: DurationScale = 'moderate',
  easingScale: EasingScale = 'transition'
): string => 
  `${property} ${getDuration(durationScale)} ${easing[easingScale]}`;

/**
 * Create multiple CSS transitions
 * @param transitions - Array of transition configurations
 * @returns Comma-separated CSS transition string
 */
export const multipleTransitions = (
  transitions: Array<{
    property: string;
    duration: DurationScale;
    easing: EasingScale;
  }>
): string => 
  transitions
    .map(({ property, duration: dur, easing: ease }) => 
      transition(property, dur, ease)
    )
    .join(', ');

/**
 * Generate CSS custom properties for motion tokens
 * Enables runtime theme switching and CSS variable usage
 */
export const motionCSSProperties = {
  // Durations
  '--duration-instant': getDuration('instant'),
  '--duration-swift': getDuration('swift'),
  '--duration-quick': getDuration('quick'),
  '--duration-fast': getDuration('fast'),
  '--duration-moderate': getDuration('moderate'),
  '--duration-deliberate': getDuration('deliberate'),
  '--duration-slow': getDuration('slow'),
  
  // Easing functions
  '--easing-linear': easing.linear,
  '--easing-ease-in': easing.easeIn,
  '--easing-ease-out': easing.easeOut,
  '--easing-ease-in-out': easing.easeInOut,
  '--easing-entrance': easing.entrance,
  '--easing-exit': easing.exit,
  '--easing-transition': easing.transition,
  '--easing-bounce': easing.bounce,
  
  // Common transitions
  '--transition-fast': transition('all', 'fast', 'transition'),
  '--transition-moderate': transition('all', 'moderate', 'transition'),
  '--transition-slow': transition('all', 'slow', 'transition'),
} as const;
