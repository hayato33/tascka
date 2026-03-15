/**
 * タスクフィルター状態のZustand Store。
 *
 * Zustand はシンプルな状態管理ライブラリ。
 * Redux と比べてボイラープレートが少なく、Hookとして自然に使える。
 *
 * このstoreでは、タスク一覧のフィルター条件（ステータス・タグ）を管理する。
 * サーバーデータ（タスク一覧そのもの）はここに入れず、TanStack Query で管理する。
 * これが「責務の分離」: UIの状態はZustand、サーバーの状態はTanStack Query。
 *
 * 注意: フィルター条件はnuqsでURLクエリパラメータと同期させることが推奨されている。
 * このstoreはnuqsと併用するか、nuqsに置き換える形で使う。
 */

import { create } from "zustand";

type TaskStatus = "todo" | "in_progress" | "done";

interface TaskFilterState {
  status: TaskStatus | null;
  tag: string | null;
  setStatus: (status: TaskStatus | null) => void;
  setTag: (tag: string | null) => void;
  reset: () => void;
}

export const useTaskFilterStore = create<TaskFilterState>((set) => ({
  status: null,
  tag: null,
  setStatus: (status) => set({ status }),
  setTag: (tag) => set({ tag }),
  reset: () => set({ status: null, tag: null }),
}));
