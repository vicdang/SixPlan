import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Map,
  Search,
  BookMarked,
  ClipboardList,
  Users,
  FolderKanban,
  Building2,
  UserCog,
  Building,
  Wrench,
  FileText,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
}

interface NavGroup {
  title: string
  items: NavItem[]
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: 'Navigation',
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { label: 'Floor Plans', href: '/rooms', icon: Map },
      { label: 'Search', href: '/search', icon: Search },
      { label: 'My Assignments', href: '/assignments', icon: BookMarked },
    ],
  },
  {
    title: 'Management',
    items: [
      { label: 'Seat Requests', href: '/requests', icon: ClipboardList },
      { label: 'Members', href: '/members', icon: Users },
      { label: 'Projects', href: '/projects', icon: FolderKanban },
    ],
  },
  {
    title: 'Administration',
    items: [
      { label: 'Rooms', href: '/admin/rooms', icon: Building2 },
      { label: 'Accounts', href: '/admin/accounts', icon: UserCog },
      { label: 'Departments', href: '/admin/departments', icon: Building },
      { label: 'Facilities', href: '/admin/facilities', icon: Wrench },
      { label: 'Audit Logs', href: '/admin/audit-logs', icon: FileText },
    ],
  },
]

export function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-surface-raised border-r border-surface-border flex flex-col h-full overflow-y-auto">
      <div className="px-4 py-5 border-b border-surface-border">
        <span className="text-xl font-semibold tracking-tight text-text-primary">SEATMAP</span>
        <p className="text-xs text-text-muted mt-0.5">Workplace seat management</p>
      </div>

      <nav className="flex-1 px-2 py-4 space-y-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.title}>
            <p className="px-3 mb-1 text-xs font-medium uppercase tracking-wider text-text-muted">
              {group.title}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((item) => (
                <li key={item.href}>
                  <NavLink
                    to={item.href}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                        isActive
                          ? 'bg-accent-muted text-accent font-medium'
                          : 'text-text-secondary hover:bg-surface-overlay hover:text-text-primary',
                      )
                    }
                  >
                    <item.icon className="w-4 h-4 shrink-0" />
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  )
}
