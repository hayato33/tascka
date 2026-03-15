/**
 * タスク詳細・編集ページ。
 *
 * App Router の動的ルート: /tasks/[id] にマッチする。
 * [id] はURLパラメータとして params.id で取得できる。
 * 例: /tasks/abc-123 にアクセスすると params.id = "abc-123" になる。
 */

export default function TaskDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <main className="mx-auto max-w-4xl p-8">
      <h1 className="mb-8 text-2xl font-bold">タスク詳細</h1>
      <p className="text-gray-600">タスクID: {params.id} - 実装中</p>
    </main>
  );
}
