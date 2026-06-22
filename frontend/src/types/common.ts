export interface Pagination {
  page: number
  size: number
  total: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: Pagination
}

export interface ApiError {
  error: {
    code: string
    message: string
    details?: Array<{ field: string; message: string }>
  }
}
