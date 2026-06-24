import { create } from 'zustand'
import type { AuthUser } from '@/types/auth'
import { tokenStorage } from '@/lib/auth-storage'

interface AuthStore {
  account: AuthUser | null
  isHydrated: boolean
  setAccount: (user: AuthUser) => void
  clearAccount: () => void
  setHydrated: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  account: null,
  isHydrated: false,

  setAccount: (user) => set({ account: user, isHydrated: true }),

  clearAccount: () => {
    tokenStorage.clear()
    set({ account: null })
  },

  setHydrated: () => set({ isHydrated: true }),
}))
