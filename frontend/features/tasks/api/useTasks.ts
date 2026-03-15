/**
 * タスク関連のTanStack Query Hooks。
 *
 * TanStack Query（旧React Query）は、サーバーデータの取得・キャッシュ・
 * 同期を管理するライブラリ。useQuery でデータを取得し、useMutation で
 * データを変更する。
 *
 * queryKey の設計方針:
 * - ["tasks"] → タスク一覧
 * - ["tasks", id] → タスク詳細
 * - queryKey が同じリクエストはキャッシュを共有する
 * - invalidateQueries(["tasks"]) でタスク関連のキャッシュをすべて無効化できる
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";

// TODO: openapi-typescript で生成した型に置き換える
interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  status: "todo" | "in_progress" | "done";
  created_at: string;
  updated_at: string;
  tags: TagResponse[];
}

interface TagResponse {
  id: string;
  name: string;
}

interface TaskListResponse {
  items: TaskResponse[];
  total: number;
  page: number;
  per_page: number;
}

interface TaskCreateInput {
  title: string;
  description?: string | null;
  status?: "todo" | "in_progress" | "done";
  tag_ids?: string[];
}

interface TaskUpdateInput {
  title?: string;
  description?: string | null;
  status?: "todo" | "in_progress" | "done";
  tag_ids?: string[];
}

/**
 * タスク一覧を取得するHook。
 */
export function useTasks(params?: {
  status?: string;
  tag?: string;
  page?: number;
  per_page?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params?.status != null) searchParams.set("status", params.status);
  if (params?.tag != null) searchParams.set("tag", params.tag);
  if (params?.page != null) searchParams.set("page", String(params.page));
  if (params?.per_page != null)
    searchParams.set("per_page", String(params.per_page));

  const queryString = searchParams.toString();
  const path = `/api/tasks${queryString ? `?${queryString}` : ""}`;

  return useQuery({
    // queryKey にパラメータを含めることで、パラメータが変わるたびに
    // 新しいクエリとしてデータを再取得する。
    queryKey: ["tasks", params],
    queryFn: () => apiFetch<TaskListResponse>(path),
  });
}

/**
 * タスク詳細を取得するHook。
 */
export function useTask(taskId: string) {
  return useQuery({
    queryKey: ["tasks", taskId],
    queryFn: () => apiFetch<TaskResponse>(`/api/tasks/${taskId}`),
    // enabled: タスクIDが存在する場合のみクエリを実行する。
    // これにより、IDが未確定の状態での不要なリクエストを防ぐ。
    enabled: !!taskId,
  });
}

/**
 * タスクを作成するHook。
 *
 * useMutation は副作用（データの作成・更新・削除）を管理する。
 * 成功後に invalidateQueries でキャッシュを無効化し、
 * 一覧を自動的に再取得させる。
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreateInput) =>
      apiFetch<TaskResponse>("/api/tasks", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      // ["tasks"] をキーに持つすべてのクエリのキャッシュを無効化する。
      // これにより、タスク一覧が自動的に再取得される。
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

/**
 * タスクを更新するHook。
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TaskUpdateInput }) =>
      apiFetch<TaskResponse>(`/api/tasks/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

/**
 * タスクを削除するHook。
 */
export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) =>
      apiFetch<void>(`/api/tasks/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
