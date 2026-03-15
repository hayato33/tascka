/**
 * API通信の共通関数。
 *
 * fetch API は 4xx/5xx レスポンスを受け取ってもエラーを throw しない。
 * response.ok が false になるだけなので、手動でエラーハンドリングが必要。
 * この共通関数で fetch をラップし、4xx/5xx の場合は自動的にエラーを throw する。
 *
 * なぜ axios ではなく fetch を使うのか:
 * - Next.js は fetch を拡張してキャッシュ機能を追加している
 * - ブラウザ標準APIなのでバンドルサイズが増えない
 * - 学習目的として、低レベルAPIの理解を深められる
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * APIリクエストを送信する共通関数。
 *
 * @param path - APIのパス（例: "/api/tasks"）
 * @param options - fetch のオプション（method, body 等）
 * @returns レスポンスのJSON
 * @throws Error - 4xx/5xx レスポンスの場合
 */
export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  // options を先にスプレッドし、headers を後からマージする。
  // これにより、呼び出し元が指定した method や body が正しく適用され、
  // かつ headers も上書きではなくマージされる。
  const { headers: optionHeaders, ...restOptions } = options ?? {};
  const response = await fetch(url, {
    ...restOptions,
    headers: {
      "Content-Type": "application/json",
      ...optionHeaders,
    },
  });

  // response.ok は HTTP ステータスコードが 200-299 の場合に true。
  // 4xx/5xx の場合は false になるので、エラーとして throw する。
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `API Error: ${response.status} ${response.statusText} - ${errorBody}`,
    );
  }

  // 204 No Content の場合はボディがないので、パースせずに返す。
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
