// Frontend API client for Little Star Playhouse FastAPI backend
// All API calls go through this module. Uses VITE_API_BASE_URL from env.

// Defaults to the same-origin reverse-proxy path. Split deployments should set
// VITE_API_BASE_URL at build time to the public API base ending in /api.
const API_BASE = (import.meta.env.VITE_API_BASE_URL?.trim() || '/api').replace(/\/+$/, '')

export function absoluteApiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path
  if (!path.startsWith('/api/')) return path
  return `${API_BASE.replace(/\/$/, '')}/${path.replace(/^\//, '').replace(/^api\//, '')}`
}

// ─── Shared state ────────────────────────────────────────────────
let csrfToken: string | null = null

export function setCsrfToken(token: string | null) { csrfToken = token }
export function getCsrfToken() { return csrfToken }

// ─── Generic fetch wrapper ───────────────────────────────────────
export class ApiError extends Error {
  status: number
  detail: string
  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`
  const headers: Record<string, string> = { ...(options.headers as Record<string, string> || {}) }

  // Add CSRF token for state-changing requests
  if (options.method && options.method !== 'GET' && csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }

  // Add JSON content-type unless it's FormData (multipart)
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // send session cookie
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const errorBody = await response.json()
      detail = errorBody.detail || errorBody.message || detail
    } catch { /* not JSON */ }
    throw new ApiError(response.status, detail)
  }

  // Handle 204 No Content
  if (response.status === 204) return undefined as T

  return response.json()
}

// ─── Type definitions ────────────────────────────────────────────
export type UserInfo = {
  id: string
  username: string
  display_name: string
  role: string
  is_active: boolean
  created_at: string
}

export type AuthResponse = {
  user: UserInfo
  csrf_token: string
}

export type ApiNoticeAttachment = {
  id: string
  file_id: string
  filename: string
  mime_type: string
  size: number
  attachment_type: string
  caption: string | null
  download_url: string
}

export type ApiNotice = {
  id: string
  slug: string
  title: string
  excerpt: string
  body: string
  category: string
  status?: string
  is_pinned: boolean
  is_important: boolean
  cover_image_id?: string | null
  cover_image_url: string | null
  external_url: string | null
  author: { id?: string; display_name: string }
  created_at: string
  updated_at: string
  published_at: string | null
  expires_at: string | null
  attachments: ApiNoticeAttachment[]
}

export type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  page_size: number
}

export type ApiDocument = {
  id: string
  title: string
  description: string
  category: string
  status: string
  file_id: string
  download_url: string
  file: {
    id: string
    original_filename: string
    mime_type: string
    extension: string
    file_size: number
  }
  created_at: string
  updated_at: string
  published_at: string | null
  expires_at: string | null
}

export type UploadedFile = {
  id: string
  original_filename: string
  display_filename: string
  mime_type: string
  extension: string
  file_size: number
  download_url: string
  created_at?: string
}

export type ApiGalleryItem = {
  id: string
  file_id: string
  caption: string
  image_url: string
  created_at: string
}

export type ApiInquiry = {
  id: string
  parent_name: string
  phone: string
  email: string | null
  child_age: string | null
  program: string | null
  message: string | null
  status: 'NEW' | 'REVIEWED' | 'CONTACTED' | 'CLOSED' | string
  created_at: string
}

export type DashboardData = {
  published_notices: number
  draft_notices: number
  scheduled_notices: number
  published_documents: number
  total_inquiries: number
  unread_inquiries: number
  recent_notices: ApiNotice[]
  recent_uploads: UploadedFile[]
  recent_inquiries?: ApiInquiry[]
}

// ─── Health ──────────────────────────────────────────────────────
export async function healthCheck(): Promise<{ status: string; version: string }> {
  return request('/health')
}

// ─── Auth ────────────────────────────────────────────────────────
export async function login(username: string, password: string): Promise<AuthResponse> {
  const data = await request<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  setCsrfToken(data.csrf_token)
  return data
}

export async function logout(): Promise<void> {
  await request<{ message: string }>('/auth/logout', { method: 'POST' })
  setCsrfToken(null)
}

export async function getMe(): Promise<AuthResponse> {
  const data = await request<AuthResponse>('/auth/me')
  setCsrfToken(data.csrf_token)
  return data
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
  return request('/auth/change-password', {
    method: 'POST',
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  })
}

// ─── Public Notices ──────────────────────────────────────────────
export async function getPublicNotices(params: {
  page?: number
  page_size?: number
  search?: string
  category?: string
  important_only?: boolean
} = {}): Promise<PaginatedResponse<ApiNotice>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.search) searchParams.set('search', params.search)
  if (params.category) searchParams.set('category', params.category)
  if (params.important_only) searchParams.set('important_only', 'true')
  const qs = searchParams.toString()
  return request(`/notices${qs ? '?' + qs : ''}`)
}

export async function getPublicNotice(idOrSlug: string): Promise<ApiNotice> {
  return request(`/notices/${idOrSlug}`)
}

// ─── Admin Notices ───────────────────────────────────────────────
export async function getAdminNotices(params: {
  page?: number
  page_size?: number
  search?: string
  category?: string
  status?: string
} = {}): Promise<PaginatedResponse<ApiNotice>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.search) searchParams.set('search', params.search)
  if (params.category) searchParams.set('category', params.category)
  if (params.status) searchParams.set('status', params.status)
  const qs = searchParams.toString()
  return request(`/notices/admin/list/all${qs ? '?' + qs : ''}`)
}

export async function getAdminNotice(noticeId: string): Promise<ApiNotice> {
  return request(`/notices/admin/detail/${noticeId}`)
}

export async function createNotice(data: {
  title: string
  excerpt: string
  body: string
  category: string
  status?: string
  is_pinned?: boolean
  is_important?: boolean
  cover_image_id?: string | null
  external_url?: string | null
  attachment_ids?: string[]
  published_at?: string | null
  expires_at?: string | null
}): Promise<ApiNotice> {
  return request('/notices', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateNotice(noticeId: string, data: {
  title?: string
  excerpt?: string
  body?: string
  category?: string
  status?: string
  is_pinned?: boolean
  is_important?: boolean
  cover_image_id?: string | null
  external_url?: string | null
  attachment_ids?: string[]
  published_at?: string | null
  expires_at?: string | null
}): Promise<ApiNotice> {
  return request(`/notices/${noticeId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteNotice(noticeId: string): Promise<void> {
  return request(`/notices/${noticeId}`, { method: 'DELETE' })
}

// ─── Public Documents ────────────────────────────────────────────
export async function getPublicDocuments(params: {
  page?: number
  page_size?: number
  search?: string
  category?: string
  file_type?: string
  sort?: string
} = {}): Promise<PaginatedResponse<ApiDocument>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.search) searchParams.set('search', params.search)
  if (params.category) searchParams.set('category', params.category)
  if (params.file_type) searchParams.set('file_type', params.file_type)
  if (params.sort) searchParams.set('sort', params.sort)
  const qs = searchParams.toString()
  return request(`/documents${qs ? '?' + qs : ''}`)
}

