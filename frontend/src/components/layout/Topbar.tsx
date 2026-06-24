import { Bell, ChevronDown, LogOut, User, UserCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useLogout } from '@/hooks/useAuth'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export function Topbar() {
  const account = useAuthStore((s) => s.account)
  const logout = useLogout()

  return (
    <header className="h-14 shrink-0 bg-surface-raised border-b border-surface-border flex items-center justify-between px-6">
      <div className="text-sm text-text-muted" />

      <div className="flex items-center gap-3">
        <button
          type="button"
          className="relative p-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-overlay transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
        </button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
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
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel className="text-xs text-text-muted font-normal">
              {account?.full_name}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link to="/profile" className="flex items-center gap-2 cursor-pointer">
                <UserCircle className="w-4 h-4" />
                My Profile
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => logout.mutate()}
              className="flex items-center gap-2 text-red-400 focus:text-red-400 cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
