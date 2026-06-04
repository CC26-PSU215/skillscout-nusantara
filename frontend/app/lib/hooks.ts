/**
 * Custom React Hooks — Debounce & Throttle utilities.
 *
 * Debouncing: Menunda pemanggilan sampai pengguna berhenti mengetik
 *   selama durasi tertentu. Cocok untuk Search Bar, auto-save.
 *
 * Throttling: Memastikan fungsi hanya dipanggil maksimal 1x per interval.
 *   Cocok untuk scroll, resize, prevent double-click.
 */

import { useState, useEffect, useRef, useCallback } from "react";

// ══════════════════════════════════════════════════════════════
// useDebounce — delay value update until user stops changing it
// ══════════════════════════════════════════════════════════════

/**
 * Debounce a value — hanya update setelah `delay` ms tanpa perubahan.
 *
 * @example
 * const [search, setSearch] = useState("");
 * const debouncedSearch = useDebounce(search, 500);
 * // debouncedSearch hanya berubah 500ms setelah user berhenti mengetik
 */
export function useDebounce<T>(value: T, delay: number = 2000): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// ══════════════════════════════════════════════════════════════
// useThrottle — limit how often a value can change
// ══════════════════════════════════════════════════════════════

/**
 * Throttle a value — hanya update maksimal 1x per `interval` ms.
 *
 * @example
 * const throttledScroll = useThrottle(scrollY, 200);
 */
export function useThrottle<T>(value: T, interval: number = 500): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastUpdated = useRef<number>(Date.now());

  useEffect(() => {
    const now = Date.now();
    const elapsed = now - lastUpdated.current;

    if (elapsed >= interval) {
      // Enough time has passed — update immediately
      lastUpdated.current = now;
      setThrottledValue(value);
    } else {
      // Schedule update for remaining time
      const timer = setTimeout(() => {
        lastUpdated.current = Date.now();
        setThrottledValue(value);
      }, interval - elapsed);

      return () => clearTimeout(timer);
    }
  }, [value, interval]);

  return throttledValue;
}

// ══════════════════════════════════════════════════════════════
// useThrottledCallback — prevent double-click / rapid fire
// ══════════════════════════════════════════════════════════════

/**
 * Returns a throttled version of a callback function.
 * Prevents rapid-fire calls (e.g., double-click on submit buttons).
 *
 * @example
 * const handleClick = useThrottledCallback(async () => {
 *   await submitForm();
 * }, 1000);
 */
export function useThrottledCallback<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number = 1000
): (...args: Parameters<T>) => void {
  const lastCall = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      const elapsed = now - lastCall.current;

      if (elapsed >= delay) {
        lastCall.current = now;
        callback(...args);
      }
    },
    [callback, delay]
  );
}
