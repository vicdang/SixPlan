import { Link } from 'react-router-dom'

export function ForbiddenPage() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <p className="text-4xl font-semibold text-text-muted">403</p>
      <p className="text-text-secondary text-sm">You don't have permission to access this page</p>
      <Link to="/dashboard" className="text-accent text-sm hover:underline">
        Back to dashboard
      </Link>
    </div>
  )
}
