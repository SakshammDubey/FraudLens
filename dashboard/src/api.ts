
const API_BASE_URL = 'http://127.0.0.1:8000'
const TOKEN_KEY = 'fraudlens_access_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  authenticated = false,
): Promise<T> {
  const headers = new Headers(init.headers)

  if (init.body) {
    headers.set('Content-Type', 'application/json')
  }

  if (authenticated) {
    const token = getToken()

    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      clearToken()
    }

    throw new Error(
      data.detail || `Request failed (${response.status})`,
    )
  }

  return data as T
}

export interface Transaction {
  transaction_id: number
  amount: number
  product: string | null
  transaction_dt: number
  fraud_probability: number
  risk_score: number
  prediction: 'fraud' | 'legitimate'
}

export interface FeedResponse {
  mode: string
  label: string
  events: Transaction[]
}

export interface TransactionsResponse {
  total: number
  count: number
  offset: number
  transactions: Transaction[]
}

export interface Investigation extends Transaction {
  threshold: number
  investigation: {
    status: string
    observations: string[]
    explanation: string
  }
}

export interface AuthUser {
  id: string
  email: string
}

export interface AuthResponse {
  access_token?: string
  token_type?: string
  user: AuthUser
  confirmation_required?: boolean
  message?: string
}

export interface RegistrationResult {
  confirmationRequired: boolean
  message: string
  user: AuthUser
}

function saveSessionIfPresent(result: AuthResponse): void {
  if (result.access_token) {
    saveToken(result.access_token)
  } else {
    clearToken()
  }
}

export async function register(
  email: string,
  password: string,
): Promise<RegistrationResult> {
  const result = await request<AuthResponse>(
    '/auth/register',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    },
  )

  saveSessionIfPresent(result)

  return {
    confirmationRequired: result.confirmation_required ?? false,
    message: result.message ?? 'Registration completed.',
    user: result.user,
  }
}

export async function login(
  email: string,
  password: string,
): Promise<AuthUser> {
  const result = await request<AuthResponse>(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    },
  )

  if (!result.access_token) {
    throw new Error('No active session was returned. Confirm your email and try again.')
  }

  saveToken(result.access_token)
  return result.user
}

export async function currentUser(): Promise<AuthUser> {
  const result = await request<{ user: AuthUser }>(
    '/auth/me',
    {},
    true,
  )

  return result.user
}

export async function fetchPublicFeed(limit = 8) {
  return request<FeedResponse>(
    `/public/feed?limit=${limit}`,
  )
}

export async function fetchTransactions(
  limit = 20,
  offset = 0,
) {
  return request<TransactionsResponse>(
    `/transactions?limit=${limit}&offset=${offset}`,
    {},
    true,
  )
}

export async function fetchInvestigation(id: number) {
  return request<Investigation>(
    `/investigate/${id}`,
    {},
    true,
  )
}
