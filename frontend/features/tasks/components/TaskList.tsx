/**
 * タスク一覧コンポーネント。
 *
 * "use client" が必要な理由:
 * TanStack Query の useTasks Hook を使うため。
 * Hooks は Client Component でしか使えない。
 */
"use client";

import { useTasks } from "../api/useTasks";
import { TaskCard } from "./TaskCard";

export function TaskList() {
  const { data, isLoading, error } = useTasks();

  if (isLoading) {
    return <div className="text-gray-500">読み込み中...</div>;
  }

  if (error) {
    return <div className="text-red-500">エラー: {error.message}</div>;
  }

  if (!data || data.items.length === 0) {
    return <div className="text-gray-500">タスクがありません</div>;
  }

  return (
    <div className="space-y-4">
      {data.items.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
}
