import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { RequireAuth } from '@/components/auth/RequireAuth'
import { LoginPage } from '@/pages/auth/LoginPage'
import { ProfilePage } from '@/pages/profile/ProfilePage'
import { NotFoundPage } from '@/pages/errors/NotFoundPage'
import { ForbiddenPage } from '@/pages/errors/ForbiddenPage'
import { useAuthStore } from '@/store/authStore'
import { tokenStorage } from '@/lib/auth-storage'
import api from '@/lib/axios'
import type { AuthUser } from '@/types/auth'

function useHydrate() {
  const setAccount = useAuthStore((s) => s.setAccount)
  const setHydrated = useAuthStore((s) => s.setHydrated)

  useEffect(() => {
    const token = tokenStorage.getAccess()
    if (!token) {
      setHydrated()
      return
    }
    api
      .get<AuthUser>('/auth/me')
      .then(({ data }) => setAccount(data))
      .catch(() => {
        tokenStorage.clear()
        setHydrated()
      })
  }, [setAccount, setHydrated])
}

function App() {
  useHydrate()

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <RequireAuth>
            <AppShell>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route
                  path="/dashboard"
                  element={
                    <div className="flex flex-col items-center justify-center h-full gap-2">
                      <p className="text-text-secondary text-sm">Dashboard</p>
                      <p className="text-text-muted text-xs">Sprint 3 — Floor plan editor coming next.</p>
                    </div>
                  }
                />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/forbidden" element={<ForbiddenPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </AppShell>
          </RequireAuth>
        }
      />
    </Routes>
  )
}

export default App
