
const API_BASE_URL = 'http://127.0.0.1:8000'
const TOKEN_KEY = 'fraudlens_access_token'

/* =========================
   Authentication utilities
========================= */

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

/* =========================
   API request handler
========================= */

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

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
    })
  } catch {
    throw new Error(
      'Cannot connect to the FraudLens API. Ensure the backend is running at http://127.0.0.1:8000.',
    )
  }

  const data: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      clearToken()
    }

    let message = `Request failed (${response.status})`

    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data
    ) {
      const detail = data.detail

      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        message = detail
          .map((item: unknown) => {
            if (
              typeof item === 'object' &&
              item !== null &&
              'msg' in item &&
              typeof item.msg === 'string'
            ) {
              return item.msg
            }

            return JSON.stringify(item)
          })
          .join('; ')
      }
    }

    throw new Error(message)
  }

  return data as T
}

/* =========================
   Transaction types
========================= */

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

/* =========================
   Investigation types
========================= */

export interface TransactionProfileField {
  key: string
  label: string
  category: string
  value: string | number | boolean | null
  available: boolean
}

export interface InvestigationDataQuality {
  total_fields: number
  available_fields: number
  missing_fields: number
  completeness_percent: number
  missing_field_labels: string[]
}

export interface FeatureContribution {
  key: string
  label: string
  value: string | number | boolean | null
  contribution: number
}

export interface FeatureContributions {
  method: string
  unit: string
  intercept: number
  calculated_logit: number
  probability_logit: number
  contribution_sum: number
  consistency_check: boolean
  increases_risk: FeatureContribution[]
  decreases_risk: FeatureContribution[]
  all_contributions: FeatureContribution[]
}

export interface InvestigationDetails {
  status: string
  observations: string[]
  explanation: string
  recommendation: string
  transaction_profile: TransactionProfileField[]
  data_quality: InvestigationDataQuality
  limitations: string[]
  feature_contributions?: FeatureContributions
}

export interface Investigation extends Transaction {
  threshold: number
  investigation: InvestigationDetails
}

/* =========================
   Authentication types
========================= */

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

/* =========================
   Authentication functions
========================= */

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
    throw new Error(
      'No active session was returned. Confirm your email and try again.',
    )
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

/* =========================
   Public fraud feed
========================= */

export async function fetchPublicFeed(
  limit = 8,
): Promise<FeedResponse> {
  return request<FeedResponse>(
    `/public/feed?limit=${limit}`,
  )
}

/* =========================
   Transaction explorer
========================= */

export async function fetchTransactions(
  limit = 20,
  offset = 0,
): Promise<TransactionsResponse> {
  return request<TransactionsResponse>(
    `/transactions?limit=${limit}&offset=${offset}`,
    {},
    true,
  )
}

/* =========================
   Fraud investigation
========================= */

export async function fetchInvestigation(
  id: number,
): Promise<Investigation> {
  return request<Investigation>(
    `/investigate/${encodeURIComponent(id)}`,
    {},
    true,
  )
}
