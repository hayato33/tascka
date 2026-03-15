/**
 * タスク作成・編集フォームコンポーネント。
 *
 * React Hook Form + Zod でフォームのバリデーションを行う。
 *
 * なぜ React Hook Form を使うのか:
 * - 非制御コンポーネント（ref ベース）のため、再レンダリングが最小限
 * - Zod と組み合わせることで、型安全なバリデーションが実現できる
 * - zodResolver がバリデーションスキーマと useForm を接続する
 *
 * "use client" が必要な理由:
 * useForm はReactのHookなので、Client Componentでしか使えない。
 */
"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

// バリデーションスキーマ。
// バックエンドの Pydantic スキーマ（TaskCreate）と対応させる。
// フロントエンドでもバリデーションすることで、
// 不正なリクエストをバックエンドに送る前にブロックできる。
const taskSchema = z.object({
  title: z
    .string()
    .min(1, "タイトルは必須です")
    .max(255, "タイトルは255文字以内です"),
  description: z.string().nullable().optional(),
  status: z.enum(["todo", "in_progress", "done"]).default("todo"),
});

type TaskFormValues = z.infer<typeof taskSchema>;

interface TaskFormProps {
  defaultValues?: Partial<TaskFormValues>;
  onSubmit: (data: TaskFormValues) => void;
  isSubmitting?: boolean;
}

export function TaskForm({
  defaultValues,
  onSubmit,
  isSubmitting = false,
}: TaskFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormValues>({
    // zodResolver で Zod スキーマを useForm のバリデーションとして使う。
    // これにより、フォームの送信時に自動的にバリデーションが実行される。
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: "",
      description: null,
      status: "todo",
      ...defaultValues,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700"
        >
          タイトル
        </label>
        <input
          id="title"
          type="text"
          {...register("title")}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700"
        >
          説明
        </label>
        <textarea
          id="description"
          {...register("description")}
          rows={3}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label
          htmlFor="status"
          className="block text-sm font-medium text-gray-700"
        >
          ステータス
        </label>
        <select
          id="status"
          {...register("status")}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="todo">未着手</option>
          <option value="in_progress">進行中</option>
          <option value="done">完了</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? "送信中..." : "保存"}
      </button>
    </form>
  );
}
