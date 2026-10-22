
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BadgeCheck,
  ChevronLeft,
  ChevronRight,
  CircleAlert,
  Command,
  Database,
  Eye,
  EyeOff,
  Fingerprint,
  Gauge,
  Layers3,
  LoaderCircle,
  LogOut,
  Menu,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  X,
  Zap,
} from 'lucide-react'
import {
  clearToken,
  currentUser,
  fetchInvestigation,
  fetchTransactions,
  getToken,
  login,
  register,
  type Investigation,
  type Transaction,
  type AuthUser,
} from './api'
import './index.css'

type User = AuthUser

type Page = 'overview' | 'transactions' | 'investigations'
type AuthMode = 'login' | 'register'

const money = (amount: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(amount)

const shortId = (id: number) => `TX-${String(id).slice(-7)}`
const initials = (email: string) => email.slice(0, 1).toUpperCase()

function Brand({ mini = false }: { mini?: boolean }) {
  return (
    <div className="brand">
      <span className="brand-mark">
        <ShieldCheck size={20} />
      </span>
      <span>
        FraudLens
        {!mini && <small>RISK INTELLIGENCE</small>}
      </span>
    </div>
  )
}

function Orb() {
  return (
    <div className="orb-scene" aria-hidden="true">
      <div className="orb-halo" />
      <div className="orb-ring orb-ring-one" />
      <div className="orb-ring orb-ring-two" />
      <div className="orb-ring orb-ring-three" />
      <div className="orb-core">
        <div className="orb-shine" />
        <div className="orb-grid" />
        <div className="orb-continent" />
      </div>
      <i className="orb-node node-one" />
      <i className="orb-node node-two" />
      <i className="orb-node node-three" />
      <div className="orb-caption">
        <span className="status-dot" />
        RISK SIGNALS / MODEL INFERENCE
      </div>
    </div>
  )
}

function RiskChip({ tx }: { tx: Pick<Transaction, 'prediction' | 'risk_score'> }) {
  const high = tx.prediction === 'fraud'

  return (
    <span className={`risk-chip ${high ? 'risk-high' : 'risk-low'}`}>
      <span />
      {high ? 'REVIEW' : 'LOW RISK'}
    </span>
  )
}

/* PUBLIC LANDING PAGE */

function Landing({ onAuth }: { onAuth: (mode: AuthMode) => void }) {
  return (
    <main className="landing">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <header className="site-header">
        <a href="#" aria-label="FraudLens home">
          <Brand />
        </a>

        <nav className="nav-links" aria-label="Main navigation">
          <a href="#capabilities">Capabilities</a>
          <a href="#methodology">Methodology</a>
        </nav>

        <div className="header-actions">
          <button className="button button-quiet" onClick={() => onAuth('login')}>
            Sign in
          </button>
          <button
            className="button button-primary header-action"
            onClick={() => onAuth('register')}
          >
            Open workspace <ArrowRight size={14} />
          </button>
        </div>
      </header>

      <section className="hero page-width">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="eyebrow-line" />
            FRAUD INVESTIGATION / RISK INTELLIGENCE
          </div>

          <h1>
            See the signal.
            <br />
            Understand the <span className="accent-word">risk.</span>
          </h1>

          <p className="hero-description">
            A focused workspace for transaction risk scoring, review
            prioritisation, and structured investigation—built to make
            model output easier to inspect.
          </p>

          <div className="hero-actions">
            <button
              className="button button-primary button-large"
              onClick={() => onAuth('register')}
            >
              Enter the workspace <ArrowRight size={16} />
            </button>
            <button
              className="button button-outline button-large"
              onClick={() => onAuth('login')}
            >
              Explore workspace <ArrowRight size={16} />
            </button>
          </div>

          <div className="hero-proof">
            <span><ShieldCheck size={14} /> Explainable review workflow</span>
            <span><Database size={14} /> IEEE-CIS dataset</span>
            <span><Fingerprint size={14} /> Protected workspace</span>
          </div>
        </div>

        <div className="hero-visual">
          <Orb />
          <div className="floating-stat stat-top">
            <span>INFERENCE ENGINE</span>
            <strong><span className="status-dot" /> MODEL ONLINE</strong>
            <small>Baseline classifier · threshold 0.50</small>
          </div>
          <div className="floating-stat stat-bottom">
            <span>INVESTIGATION MODE</span>
            <strong>Risk <span>→</span> Evidence</strong>
            <small>Score · observations · review status</small>
          </div>
        </div>
      </section>

      <section className="page-width metrics-strip" aria-label="Dataset and model metrics">
        <div><span>590,540</span><small>HISTORICAL TRANSACTIONS</small></div>
        <div><span>3.50%</span><small>DATASET FRAUD PREVALENCE</small></div>
        <div><span>0.7772</span><small>BASELINE ROC-AUC</small></div>
        <div><span>0.1314</span><small>BASELINE AVERAGE PRECISION</small></div>
        <p>
          Dataset and baseline validation figures. They are not live banking
          statistics or production service-level guarantees.
        </p>
      </section>

      <section id="capabilities" className="page-width capabilities">
        <div className="section-heading">
          <div>
            <div className="eyebrow">
              <span className="eyebrow-line" />
              BUILT FOR INSPECTION
            </div>
            <h2>From score to review.</h2>
          </div>
          <p>
            One coherent workflow from the first risk signal to a traceable,
            structured investigation view.
          </p>
        </div>

        <div className="capability-grid">
          <article className="capability-card">
            <span><Gauge size={20} /></span>
            <small>01 / SCORING</small>
            <h3>Risk prioritisation</h3>
            <p>
              Review model scores and threshold-based flags without
              confusing prediction with ground truth.
            </p>
            <ArrowUpRight className="card-arrow" />
          </article>

          <article className="capability-card">
            <span><Layers3 size={20} /></span>
            <small>02 / INVESTIGATION</small>
            <h3>Structured evidence</h3>
            <p>
              Inspect transaction attributes, missing-data observations,
              score, and review status in one place.
            </p>
            <ArrowUpRight className="card-arrow" />
          </article>

          <article className="capability-card">
            <span><Shield size={20} /></span>
            <small>03 / ACCESS</small>
            <h3>Protected workspace</h3>
            <p>
              Sign-in is required for the transaction explorer and
              individual investigation endpoint.
            </p>
            <ArrowUpRight className="card-arrow" />
          </article>
        </div>
      </section>

      <section id="methodology" className="page-width methodology-section">
        <div className="eyebrow">
          <span className="eyebrow-line" />
          HOW FRAUDLENS WORKS
        </div>
        <h2>From transaction to investigation.</h2>
        <p className="methodology-intro">
          Historical transaction data is prepared, scored by a baseline
          classifier, and presented for analyst review. Flagged transactions
          can then be inspected through a structured investigation view.
        </p>

        <div className="methodology-steps">
          <article>
            <span>01</span>
            <h3>Transaction data</h3>
            <p>IEEE-CIS historical transaction records provide the input data.</p>
          </article>
          <article>
            <span>02</span>
            <h3>Model scoring</h3>
            <p>A baseline classifier assigns a risk score to each transaction.</p>
          </article>
          <article>
            <span>03</span>
            <h3>Risk review</h3>
            <p>Threshold-based flags help prioritise transactions for human review.</p>
          </article>
          <article>
            <span>04</span>
            <h3>Evidence inspection</h3>
            <p>Inspect transaction attributes and data observations for context.</p>
          </article>
        </div>

        <p className="methodology-disclaimer">
          Model scores are not proof of fraud. The current baseline does not
          establish causal explanations for individual predictions.
        </p>
      </section>

      <footer className="page-width site-footer">
        <span className="brand-mini"><ShieldCheck size={15} /> FraudLens</span>
        <span>Academic prototype · historical dataset replay</span>
        <span>Not connected to live financial institutions</span>
      </footer>
    </main>
  )
}

/* LOGIN AND REGISTRATION */

function AuthPage({
  initialMode,
  onSuccess,
  onBack,
}: {
  initialMode: AuthMode
  onSuccess: (user: User) => void
  onBack: () => void
}) {
  const [mode, setMode] = useState<AuthMode>(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [confirmation, setConfirmation] = useState('')

  useEffect(() => {
    setMode(initialMode)
    setError('')
    setConfirmation('')
  }, [initialMode])

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setConfirmation('')
    setBusy(true)

    try {
      if (mode === 'register') {
        const result = await register(email.trim(), password)

        if (result.confirmationRequired) {
          setConfirmation(
            result.message ||
              `A confirmation email has been requested for ${email.trim()}. Check your inbox and spam folder, then confirm your address before signing in.`,
          )
          setPassword('')
          return
        }

        // Some Supabase configurations allow registration without email
        // confirmation. In that case, continue only if a session exists.
        if (!getToken()) {
          setConfirmation(
            'Your registration was received. Check your email for a confirmation link, then return here and sign in.',
          )
          setPassword('')
          return
        }

        onSuccess(result.user)
        return
      }

      const user = await login(email.trim(), password)
      onSuccess(user)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  if (confirmation) {
    return (
      <main className="auth-page">
        <div className="auth-backdrop" />

        <button className="auth-back" onClick={onBack}>
          <ChevronLeft size={15} /> Back to overview
        </button>

        <div className="auth-layout">
          <div className="auth-brand-side">
            <Brand />
            <div className="eyebrow" style={{ marginTop: 48 }}>
              <span className="eyebrow-line" />
              EMAIL VERIFICATION
            </div>
            <h1>
              One step
              <br />
              <span className="accent-word">remaining.</span>
            </h1>
            <p>
              Confirm your email address before accessing the FraudLens
              analyst workspace.
            </p>
            <div className="auth-assurance">
              <ShieldCheck size={23} />
              <span>
                <strong>Protected access</strong>
                <small>Supabase authentication</small>
              </span>
            </div>
            <Orb />
          </div>

          <section className="auth-card">
            <div className="auth-card-top">
              <span className="brand-mark"><BadgeCheck size={17} /></span>
              EMAIL CONFIRMATION
            </div>

            <h2>Check your inbox</h2>
            <p className="auth-subtitle">
              Registration has been received for <strong>{email.trim()}</strong>.
            </p>

            <div className="form-success" role="status">
              <BadgeCheck size={18} />
              <span>{confirmation}</span>
            </div>

            <p className="auth-legal">
              Open the confirmation link sent by Supabase. Once your email
              is confirmed, return here and sign in with your email and
              password. Registration alone does not open the dashboard.
            </p>

            <button
              className="button button-primary auth-submit"
              onClick={() => {
                setMode('login')
                setConfirmation('')
                setError('')
                setPassword('')
              }}
            >
              Continue to sign in <ArrowRight size={15} />
            </button>

            <button
              className="button button-outline auth-submit"
              onClick={onBack}
              style={{ marginTop: 10 }}
            >
              Back to overview
            </button>
          </section>
        </div>
      </main>
    )
  }

  return (
    <main className="auth-page">
      <div className="auth-backdrop" />

      <button className="auth-back" onClick={onBack}>
        <ChevronLeft size={15} /> Back to overview
      </button>

      <div className="auth-layout">
        <div className="auth-brand-side">
          <Brand />

          <div className="eyebrow" style={{ marginTop: 48 }}>
            <span className="eyebrow-line" />
            SECURE ANALYST WORKSPACE
          </div>

          <h1>
            Investigate with
            <br />
            <span className="accent-word">clarity.</span>
          </h1>

          <p>
            Access transaction scoring, risk prioritisation, and structured
            investigation details in one focused workspace.
          </p>

          <div className="auth-assurance">
            <ShieldCheck size={23} />
            <span>
              <strong>Protected access</strong>
              <small>Token-authenticated API · Supabase auth</small>
            </span>
          </div>

          <Orb />
        </div>

        <section className="auth-card">
          <div className="auth-card-top">
            <span className="brand-mark"><Command size={17} /></span>
            FRAUDLENS ACCESS
          </div>

          <h2>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>

          <p className="auth-subtitle">
            {mode === 'login'
              ? 'Sign in to continue to your workspace.'
              : 'Register to open your analyst workspace.'}
          </p>

          <div className="auth-tabs">
            <button
              type="button"
              className={mode === 'login' ? 'active' : ''}
              onClick={() => {
                setMode('login')
                setError('')
              }}
            >
              Sign in
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'active' : ''}
              onClick={() => {
                setMode('register')
                setError('')
              }}
            >
              Create account
            </button>
          </div>

          <form className="auth-form" onSubmit={submit}>
            <label>
              Email address
              <input
                type="email"
                autoComplete="email"
                value={email}
                onChange={event => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
              />
            </label>

            <label>
              Password
              <div className="password-wrap">
                <input
                  type={showPassword ? 'text' : 'password'}
                  autoComplete={
                    mode === 'login' ? 'current-password' : 'new-password'
                  }
                  minLength={mode === 'register' ? 8 : 1}
                  maxLength={128}
                  value={password}
                  onChange={event => setPassword(event.target.value)}
                  placeholder={
                    mode === 'register'
                      ? 'At least 8 characters'
                      : 'Enter your password'
                  }
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(value => !value)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </label>

            {error && (
              <div className="form-error" role="alert">
                <CircleAlert size={15} />
                {error}
              </div>
            )}

            <button
              className="button button-primary auth-submit"
              type="submit"
              disabled={busy}
            >
              {busy ? (
                <LoaderCircle size={15} className="spin" />
              ) : (
                <ArrowRight size={15} />
              )}
              {busy
                ? 'Please wait…'
                : mode === 'login'
                  ? 'Sign in to workspace'
                  : 'Create account'}
            </button>
          </form>

          <p className="auth-legal">
            Authentication is handled by Supabase. If email confirmation is
            enabled, confirm your email address before signing in.
          </p>
        </section>
      </div>
    </main>
  )
}

/* TRANSACTION INVESTIGATION MODAL */

function InvestigationModal({
  id,
  onClose,
}: {
  id: number
  onClose: () => void
}) {
  const [detail, setDetail] = useState<Investigation | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    fetchInvestigation(id)
      .then(value => {
        if (!cancelled) setDetail(value)
      })
      .catch(e => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Investigation failed')
        }
      })

    return () => {
      cancelled = true
    }
  }, [id])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className="modal-backdrop"
      onMouseDown={event => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <section
        className="investigation-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="investigation-title"
      >
        <div className="modal-heading">
          <div>
            <div className="eyebrow">
              <span className="eyebrow-line" />
              CASE REVIEW
            </div>
            <h2 id="investigation-title">Transaction investigation</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close investigation"
          >
            <X size={16} />
          </button>
        </div>

        <div className="investigation-body">
          {error ? (
            <div className="form-error">
              <CircleAlert size={15} />
              {error}
            </div>
          ) : !detail ? (
            <div className="empty-state">
              <LoaderCircle className="spin" size={18} />
              Loading investigation…
            </div>
          ) : (
            <>
              <div className="investigation-score">
                <div>
                  <span>MODEL RISK SCORE</span>
                  <strong className={detail.risk_score >= 50 ? 'text-alert' : ''}>
                    {detail.risk_score.toFixed(2)}
                    <small>%</small>
                  </strong>
                  <RiskChip tx={detail} />
                </div>
                <div className="score-gauge">
                  <span>{detail.risk_score.toFixed(0)}</span>
                  <small>/100</small>
                </div>
              </div>

              <div className="investigation-facts">
                <div><span>TRANSACTION ID</span><strong>{detail.transaction_id}</strong></div>
                <div><span>AMOUNT</span><strong>{money(detail.amount)}</strong></div>
                <div><span>PRODUCT</span><strong>{detail.product || 'Unknown'}</strong></div>
                <div><span>DECISION THRESHOLD</span><strong>{(detail.threshold * 100).toFixed(0)}%</strong></div>
              </div>

              <div className="explanation-block">
                <h3><Sparkles size={15} /> Model interpretation</h3>
                <p>{detail.investigation.explanation}</p>
              </div>

              <div className="observation-block">
                <h3><Layers3 size={15} /> Data observations</h3>
                {detail.investigation.observations.length ? (
                  detail.investigation.observations.map(item => (
                    <div className="observation-row" key={item}>
                      <span><CircleAlert size={12} /></span>
                      {item}
                    </div>
                  ))
                ) : (
                  <p>No missingness observations from the selected fields.</p>
                )}
              </div>

              <p className="modal-disclaimer">
                A score above the configured threshold is a review flag,
                not proof of fraud. The baseline does not provide causal
                feature attribution.
              </p>
            </>
          )}
        </div>
      </section>
    </div>
  )
}