// ─── Admin Documents ─────────────────────────────────────────────
export async function getAdminDocuments(params: {
  page?: number
  page_size?: number
  search?: string
  category?: string
  status?: string
} = {}): Promise<PaginatedResponse<ApiDocument>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.search) searchParams.set('search', params.search)
  if (params.category) searchParams.set('category', params.category)
  if (params.status) searchParams.set('status', params.status)
  const qs = searchParams.toString()
  return request(`/documents/admin/list/all${qs ? '?' + qs : ''}`)
}

export async function createDocument(data: {
  title: string
  description: string
  category: string
  file_id: string
  status?: string
  published_at?: string | null
  expires_at?: string | null
}): Promise<ApiDocument> {
  return request('/documents', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateDocument(documentId: string, data: {
  title?: string
  description?: string
  category?: string
  file_id?: string
  status?: string
  published_at?: string | null
  expires_at?: string | null
}): Promise<ApiDocument> {
  return request(`/documents/${documentId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteDocument(documentId: string): Promise<void> {
  return request(`/documents/${documentId}`, { method: 'DELETE' })
}

// ─── File Uploads ────────────────────────────────────────────────
export async function uploadFiles(files: File[], onProgress?: (progress: number) => void): Promise<{ files: UploadedFile[] }> {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  return uploadForm('/uploads', formData, onProgress)
}

function uploadForm<T>(path: string, formData: FormData, onProgress?: (progress: number) => void): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE}${path}`)
    xhr.withCredentials = true
    if (csrfToken) xhr.setRequestHeader('X-CSRF-Token', csrfToken)
    xhr.upload.onprogress = event => {
      if (event.lengthComputable) onProgress?.(Math.round((event.loaded / event.total) * 100))
    }
    xhr.onerror = () => reject(new ApiError(0, 'Network error while uploading. Check your connection and try again.'))
    xhr.onabort = () => reject(new ApiError(0, 'Upload was cancelled.'))
    xhr.onload = () => {
      let body: any = null
      try { body = xhr.responseText ? JSON.parse(xhr.responseText) : null } catch { /* response was not JSON */ }
      if (xhr.status >= 200 && xhr.status < 300) {
        onProgress?.(100)
        resolve(body as T)
      } else {
        reject(new ApiError(xhr.status, body?.detail || body?.message || `Upload failed with status ${xhr.status}`))
      }
    }
    xhr.send(formData)
  })
}

