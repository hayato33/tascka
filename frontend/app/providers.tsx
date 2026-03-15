/**
 * アプリケーション全体のProvider設定。
 *
 * "use client" が必要な理由:
 * TanStack Query の QueryClientProvider は React の Context API を使っており、
 * Context API は Client Component でしか使えない。
 * Next.js App Router では、デフォルトですべてのコンポーネントが Server Component なので、
 * Context を使うコンポーネントには明示的に "use client" を付ける必要がある。
 *
 * なぜ providers.tsx を layout.tsx から分離するのか:
 * layout.tsx 自体は Server Component のままにしたい（メタデータ等の処理があるため）。
 * "use client" を付けたProvider部分だけを別ファイルに切り出すことで、
 * layout.tsx の Server Component としての恩恵を保ちつつ、
 * Client Component に必要な Provider を提供できる。
 */
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  // QueryClient を useState で初期化するのは、
  // Server Side Rendering 時に複数のリクエスト間で
  // QueryClient が共有されるのを防ぐため。
  // useState を使うことで、クライアントごとに独立した QueryClient が生成される。
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // staleTime: データが「古い」と見なされるまでの時間（ミリ秒）。
            // この間はキャッシュから即座にデータを返し、バックグラウンドで再取得しない。
            staleTime: 60 * 1000,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
