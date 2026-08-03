/**
 * Saved plans store (Phase 3).
 *
 * Currently persists bookmarks to localStorage (device-only).  The
 * `SavedPlansStore` interface is deliberately storage-agnostic so that
 * when user accounts are introduced, the localStorage implementation can
 * be swapped for an API-backed store without touching any UI code —
 * each plan already carries a stable id and timestamp.
 */
import type { RedesignResult } from "../types";

export interface SavedPlan {
  /** Stable id (survives a future move to server-side storage). */
  id: string;
  saved_at: string; // ISO timestamp
  // Request context — lets the user regenerate this exact plan later.
  role: string;
  target_role?: string | null;
  age?: number | null;
  user_skills?: string[];
  // Full result snapshot.
  result: RedesignResult;
}

export interface SavedPlansStore {
  list(): SavedPlan[];
  save(plan: SavedPlan): void;
  remove(id: string): void;
}

const STORAGE_KEY = "nexa_saved_plans";
const MAX_PLANS = 20;

function load(): SavedPlan[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as SavedPlan[]) : [];
  } catch {
    return [];
  }
}

function persist(plans: SavedPlan[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plans.slice(0, MAX_PLANS)));
  } catch {
    // storage full / unavailable — bookmarks are best-effort
  }
}

export function makePlanId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

const localStorageStore: SavedPlansStore = {
  list() {
    // newest first
    return load().sort((a, b) => b.saved_at.localeCompare(a.saved_at));
  },
  save(plan) {
    const plans = load().filter((p) => p.id !== plan.id);
    plans.unshift(plan);
    persist(plans);
  },
  remove(id) {
    persist(load().filter((p) => p.id !== id));
  },
};

export const savedPlansStore: SavedPlansStore = localStorageStore;