export async function getAdminUploads(params: {
  page?: number
  page_size?: number
  search?: string
  file_type?: string
} = {}): Promise<PaginatedResponse<UploadedFile>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.search) searchParams.set('search', params.search)
  if (params.file_type) searchParams.set('file_type', params.file_type)
  const qs = searchParams.toString()
  return request(`/uploads/admin/list/all${qs ? '?' + qs : ''}`)
}

export async function deleteUpload(fileId: string): Promise<void> {
  return request(`/uploads/admin/${fileId}`, { method: 'DELETE' })
}

export async function getGallery(): Promise<{ items: ApiGalleryItem[] }> {
  return request('/gallery')
}

export async function createGalleryImage(file: File, caption: string, onProgress?: (progress: number) => void): Promise<ApiGalleryItem> {
  const formData = new FormData()
  formData.append('image', file)
  formData.append('caption', caption)
  return uploadForm('/gallery/admin/images', formData, onProgress)
}

export async function deleteGalleryImage(itemId: string): Promise<void> {
  return request(`/gallery/admin/${itemId}`, { method: 'DELETE' })
}

export function getDownloadUrl(fileId: string): string {
  return `${API_BASE}/uploads/${fileId}/download`
}

// ─── Inquiries ───────────────────────────────────────────────────
export async function submitInquiry(data: {
  parent_name: string
  phone: string
  email?: string
  child_age?: string
  program?: string
  message?: string
  website?: string
}): Promise<{ message: string; id: string }> {
  return request('/inquiries', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getAdminInquiries(params: {
  page?: number
  page_size?: number
  search?: string
  status_filter?: string
} = {}): Promise<PaginatedResponse<ApiInquiry>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.search) searchParams.set('search', params.search)
  if (params.status_filter) searchParams.set('status_filter', params.status_filter)
  const qs = searchParams.toString()
  return request(`/inquiries/admin/list/all${qs ? '?' + qs : ''}`)
}

export async function getAdminInquiry(inquiryId: string): Promise<ApiInquiry> {
  return request(`/inquiries/admin/${inquiryId}`)
}

export async function updateInquiryStatus(inquiryId: string, status: string): Promise<ApiInquiry> {
  return request(`/inquiries/admin/${inquiryId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

export async function deleteInquiry(inquiryId: string): Promise<void> {
  return request(`/inquiries/admin/${inquiryId}`, { method: 'DELETE' })
}

// ─── Dashboard ───────────────────────────────────────────────────
export async function getDashboard(): Promise<DashboardData> {
  return request('/admin/dashboard')
}
