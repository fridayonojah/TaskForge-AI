import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Cpu, Loader2, Plane, Presentation, FileText, Table2, Search,
} from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { cn } from '../../lib/utils'

const FEATURES = [
  {
    icon: Plane,
    label: 'Trip Planner',
    desc: 'Tell it where you\'re going — get real flights, hotels, and a day-by-day plan.',
    gradient: 'from-blue-500/20 to-cyan-500/10',
    border: 'hover:border-blue-500/30',
    iconColor: 'text-blue-400',
    iconBg: 'bg-blue-500/10',
  },
  {
    icon: Presentation,
    label: 'Slide Creator',
    desc: 'Give it a topic — get a structured, ready-to-present deck.',
    gradient: 'from-violet-500/20 to-purple-500/10',
    border: 'hover:border-violet-500/30',
    iconColor: 'text-violet-400',
    iconBg: 'bg-violet-500/10',
  },
  {
    icon: FileText,
    label: 'Resume Polish',
    desc: 'Paste your resume — get a rewrite tailored to the role you want.',
    gradient: 'from-emerald-500/20 to-teal-500/10',
    border: 'hover:border-emerald-500/30',
    iconColor: 'text-emerald-400',
    iconBg: 'bg-emerald-500/10',
  },
  {
    icon: Table2,
    label: 'Sheet Builder',
    desc: 'Describe your data — download a spreadsheet ready to use.',
    gradient: 'from-orange-500/20 to-amber-500/10',
    border: 'hover:border-orange-500/30',
    iconColor: 'text-orange-400',
    iconBg: 'bg-orange-500/10',
  },
  {
    icon: Search,
    label: 'Market Research',
    desc: 'Name an industry — get a concise briefing on trends and key players.',
    gradient: 'from-pink-500/20 to-rose-500/10',
    border: 'hover:border-pink-500/30',
    iconColor: 'text-pink-400',
    iconBg: 'bg-pink-500/10',
  },
]

// Body background (#100e0b) is in index.css — blend modes composite against it.
function AuraBackground() {
  return (
    <>
      <div aria-hidden="true" style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse 120% 145% at 50% -50%, rgba(0,0,0,0) 58%, rgb(240,240,245) 76%, rgba(0,0,0,0) 84%)',
        mixBlendMode: 'screen', filter: 'blur(90px)', opacity: 0.35, transform: 'translateZ(0)',
      }} />
      <div aria-hidden="true" style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse 120% 145% at 50% -50%, rgba(0,0,0,0) 50%, rgba(121,42,242,0.18) 78%, rgba(0,0,0,0) 100%)',
        mixBlendMode: 'screen', filter: 'blur(260px)', transform: 'translateZ(0)',
      }} />
      <div aria-hidden="true" style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse 120% 145% at 50% -50%, rgba(0,0,0,0) 82.5%, #ff007a 83.5%, rgba(0,0,0,0) 84.5%)',
        mixBlendMode: 'lighten', filter: 'blur(43px)', opacity: 0.3, transform: 'translateZ(0)',
      }} />
    </>
  )
}

const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  show: { opacity: 1, y: 0 },
}

const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.09, delayChildren: 0.1 } },
}

