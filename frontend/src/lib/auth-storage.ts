const KEY_ACCESS = 'seatmap_access_token'
const KEY_REFRESH = 'seatmap_refresh_token'

export const tokenStorage = {
  getAccess: () => localStorage.getItem(KEY_ACCESS),
  setAccess: (token: string) => localStorage.setItem(KEY_ACCESS, token),
  getRefresh: () => localStorage.getItem(KEY_REFRESH),
  setRefresh: (token: string) => localStorage.setItem(KEY_REFRESH, token),
  clear: () => {
    localStorage.removeItem(KEY_ACCESS)
    localStorage.removeItem(KEY_REFRESH)
  },
}
