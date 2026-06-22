import { Routes, Route, Navigate } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { NotFoundPage } from '@/pages/errors/NotFoundPage'
import { ForbiddenPage } from '@/pages/errors/ForbiddenPage'

function App() {
  return (
    <Routes>
      <Route
        path="/*"
        element={
          <AppShell>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route
                path="/dashboard"
                element={
                  <div className="flex flex-col items-center justify-center h-full gap-2">
                    <p className="text-text-secondary text-sm">
                      Sprint 1 complete — Foundation ready.
                    </p>
                    <p className="text-text-muted text-xs">
                      Auth and routing arrive in Sprint 2.
                    </p>
                  </div>
                }
              />
              <Route path="/forbidden" element={<ForbiddenPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </AppShell>
        }
      />
    </Routes>
  )
}

export default App
