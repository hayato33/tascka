/**
 * タスクフィルターコンポーネント。
 *
 * ステータスでタスクをフィルターするUI。
 * フィルター状態は Zustand ストアで管理する。
 *
 * "use client" が必要な理由:
 * Zustand の useTaskFilterStore Hook を使うため。
 */
"use client";

import { useTaskFilterStore } from "../stores/taskFilterStore";

const STATUS_OPTIONS = [
  { value: null, label: "すべて" },
  { value: "todo" as const, label: "未着手" },
  { value: "in_progress" as const, label: "進行中" },
  { value: "done" as const, label: "完了" },
];

export function TaskFilter() {
  const { status, setStatus } = useTaskFilterStore();

  return (
    <div className="flex gap-2">
      {STATUS_OPTIONS.map((option) => (
        <button
          type="button"
          key={option.value ?? "all"}
          onClick={() => setStatus(option.value)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${
            status === option.value
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
