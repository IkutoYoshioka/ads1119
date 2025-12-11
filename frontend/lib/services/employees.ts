// lib/services/employees.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

// パスワードリセットリクエストを送信する関数(現状、パスワードを忘れた人ページで使用)
export async function requestPasswordReset(
  employeeCode: string,
  facility: string,
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/password-reset/request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ employeeCode, facility }),
  });

  if (!res.ok) {
    // エラー詳細を見たい場合は res.json() してもよい
    throw new Error('Failed to request password reset');
  }
}
