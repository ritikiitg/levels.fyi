import { Link, NavLink } from 'react-router-dom';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <header className="border-b border-ink-100 bg-white/85 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.png" alt="this1" className="w-10 h-10 rounded-xl logo-glow" />
            <span className="wordmark text-3xl">
              <span className="this">this</span><span className="one">1</span>
            </span>
          </Link>
          <nav className="flex gap-2 text-sm">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `px-4 py-2 rounded-full transition ${
                  isActive ? 'bg-paper-soft text-ink-950' : 'text-ink-500 hover:text-ink-950 hover:bg-paper-soft'
                }`
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/companies"
              className={({ isActive }) =>
                `px-4 py-2 rounded-full transition ${
                  isActive ? 'bg-paper-soft text-ink-950' : 'text-ink-500 hover:text-ink-950 hover:bg-paper-soft'
                }`
              }
            >
              Companies
            </NavLink>
            <a href="/internal/admin" className="honeypot" tabIndex={-1} aria-hidden="true">admin</a>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-10">{children}</main>
      <footer className="border-t border-ink-100 text-xs text-ink-500 text-center py-4">
        this1 · Levels.fyi hackathon · No real user data
      </footer>
    </div>
  );
}