/* AUTHENTICATED DASHBOARD */

function Dashboard({
  user,
  onLogout,
}: {
  user: User
  onLogout: () => void
}) {
  const [page, setPage] = useState<Page>('overview')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<number | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const load = useCallback(async (nextOffset = offset) => {
    setLoading(true)
    setError('')

    try {
      const result = await fetchTransactions(20, nextOffset)
      setTransactions(result.transactions)
      setTotal(result.total)
      setOffset(nextOffset)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load transactions')
    } finally {
      setLoading(false)
    }
  }, [offset])

  useEffect(() => {
    void load(0)
    // Initial data load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const filtered = useMemo(
    () => transactions.filter(tx => String(tx.transaction_id).includes(search.trim())),
    [transactions, search],
  )

  const flagged = transactions.filter(tx => tx.prediction === 'fraud').length

  const averageRisk = transactions.length
    ? transactions.reduce((sum, tx) => sum + tx.risk_score, 0) / transactions.length
    : 0

  const openPage = (next: Page) => {
    setPage(next)
    setSidebarOpen(false)
  }

  return (
    <div className="dashboard-shell">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand"><Brand /></div>
        <p className="side-label">WORKSPACE</p>

        <button
          className={`side-link ${page === 'overview' ? 'active' : ''}`}
          onClick={() => openPage('overview')}
        >
          <Gauge size={16} /> Overview
          {page === 'overview' && <i className="side-active-mark" />}
        </button>

        <button
          className={`side-link ${page === 'transactions' ? 'active' : ''}`}
          onClick={() => openPage('transactions')}
        >
          <Database size={16} /> Transaction explorer
          {page === 'transactions' && <i className="side-active-mark" />}
        </button>

        <button
          className={`side-link ${page === 'investigations' ? 'active' : ''}`}
          onClick={() => openPage('investigations')}
        >
          <ShieldAlert size={16} /> Investigations
          {page === 'investigations' && <i className="side-active-mark" />}
        </button>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="status-dot" />
            <span><strong>API SERVICE</strong><small>Local prototype</small></span>
          </div>

          <div className="sidebar-user">
            <span className="avatar">{initials(user.email)}</span>
            <span className="user-meta">
              <strong>{user.email}</strong>
              <small>Analyst session</small>
            </span>
            <button
              className="icon-button"
              onClick={onLogout}
              title="Sign out"
              aria-label="Sign out"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              className="icon-button mobile-menu"
              onClick={() => setSidebarOpen(value => !value)}
              aria-label="Toggle navigation"
            >
              <Menu size={16} />
            </button>
            <div className="breadcrumb">
              FraudLens <ChevronRight size={12} />{' '}
              <strong>
                {page === 'overview'
                  ? 'Overview'
                  : page === 'transactions'
                    ? 'Transaction explorer'
                    : 'Investigations'}
              </strong>
            </div>
          </div>

          <div className="topbar-right">
            <span className="replay-badge"><span className="status-dot" /> HISTORICAL REPLAY</span>
            <span className="top-avatar">{initials(user.email)}</span>
          </div>
        </header>

        <div className="dashboard-content">
          <div className="dashboard-welcome">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                RISK INTELLIGENCE / WORKSPACE
              </div>
              <h1>
                {page === 'overview'
                  ? 'Good to have you back.'
                  : page === 'transactions'
                    ? 'Transaction explorer.'
                    : 'Investigation queue.'}
              </h1>
              <p>
                {page === 'overview'
                  ? 'Review model-scored transactions and inspect the signals that need attention.'
                  : page === 'transactions'
                    ? 'Search the currently loaded page and open a transaction for investigation.'
                    : 'Open any transaction to inspect its score and data observations.'}
              </p>
            </div>

            <button className="button button-outline" onClick={() => void load(offset)}>
              <RefreshCw size={14} className={loading ? 'spin' : ''} />
              Refresh data
            </button>
          </div>

          {error && (
            <div className="dashboard-error">
              <CircleAlert size={16} />
              {error}
              <button onClick={() => void load(offset)}>Retry</button>
            </div>
          )}

          {page === 'overview' && (
            <div className="dashboard-stat-grid">
              <article className="dash-stat">
                <div className="dash-stat-head">
                  DATASET TRANSACTIONS
                  <span className="stat-symbol"><Database size={15} /></span>
                </div>
                <strong>{total.toLocaleString()}</strong>
                <div className="dash-stat-foot">
                  <span className="stat-foot-icon"><BadgeCheck size={12} /></span>
                  Loaded historical dataset size
                </div>
                <Database className="stat-watermark" size={70} />
              </article>

              <article className="dash-stat">
                <div className="dash-stat-head">
                  FLAGGED ON THIS PAGE
                  <span className="stat-symbol alert-symbol"><ShieldAlert size={15} /></span>
                </div>
                <strong>{flagged}<small> / {transactions.length}</small></strong>
                <div className="dash-stat-foot"><span className="stat-foot-alert">THRESHOLD ≥ 50%</span></div>
                <div className="stat-ring">
                  <span>
                    {transactions.length ? Math.round((flagged / transactions.length) * 100) : 0}%
                  </span>
                </div>
              </article>

              <article className="dash-stat">
                <div className="dash-stat-head">
                  MEAN PAGE RISK
                  <span className="stat-symbol"><Activity size={15} /></span>
                </div>
                <strong>{averageRisk.toFixed(2)}<small>%</small></strong>
                <div className="dash-stat-foot">Mean model score of loaded rows</div>
                <div className="mini-bars">
                  {[13, 22, 17, 27, 19, 29, 23, 16, 26].map((height, i) => (
                    <i key={i} style={{ height }} />
                  ))}
                </div>
              </article>

              <article className="dash-stat">
                <div className="dash-stat-head">
                  MODEL VALIDATION
                  <span className="stat-symbol"><Zap size={15} /></span>
                </div>
                <strong>0.7772</strong>
                <div className="dash-stat-foot">ROC-AUC · held-out validation</div>
                <div className="risk-track"><i style={{ width: '77.72%' }} /></div>
              </article>
            </div>
          )}

          <section className="table-panel">
            <div className="table-panel-head">
              <div>
                <div className="eyebrow">
                  <span className="eyebrow-line" />
                  {page === 'investigations' ? 'REVIEW QUEUE' : 'TRANSACTION DATA'}
                </div>
                <h2>
                  {page === 'investigations' ? 'Flagged transactions' : 'Recent transactions'}{' '}
                  <span>{filtered.filter(tx => page !== 'investigations' || tx.prediction === 'fraud').length}</span>
                </h2>
                <p>Scores are model outputs; review flags are not confirmed fraud labels.</p>
              </div>

              <div className="table-tools">
                <label className="search-box">
                  <Search size={14} />
                  <input
                    value={search}
                    onChange={event => setSearch(event.target.value)}
                    placeholder="Search transaction ID"
                  />
                </label>
              </div>
            </div>

            <div className="table-scroll">
              <table className="transaction-table">
                <thead>
                  <tr>
                    <th>TRANSACTION</th>
                    <th>AMOUNT</th>
                    <th>PRODUCT</th>
                    <th>MODEL RISK</th>
                    <th>STATUS</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {loading && !transactions.length ? (
                    <tr>
                      <td colSpan={6}>
                        <div className="empty-state">
                          <LoaderCircle className="spin" size={17} />
                          Loading transactions…
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filtered
                      .filter(tx => page !== 'investigations' || tx.prediction === 'fraud')
                      .map(tx => (
                        <tr
                          key={tx.transaction_id}
                          onClick={() => setSelected(tx.transaction_id)}
                        >
                          <td>
                            <span className="transaction-id">
                              <i className="tx-dot" />
                              {shortId(tx.transaction_id)}
                            </span>
                          </td>
                          <td className="amount-cell">{money(tx.amount)}</td>
                          <td><span className="product-pill">{tx.product || '—'}</span></td>
                          <td>
                            <div className="risk-cell">
                              <strong className={tx.risk_score >= 50 ? 'text-alert' : ''}>
                                {tx.risk_score.toFixed(2)}%
                              </strong>
                              <span className="risk-bar">
                                <i
                                  className={tx.risk_score >= 50 ? 'bar-high' : ''}
                                  style={{ width: `${Math.min(tx.risk_score, 100)}%` }}
                                />
                              </span>
                            </div>
                          </td>
                          <td><RiskChip tx={tx} /></td>
                          <td>
                            <button
                              className="row-open"
                              aria-label={`Investigate ${tx.transaction_id}`}
                              onClick={event => {
                                event.stopPropagation()
                                setSelected(tx.transaction_id)
                              }}
                            >
                              <ArrowUpRight size={14} />
                            </button>
                          </td>
                        </tr>
                      ))
                  )}
                </tbody>
              </table>

              {!loading && !error && filtered.filter(
                tx => page !== 'investigations' || tx.prediction === 'fraud',
              ).length === 0 && (
                <div className="empty-state">No matching transactions on this page.</div>
              )}
            </div>

            <div className="table-footer">
              <span>
                {total
                  ? `${offset + 1}–${Math.min(offset + transactions.length, total)} of ${total.toLocaleString()} transactions`
                  : 'No transactions loaded'}
              </span>
              <span style={{ display: 'flex', gap: 8 }}>
                <button
                  className="icon-button"
                  disabled={offset <= 0 || loading}
                  onClick={() => void load(Math.max(0, offset - 20))}
                  aria-label="Previous page"
                >
                  <ChevronLeft size={14} />
                </button>
                <button
                  className="icon-button"
                  disabled={offset + 20 >= total || loading}
                  onClick={() => void load(offset + 20)}
                  aria-label="Next page"
                >
                  <ChevronRight size={14} />
                </button>
              </span>
            </div>
          </section>

          <div className="dashboard-note">
            <ShieldCheck size={16} />
            <div>
              <strong>Prototype limitation.</strong> The dashboard scores a
              historical IEEE-CIS dataset slice. A threshold-based model flag
              is not proof of fraud, and the baseline explanation reports
              data observations rather than causal feature attribution.
            </div>
          </div>
        </div>
      </main>

      {selected !== null && (
        <InvestigationModal id={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}

/* APPLICATION ENTRY POINT AND SESSION CHECK */

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [authMode, setAuthMode] = useState<AuthMode | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)

  useEffect(() => {
    let cancelled = false

    if (!getToken()) {
      setCheckingSession(false)
      return
    }

    currentUser()
      .then(value => {
        if (!cancelled) setUser(value)
      })
      .catch(() => {
        clearToken()
      })
      .finally(() => {
        if (!cancelled) setCheckingSession(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const logout = () => {
    clearToken()
    setUser(null)
    setAuthMode(null)
  }

  if (checkingSession) {
    return (
      <div className="app-loading">
        <span className="brand-mark"><ShieldCheck size={20} /></span>
        <span>Loading FraudLens…</span>
      </div>
    )
  }

  if (user) {
    return <Dashboard user={user} onLogout={logout} />
  }

  if (authMode) {
    return (
      <AuthPage
        initialMode={authMode}
        onSuccess={setUser}
        onBack={() => setAuthMode(null)}
      />
    )
  }

  return <Landing onAuth={setAuthMode} />
}