export function AuthPage() {
  const { login, register } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e: { preventDefault(): void }) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      mode === 'login' ? await login(email, password) : await register(email, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const AuthForm = (
    <div className="w-full max-w-sm">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <h2 className="mb-1 text-xl font-semibold text-white">
          {mode === 'login' ? 'Welcome back' : 'Create your account'}
        </h2>
        <p className="mb-6 text-sm text-white/35">
          {mode === 'login' ? 'Your workspace is waiting.' : 'Free to start — no card required.'}
        </p>

        <div className="mb-5 flex rounded-xl border border-white/10 bg-white/[0.04] p-1">
          {(['login', 'register'] as const).map((m) => (
            <button key={m} type="button"
              onClick={() => { setMode(m); setError(null) }}
              className={cn(
                'flex-1 rounded-lg py-2 text-sm font-medium transition-all',
                mode === m ? 'bg-white/10 text-white shadow-sm' : 'text-white/35 hover:text-white/60',
              )}>
              {m === 'login' ? 'Sign In' : 'Sign Up'}
            </button>
          ))}
        </div>

        <form onSubmit={submit} className="space-y-3.5">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-white/45">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              required placeholder="you@example.com"
              className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-3.5 py-2.5 text-sm text-white placeholder-white/20 outline-none transition focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/30"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-white/45">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              required placeholder="••••••••"
              className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-3.5 py-2.5 text-sm text-white placeholder-white/20 outline-none transition focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/30"
            />
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-xs text-red-400"
            >
              {error}
            </motion.p>
          )}

          <button type="submit" disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 py-2.5 text-sm font-semibold text-white shadow-lg shadow-purple-500/20 transition hover:opacity-90 active:scale-[0.98] disabled:opacity-60">
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-white/20">
          By continuing you agree to our{' '}
          <span className="cursor-pointer underline underline-offset-2 transition-colors hover:text-white/40">
            Terms of Service
          </span>
        </p>
      </motion.div>
    </div>
  )

  return (
    // overflow-x hidden keeps aura from bleeding; overflow-y auto lets the page scroll
    <div style={{ position: 'relative', overflowX: 'hidden', minHeight: '100vh' }}>
      <AuraBackground />

      <div style={{ position: 'relative', zIndex: 1 }}>

        {/* ── Mobile (< lg): single scrollable column ──────────────────────── */}
        <div className="flex flex-col px-6 pb-16 pt-10 lg:hidden">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mb-6 flex items-center gap-2.5"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 shadow-md shadow-purple-500/30">
              <Cpu className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-semibold text-white/70">TaskForge</span>
          </motion.div>

          {/* Headline */}
          <motion.div
            initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold leading-snug tracking-tight text-white">
              Stop starting from scratch.{' '}
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-orange-300 bg-clip-text text-transparent">
                Every time.
              </span>
            </h1>
            <p className="mt-2 text-sm text-white/40">
              Tell it what you need. Get something worth using.
            </p>
          </motion.div>

          {/* Feature cards — 2-col grid */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-40px' }}
            className="mb-10 grid grid-cols-2 gap-3"
          >
            {FEATURES.map(({ icon: Icon, label, desc, gradient, border, iconColor, iconBg }) => (
              <motion.div
                key={label}
                variants={fadeUp}
                transition={{ duration: 0.4, ease: 'easeOut' }}
                whileHover={{ y: -2, transition: { duration: 0.15 } }}
                className={cn(
                  'group rounded-2xl border border-white/8 bg-gradient-to-br p-4 transition-colors duration-200',
                  gradient, border,
                )}
              >
                <div className={cn('mb-2.5 inline-flex h-7 w-7 items-center justify-center rounded-lg', iconBg)}>
                  <Icon className={cn('h-3.5 w-3.5', iconColor)} />
                </div>
                <p className="mb-1 text-xs font-semibold text-white/80">{label}</p>
                <p className="text-[11px] leading-relaxed text-white/35">{desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Auth form */}
          <div>{AuthForm}</div>
        </div>

        {/* ── Desktop (lg+): scrollable left + sticky right ─────────────────── */}
        <div className="hidden min-h-screen lg:flex">

          {/* Left — scrolls with page */}
          <div className="flex flex-1 flex-col px-14 pb-24 pt-12">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="mb-16 flex items-center gap-3"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/30">
                <Cpu className="h-4.5 w-4.5 text-white" />
              </div>
              <span className="text-sm font-semibold tracking-wide text-white/70">TaskForge</span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="mb-4 max-w-lg text-5xl font-bold leading-tight tracking-tight text-white"
            >
              Stop starting
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-orange-300 bg-clip-text text-transparent">
                from scratch.
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1, ease: 'easeOut' }}
              className="mb-14 max-w-md text-base text-white/40"
            >
              Tell TaskForge what you need — a trip plan, a presentation, a resume
              rewrite, a spreadsheet, or a market briefing. Get something worth
              using, in minutes.
            </motion.p>

            {/* Feature cards — 2-col grid with scroll-triggered stagger */}
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, margin: '-80px' }}
              className="grid max-w-2xl grid-cols-2 gap-4"
            >
              {FEATURES.map(({ icon: Icon, label, desc, gradient, border, iconColor, iconBg }) => (
                <motion.div
                  key={label}
                  variants={fadeUp}
                  transition={{ duration: 0.45, ease: 'easeOut' }}
                  whileHover={{ y: -4, transition: { duration: 0.18 } }}
                  className={cn(
                    'group cursor-default rounded-2xl border border-white/8 bg-gradient-to-br p-5 transition-colors duration-200',
                    gradient, border,
                  )}
                >
                  <div className={cn('mb-3 inline-flex h-9 w-9 items-center justify-center rounded-xl', iconBg)}>
                    <Icon className={cn('h-4.5 w-4.5', iconColor)} />
                  </div>
                  <p className="mb-1.5 text-sm font-semibold text-white/85">{label}</p>
                  <p className="text-xs leading-relaxed text-white/40">{desc}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* Trust badges */}
            <motion.div
              initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="mt-12 flex flex-wrap gap-2"
            >
              {['Free to start', 'No card required', 'Results in minutes'].map((t) => (
                <span key={t} className="rounded-full border border-white/8 bg-white/[0.03] px-2.5 py-1 text-[11px] text-white/25">
                  {t}
                </span>
              ))}
            </motion.div>
          </div>

          {/* Right — sticky, stays in view as left scrolls */}
          <div className="sticky top-0 flex h-screen w-[420px] shrink-0 items-center justify-center border-l border-white/[0.06] px-10 xl:w-[460px]">
            {AuthForm}
          </div>

        </div>
      </div>
    </div>
  )
}
