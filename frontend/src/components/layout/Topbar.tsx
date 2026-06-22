import { Bell, ChevronDown, User } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export function Topbar() {
  const account = useAuthStore((s) => s.account)

  return (
    <header className="h-14 shrink-0 bg-surface-raised border-b border-surface-border flex items-center justify-between px-6">
      <div className="text-sm text-text-muted">
        {/* Breadcrumb — populated per-page in Sprint 2+ */}
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          className="relative p-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-overlay transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
        </button>

        <button
          type="button"
          className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-md hover:bg-surface-overlay transition-colors"
        >
          <div className="w-7 h-7 rounded-full bg-accent-muted flex items-center justify-center">
            <User className="w-4 h-4 text-accent" />
          </div>
          <span className="text-sm text-text-secondary">
            {account?.username ?? 'Account'}
          </span>
          <ChevronDown className="w-3.5 h-3.5 text-text-muted" />
        </button>
      </div>
    </header>
  )
}
