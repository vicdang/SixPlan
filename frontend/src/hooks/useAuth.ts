import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import api from '@/lib/axios'
import { tokenStorage } from '@/lib/auth-storage'
import { useAuthStore } from '@/store/authStore'
import type { AuthUser, LoginResponse } from '@/types/auth'

export function useMe() {
  return useQuery<AuthUser>({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const { data } = await api.get('/auth/me')
      return data
    },
    enabled: !!tokenStorage.getAccess(),
    retry: false,
  })
}

export function useLogin() {
  const setAccount = useAuthStore((s) => s.setAccount)
  const navigate = useNavigate()
  const qc = useQueryClient()

  return useMutation<LoginResponse, Error, { identifier: string; password: string }>({
    mutationFn: async (body) => {
      const { data } = await api.post<LoginResponse>('/auth/login', body)
      return data
    },
    onSuccess: (data) => {
      tokenStorage.setAccess(data.access_token)
      tokenStorage.setRefresh(data.refresh_token)
      setAccount(data.user)
      qc.invalidateQueries({ queryKey: ['auth'] })
      navigate('/dashboard')
    },
    onError: (err: unknown) => {
      const msg =
        (err as { response?: { data?: { error?: { message?: string } } } })?.response?.data?.error?.message ??
        'Login failed'
      toast.error(msg)
    },
  })
}

export function useLogout() {
  const clearAccount = useAuthStore((s) => s.clearAccount)
  const navigate = useNavigate()
  const qc = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      await api.post('/auth/logout')
    },
    onSettled: () => {
      clearAccount()
      qc.clear()
      navigate('/login')
      toast.success('Signed out')
    },
  })
}

export function useChangePassword() {
  return useMutation({
    mutationFn: async (body: { current_password: string; new_password: string }) => {
      await api.post('/auth/change-password', body)
    },
    onSuccess: () => toast.success('Password updated'),
    onError: (err: unknown) => {
      const msg =
        (err as { response?: { data?: { error?: { message?: string } } } })?.response?.data?.error?.message ??
        'Failed to update password'
      toast.error(msg)
    },
  })
}
