const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  role: string
  is_active: boolean
}

export interface Document {
  id: string
  user_id: string | null
  filename: string
  content_type: string
  storage_path: string
  status: string
  created_at: string
}

export interface DocumentDetails extends Document {
  chunk_count: number
  embedded_chunks: number
}

export interface UploadDocumentResponse {
  id: string
  filename: string
  content_type: string
  storage_path: string
  status: string
  created_at: string
  job_id: string
}

export interface DeleteDocumentResponse {
  message: string
  document_id: string
}

export interface JobStatus {
  job_id: string
  status: string
  document_id: string
  retries_left: number | null
  enqueued_at?: string
  started_at?: string
  ended_at?: string
  error?: string
}

export interface QuerySource {
  document: string
  page: number
  chunk_index: number
  parent_section: string | null
  section: string | null
}

export interface QueryResponse {
  conversation_id: string
  question: string
  answer: string
  sources: QuerySource[]
}

export async function checkHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`,
  )

  if (!response.ok) {
    throw new Error(
      'Backend health check failed',
    )
  }

  return response.json()
}

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ||
        'Invalid email or password',
    )
  }

  return response.json()
}

export async function getCurrentUser(
  token: string,
): Promise<User> {
  const response = await fetch(
    `${API_BASE_URL}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  if (!response.ok) {
    throw new Error(
      'Unable to load current user',
    )
  }

  return response.json()
}

export async function getDocuments(
  token: string,
): Promise<Document[]> {
  const response = await fetch(
    `${API_BASE_URL}/documents`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ||
        'Unable to load documents',
    )
  }

  return response.json()
}

export async function getDocumentDetails(
  token: string,
  documentId: string,
): Promise<DocumentDetails> {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      typeof errorData?.detail === 'string'
        ? errorData.detail
        : 'Unable to load document details',
    )
  }

  return response.json()
}

export async function uploadDocument(
  token: string,
  file: File,
): Promise<UploadDocumentResponse> {
  const formData = new FormData()

  formData.append('file', file)

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ||
        'Unable to upload document',
    )
  }

  return response.json()
}

export async function getJobStatus(
  token: string,
  jobId: string,
): Promise<JobStatus> {
  const response = await fetch(
    `${API_BASE_URL}/documents/jobs/${jobId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      typeof errorData?.detail === 'string'
        ? errorData.detail
        : 'Unable to check processing status',
    )
  }

  return response.json()
}

export async function deleteDocument(
  token: string,
  documentId: string,
): Promise<DeleteDocumentResponse> {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      typeof errorData?.detail === 'string'
        ? errorData.detail
        : 'Unable to delete document',
    )
  }

  return response.json()
}

export async function askQuestion(
  token: string,
  question: string,
  conversationId: string | null = null,
  documentIds: string[] | null = null,
): Promise<QueryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/query`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
        document_ids: documentIds,
      }),
    },
  )

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null)

    throw new Error(
      typeof errorData?.detail === 'string'
        ? errorData.detail
        : 'Unable to answer question',
    )
  }

  return response.json()
}

export function saveToken(
  token: string,
) {
  localStorage.setItem(
    'access_token',
    token,
  )
}

export function getToken() {
  return localStorage.getItem(
    'access_token',
  )
}

export function removeToken() {
  localStorage.removeItem(
    'access_token',
  )
}