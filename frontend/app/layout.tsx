/**
 * ルートレイアウト。
 *
 * Next.js App Routerでは、layout.tsx はそのディレクトリ以下の
 * すべてのページに共通するUIを定義する。
 * ルートの layout.tsx は必須で、<html> と <body> タグを含む必要がある。
 *
 * ここでは以下を設定する:
 * - グローバルCSS（Tailwind CSS）の読み込み
 * - TanStack Query の Provider 設定
 * - 共通のメタデータ（title等）
 */

import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Tascka",
  description: "タスク管理アプリ",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
