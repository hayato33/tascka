/**
 * タスクカードコンポーネント。
 *
 * 個々のタスクを表示するカードUI。
 * タスク一覧（TaskList）から呼び出される。
 */

import type { Task } from "../types";

const STATUS_LABELS: Record<string, string> = {
  todo: "未着手",
  in_progress: "進行中",
  done: "完了",
};

const STATUS_COLORS: Record<string, string> = {
  todo: "bg-gray-100 text-gray-800",
  in_progress: "bg-blue-100 text-blue-800",
  done: "bg-green-100 text-green-800",
};

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <h3 className="text-lg font-semibold">{task.title}</h3>
        <span
          className={`rounded-full px-2 py-1 text-xs font-medium ${STATUS_COLORS[task.status]}`}
        >
          {STATUS_LABELS[task.status]}
        </span>
      </div>
      {task.description && (
        <p className="mt-2 text-sm text-gray-600">{task.description}</p>
      )}
      {task.tags.length > 0 && (
        <div className="mt-3 flex gap-2">
          {task.tags.map((tag) => (
            <span
              key={tag.id}
              className="rounded bg-gray-200 px-2 py-0.5 text-xs text-gray-700"
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
