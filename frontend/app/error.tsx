/**
 * エラーUI。
 *
 * Next.js App Router では、error.tsx を配置すると、
 * そのディレクトリ以下でランタイムエラーが発生した際に自動的にこのコンポーネントが表示される。
 * React の Error Boundary として機能する。
 *
 * "use client" が必要な理由:
 * Error Boundary は React のクラスコンポーネントの機能であり、
 * Client Component でしか動作しない。Next.js の error.tsx は
 * 内部的に Error Boundary でラップされるため、"use client" が必須。
 */
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h2 className="text-xl font-semibold text-red-600">
        エラーが発生しました
      </h2>
      <p className="text-gray-600">
        予期しないエラーが発生しました。
        {error.digest && (
          <span className="block text-sm text-gray-400">
            エラーID: {error.digest}
          </span>
        )}
      </p>
      <button
        onClick={reset}
        className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        再試行
      </button>
    </div>
  );
}
