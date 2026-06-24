import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import type { UserRole } from '@/types/auth'

interface Props {
  children: React.ReactNode
  roles?: UserRole[]
}

export function RequireAuth({ children, roles }: Props) {
  const account = useAuthStore((s) => s.account)
  const isHydrated = useAuthStore((s) => s.isHydrated)
  const location = useLocation()

  if (!isHydrated) {
    return (
      <div className="flex h-screen items-center justify-center bg-surface-base">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-surface-border border-t-accent" />
      </div>
    )
  }

  if (!account) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (roles && !roles.includes(account.role)) {
    return <Navigate to="/forbidden" replace />
  }

  return <>{children}</>
}
