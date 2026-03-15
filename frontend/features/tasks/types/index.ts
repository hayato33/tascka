/**
 * タスク関連の型定義。
 *
 * openapi-typescript で生成した型をここで re-export する。
 * 型生成後に以下のようにインポートを切り替える:
 *
 * import type { components } from "@/types/api";
 * export type Task = components["schemas"]["TaskResponse"];
 * export type TaskCreate = components["schemas"]["TaskCreate"];
 *
 * 現時点では手動で型を定義しているが、
 * `npm run gen:api` で自動生成した型に置き換えることを推奨。
 */

export type TaskStatus = "todo" | "in_progress" | "done";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface Tag {
  id: string;
  name: string;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
  page: number;
  per_page: number;
}
