// lib/services/auth.ts
export interface LoginResult {
  employeeId: string;
  grade: string;
  isAdmin: boolean;
  redirectPath: string;
}

// パスワード忘れたページで使用する施設オプションの型
export interface FacilityOption {
  value: string;
  label: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  // 開発中に気付きやすくするため
  // eslint-disable-next-line no-console
  console.warn(
    'NEXT_PUBLIC_API_BASE_URL is not set. Please define it in .env.local.',
  );
}

export async function login(
  employeeCode: string,
  password: string,
): Promise<LoginResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ employeeCode, password }),
  });

  if (!res.ok) {
    throw new Error('Login failed');
  }

  return (await res.json()) as LoginResult;
}

export async function logout(): Promise<void> {
  await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include", // Cookie を送るために必須
  })
}


export async function fetchFacilities(): Promise<FacilityOption[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/facilities`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error('Failed to fetch facilities');
  }

  return (await res.json()) as FacilityOption[];
}
