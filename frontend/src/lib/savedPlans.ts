/**
 * Saved plans store (Phase 3 → Phase 5).
 *
 * Supports two backends:
 *  - localStorage (anonymous users — device-only bookmarks)
 *  - API (logged-in users — plans persist per user account)
 *
 * The `SavedPlansStore` interface is async so both backends share the
 * same shape.  `getStore(isLoggedIn)` returns the right implementation.
 *
 * `migrateLocalPlans()` moves any localStorage plans to the server
 * the first time a user logs in, then clears localStorage.
 */
import { api } from "../api/client";
import type { RedesignResult } from "../types";

export interface SavedPlan {
  /** Stable id (localStorage: client-generated; API: stringified server id). */
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
  list(): Promise<SavedPlan[]>;
  save(plan: SavedPlan): Promise<SavedPlan>;
  remove(id: string): Promise<void>;
}

const STORAGE_KEY = "nexa_saved_plans";
const MAX_PLANS = 20;

// ── localStorage backend (anonymous) ──────────────────────────────────────────

function loadLocal(): SavedPlan[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as SavedPlan[]) : [];
  } catch {
    return [];
  }
}

function persistLocal(plans: SavedPlan[]) {
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
  async list() {
    return loadLocal().sort((a, b) => b.saved_at.localeCompare(a.saved_at));
  },
  async save(plan) {
    const plans = loadLocal().filter((p) => p.id !== plan.id);
    plans.unshift(plan);
    persistLocal(plans);
    return plan;
  },
  async remove(id) {
    persistLocal(loadLocal().filter((p) => p.id !== id));
  },
};

// ── API backend (logged-in) ───────────────────────────────────────────────────

interface SavedRedesignAPI {
  id: number;
  client_id: string;
  role: string;
  target_role: string;
  age: number | null;
  user_skills: string[];
  result: RedesignResult;
  created_at: string;
}

function apiPlanToSavedPlan(r: SavedRedesignAPI): SavedPlan {
  return {
    id: String(r.id),
    saved_at: r.created_at,
    role: r.role,
    target_role: r.target_role || null,
    age: r.age,
    user_skills: r.user_skills,
    result: r.result,
  };
}

const apiStore: SavedPlansStore = {
  async list() {
    const rows = await api.get<SavedRedesignAPI[]>("/api/saved-redesigns");
    return rows.map(apiPlanToSavedPlan);
  },
  async save(plan) {
    const row = await api.post<SavedRedesignAPI>("/api/saved-redesigns", {
      client_id: plan.id,
      role: plan.role,
      target_role: plan.target_role ?? "",
      age: plan.age ?? null,
      user_skills: plan.user_skills ?? [],
      result: plan.result,
    });
    return apiPlanToSavedPlan(row);
  },
  async remove(id) {
    await api.del(`/api/saved-redesigns/${parseInt(id, 10)}`);
  },
};

// ── Factory ───────────────────────────────────────────────────────────────────

export function getStore(loggedIn: boolean): SavedPlansStore {
  return loggedIn ? apiStore : localStorageStore;
}

// ── Migration (localStorage → server on first login) ──────────────────────────

export async function migrateLocalPlans(): Promise<void> {
  const localPlans = loadLocal();
  if (localPlans.length === 0) return;
  for (const plan of localPlans) {
    try {
      await api.post("/api/saved-redesigns", {
        client_id: plan.id,
        role: plan.role,
        target_role: plan.target_role ?? "",
        age: plan.age ?? null,
        user_skills: plan.user_skills ?? [],
        result: plan.result,
      });
    } catch {
      // best-effort — skip plans that fail to upload
    }
  }
  // Clear localStorage after migration
  localStorage.removeItem(STORAGE_KEY);
}
