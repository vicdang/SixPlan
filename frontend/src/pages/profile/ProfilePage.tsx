import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, MapPin, Pencil, Key } from 'lucide-react'
import { toast } from 'sonner'
import api from '@/lib/axios'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { formatDate } from '@/lib/utils'

interface ProfileDetail {
  account_id: string
  member_id: string
  username: string
  employee_id: string
  full_name: string
  email: string
  phone: string | null
  gender: string | null
  title: string | null
  department: { id: string; code: string; name: string } | null
  role: string
  avatar_url: string | null
  last_login_at: string | null
}

interface AssignmentSummary {
  id: string
  seat_id: string
  seat_code: string
  room_code: string
  room_name: string
  assignment_type: string
  hostname: string | null
  ip_address: string | null
  mac_address: string | null
}

function initials(name: string) {
  return name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()
}

const editSchema = z.object({
  phone: z.string().max(30).optional().or(z.literal('')),
})

const pwSchema = z
  .object({
    current_password: z.string().min(1, 'Required'),
    new_password: z
      .string()
      .min(8, 'Min 8 characters')
      .regex(/[A-Z]/, 'Must contain uppercase letter')
      .regex(/[0-9]/, 'Must contain number'),
    confirm_password: z.string(),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type EditValues = z.infer<typeof editSchema>
type PwValues = z.infer<typeof pwSchema>

export function ProfilePage() {
  const qc = useQueryClient()
  const [editOpen, setEditOpen] = useState(false)
  const [pwOpen, setPwOpen] = useState(false)
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const { data: profile, isLoading } = useQuery<ProfileDetail>({
    queryKey: ['profile'],
    queryFn: async () => {
      const { data } = await api.get('/profile')
      return data
    },
  })

  const { data: assignments } = useQuery<{ primary: AssignmentSummary | null; secondary: AssignmentSummary[] }>({
    queryKey: ['profile', 'assignments'],
    queryFn: async () => {
      const { data } = await api.get('/profile/assignments')
      return data
    },
    enabled: !!profile,
  })

  const editForm = useForm<EditValues>({ resolver: zodResolver(editSchema) })
  const pwForm = useForm<PwValues>({ resolver: zodResolver(pwSchema) })

  const updateMutation = useMutation({
    mutationFn: async (body: { phone: string | null }) => {
      const { data } = await api.put('/profile', body)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['profile'] })
      setEditOpen(false)
      toast.success('Profile updated')
    },
    onError: () => toast.error('Failed to update profile'),
  })

  const pwMutation = useMutation({
    mutationFn: async (body: { current_password: string; new_password: string }) => {
      await api.post('/profile/change-password', body)
    },
    onSuccess: () => {
      setPwOpen(false)
      pwForm.reset()
      toast.success('Password updated')
    },
    onError: (err: unknown) => {
      const msg =
        (err as { response?: { data?: { error?: { message?: string } } } })?.response?.data?.error?.message ??
        'Failed to update password'
      toast.error(msg)
    },
  })

  if (isLoading || !profile) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-surface-border border-t-accent" />
      </div>
    )
  }

  const roleVariant = (role: string) => {
    if (role === 'admin') return 'admin'
    if (role === 'manager') return 'manager'
    return 'user'
  }

  return (
    <div className="max-w-2xl space-y-6">
      <PageHeader
        title="My Profile"
        actions={
          <Button variant="outline" size="sm" onClick={() => { editForm.setValue('phone', profile.phone ?? ''); setEditOpen(true) }}>
            <Pencil className="mr-2 h-3.5 w-3.5" />
            Edit profile
          </Button>
        }
      />

      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-accent-muted flex items-center justify-center text-accent text-xl font-medium shrink-0">
              {profile.avatar_url ? (
                <img src={profile.avatar_url} alt="" className="h-full w-full rounded-full object-cover" />
              ) : (
                initials(profile.full_name)
              )}
            </div>
            <div>
              <p className="text-base font-medium text-text-primary">{profile.full_name}</p>
              {profile.title && <p className="text-sm text-text-secondary">{profile.title}</p>}
              {profile.department && <p className="text-sm text-text-muted">{profile.department.name}</p>}
            </div>
          </div>

          <Separator />

          <dl className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
            <Row label="Username" value={profile.username} mono />
            <Row label="Employee ID" value={profile.employee_id} mono />
            <Row label="Email" value={profile.email} />
            <Row label="Phone" value={profile.phone ?? '—'} />
            <Row label="Gender" value={profile.gender ?? '—'} />
            <Row label="Department" value={profile.department?.name ?? '—'} />
            <div>
              <dt className="text-text-muted mb-1">Role</dt>
              <dd>
                <Badge variant={roleVariant(profile.role) as 'admin' | 'manager' | 'user'}>
                  {profile.role}
                </Badge>
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Password</p>
              <p className="text-sm text-text-muted">••••••••</p>
            </div>
            <Button variant="outline" size="sm" onClick={() => { pwForm.reset(); setPwOpen(true) }}>
              <Key className="mr-2 h-3.5 w-3.5" />
              Change password
            </Button>
          </div>
          {profile.last_login_at && (
            <p className="text-xs text-text-muted">Last login: {formatDate(profile.last_login_at)}</p>
          )}
        </CardContent>
      </Card>

      {/* Seat Assignments */}
      <Card>
        <CardHeader>
          <CardTitle>My Seat Assignments</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-text-muted mb-2">Primary seat</p>
            {assignments?.primary ? (
              <AssignmentCard assignment={assignments.primary} />
            ) : (
              <p className="text-sm text-text-muted">No primary seat assigned</p>
            )}
          </div>
          <Separator />
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-text-muted mb-2">
              Secondary slots ({assignments?.secondary.length ?? 0})
            </p>
            {assignments?.secondary.length ? (
              <div className="space-y-2">
                {assignments.secondary.map((a) => (
                  <AssignmentCard key={a.id} assignment={a} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-text-muted">No secondary slots</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Edit Profile Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit profile</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={editForm.handleSubmit((v) =>
              updateMutation.mutate({ phone: v.phone || null }),
            )}
            className="space-y-4 mt-2"
          >
            <div className="space-y-1.5">
              <Label htmlFor="edit-phone">Phone</Label>
              <Input id="edit-phone" placeholder="+84 901 234 567" {...editForm.register('phone')} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setEditOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Saving…' : 'Save changes'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Change Password Dialog */}
      <Dialog open={pwOpen} onOpenChange={setPwOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change password</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={pwForm.handleSubmit((v) =>
              pwMutation.mutate({ current_password: v.current_password, new_password: v.new_password }),
            )}
            className="space-y-4 mt-2"
          >
            <PasswordField
              id="current-password"
              label="Current password"
              show={showCurrent}
              onToggle={() => setShowCurrent((v) => !v)}
              registration={pwForm.register('current_password')}
              error={pwForm.formState.errors.current_password?.message}
            />
            <PasswordField
              id="new-password"
              label="New password"
              show={showNew}
              onToggle={() => setShowNew((v) => !v)}
              registration={pwForm.register('new_password')}
              error={pwForm.formState.errors.new_password?.message}
              hint="Min 8 chars, 1 uppercase, 1 number"
            />
            <PasswordField
              id="confirm-password"
              label="Confirm new password"
              show={showConfirm}
              onToggle={() => setShowConfirm((v) => !v)}
              registration={pwForm.register('confirm_password')}
              error={pwForm.formState.errors.confirm_password?.message}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setPwOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={pwMutation.isPending}>
                {pwMutation.isPending ? 'Updating…' : 'Update password'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-text-muted mb-1">{label}</dt>
      <dd className={mono ? 'font-mono text-xs text-accent' : 'text-text-primary'}>{value}</dd>
    </div>
  )
}

function AssignmentCard({ assignment }: { assignment: AssignmentSummary }) {
  return (
    <div className="rounded-lg border border-surface-border bg-surface-base p-3 text-sm">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-accent">{assignment.seat_code}</span>
        <button type="button" className="flex items-center gap-1 text-xs text-text-muted hover:text-accent transition-colors">
          <MapPin className="h-3 w-3" />
          View on map
        </button>
      </div>
      <p className="text-text-muted text-xs mt-1">{assignment.room_name}</p>
      {assignment.hostname && (
        <p className="text-text-muted text-xs mt-1">
          {assignment.hostname} · {assignment.ip_address}
        </p>
      )}
    </div>
  )
}

function PasswordField({
  id, label, show, onToggle, registration, error, hint,
}: {
  id: string
  label: string
  show: boolean
  onToggle: () => void
  registration: object
  error?: string
  hint?: string
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      <div className="relative">
        <Input
          id={id}
          type={show ? 'text' : 'password'}
          className="pr-10"
          {...(registration as React.InputHTMLAttributes<HTMLInputElement>)}
        />
        <button
          type="button"
          onClick={onToggle}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary"
          tabIndex={-1}
        >
          {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
      {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}
