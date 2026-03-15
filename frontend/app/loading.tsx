/**
 * ローディングUI。
 *
 * Next.js App Router では、loading.tsx を配置すると、
 * そのディレクトリ以下のページが読み込み中の間、自動的にこのコンポーネントが表示される。
 * React の Suspense 境界として機能し、TanStack Query の useSuspenseQuery と連携する。
 */

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-lg text-gray-500">読み込み中...</div>
    </div>
  );
}
