import { create } from 'zustand'
import type { AuthUser } from '@/types/auth'
import { tokenStorage } from '@/lib/auth-storage'

interface AuthStore {
  account: AuthUser | null
  isHydrated: boolean
  setAccount: (user: AuthUser) => void
  clearAccount: () => void
  hydrate: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  account: null,
  isHydrated: false,

  setAccount: (user) => set({ account: user }),

  clearAccount: () => {
    tokenStorage.clear()
    set({ account: null })
  },

  hydrate: () => {
    // Will be populated in Sprint 2 with token validation
    set({ isHydrated: true })
  },
}))
