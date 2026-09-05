import {
  useEffect,
  useRef,
  useState,
} from 'react'
import type { FormEvent } from 'react'
import ReactMarkdown from 'react-markdown'

import {
  askQuestion,
  checkHealth,
  deleteDocument,
  getCurrentUser,
  getDocumentDetails,
  getDocuments,
  getJobStatus,
  getToken,
  login,
  removeToken,
  saveToken,
  uploadDocument,
  type Document,
  type DocumentDetails,
  type QuerySource,
  type User,
} from './services/api'

import './App.css'

type Page =
  | 'dashboard'
  | 'documents'
  | 'upload'
  | 'ask'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: QuerySource[]
}

function App() {
  const [activePage, setActivePage] =
    useState<Page>('dashboard')

  const [backendStatus, setBackendStatus] =
    useState('Checking...')

  const [user, setUser] =
    useState<User | null>(null)

  const [authLoading, setAuthLoading] =
    useState(true)

  const [email, setEmail] = useState('')
  const [password, setPassword] =
    useState('')

  const [loginError, setLoginError] =
    useState('')

  const [loginLoading, setLoginLoading] =
    useState(false)

  const [documents, setDocuments] =
    useState<Document[]>([])

  const [
    documentsLoading,
    setDocumentsLoading,
  ] = useState(false)

  const [
    documentsError,
    setDocumentsError,
  ] = useState('')

  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(null)

  const [
    uploadLoading,
    setUploadLoading,
  ] = useState(false)

  const [uploadError, setUploadError] =
    useState('')

  const [uploadSuccess, setUploadSuccess] =
    useState('')

  const [
    processingStatus,
    setProcessingStatus,
  ] = useState('')

  const [
    processingError,
    setProcessingError,
  ] = useState('')

  const [question, setQuestion] =
    useState('')

  const [chatLoading, setChatLoading] =
    useState(false)

  const [chatError, setChatError] =
    useState('')

  const [
    conversationId,
    setConversationId,
  ] = useState<string | null>(null)

  const [
    chatMessages,
    setChatMessages,
  ] = useState<ChatMessage[]>([])

  const [
    selectedDocumentIds,
    setSelectedDocumentIds,
  ] = useState<string[]>([])

  const [
    selectedDocumentDetails,
    setSelectedDocumentDetails,
  ] = useState<DocumentDetails | null>(
    null,
  )

  const [
    documentDetailsLoading,
    setDocumentDetailsLoading,
  ] = useState(false)

  const [
    documentDetailsError,
    setDocumentDetailsError,
  ] = useState('')

  const [
    deletingDocumentId,
    setDeletingDocumentId,
  ] = useState<string | null>(null)

  const [
    deleteSuccess,
    setDeleteSuccess,
  ] = useState('')

  const [
    deleteError,
    setDeleteError,
  ] = useState('')

  const fileInputRef =
    useRef<HTMLInputElement | null>(null)

  const chatBottomRef =
    useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setBackendStatus(data.status)
      })
      .catch(() => {
        setBackendStatus('unavailable')
      })
  }, [])

  useEffect(() => {
    const token = getToken()

    if (!token) {
      setAuthLoading(false)
      return
    }

    getCurrentUser(token)
      .then((currentUser) => {
        setUser(currentUser)
      })
      .catch(() => {
        removeToken()
        setUser(null)
      })
      .finally(() => {
        setAuthLoading(false)
      })
  }, [])

  useEffect(() => {
    if (user) {
      loadDocuments()
    }
  }, [user])

  useEffect(() => {
    if (activePage !== 'ask') {
      return
    }

    chatBottomRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
    })
  }, [
    chatMessages,
    chatLoading,
    activePage,
  ])

  async function loadDocuments() {
    const token = getToken()

    if (!token) {
      return
    }

    setDocumentsLoading(true)
    setDocumentsError('')

    try {
      const data =
        await getDocuments(token)

      setDocuments(data)
    } catch (error) {
      if (error instanceof Error) {
        setDocumentsError(error.message)
      } else {
        setDocumentsError(
          'Unable to load documents',
        )
      }
    } finally {
      setDocumentsLoading(false)
    }
  }

  async function handleLogin(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setLoginError('')
    setLoginLoading(true)

    try {
      const result =
        await login(email, password)

      saveToken(result.access_token)

      const currentUser =
        await getCurrentUser(
          result.access_token,
        )

      setUser(currentUser)
      setEmail('')
      setPassword('')
    } catch (error) {
      if (error instanceof Error) {
        setLoginError(error.message)
      } else {
        setLoginError('Login failed')
      }
    } finally {
      setLoginLoading(false)
    }
  }

  async function handleUpload(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!selectedFile) {
      setUploadError(
        'Please choose a file first.',
      )
      return
    }

    const token = getToken()

    if (!token) {
      setUploadError(
        'Authentication token not found.',
      )
      return
    }

    const fileBeingUploaded =
      selectedFile

    setUploadLoading(true)
    setUploadError('')
    setUploadSuccess('')
    setProcessingStatus('')
    setProcessingError('')

    try {
      const result =
        await uploadDocument(
          token,
          fileBeingUploaded,
        )

      setUploadSuccess(
        `${result.filename} uploaded successfully.`,
      )

      setProcessingStatus('Queued')

      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      let completed = false

      while (!completed) {
        await new Promise(
          (resolve) =>
            setTimeout(resolve, 2000),
        )

        const job =
          await getJobStatus(
            token,
            result.job_id,
          )

        if (
          job.status === 'queued' ||
          job.status === 'scheduled' ||
          job.status === 'deferred'
        ) {
          setProcessingStatus('Queued')
        } else if (
          job.status === 'started'
        ) {
          setProcessingStatus(
            'Processing',
          )
        } else if (
          job.status === 'finished'
        ) {
          setProcessingStatus('Finished')

          setUploadSuccess(
            `${result.filename} uploaded and processed successfully.`,
          )

          completed = true

          await loadDocuments()
        } else if (
          job.status === 'failed'
        ) {
          setProcessingStatus('Failed')

          setProcessingError(
            'Document processing failed. Please try again.',
          )

          completed = true

          await loadDocuments()
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        setUploadError(error.message)
      } else {
        setUploadError(
          'Unable to upload document',
        )
      }
    } finally {
      setUploadLoading(false)
    }
  }

  async function handleViewDetails(
    documentId: string,
  ) {
    const token = getToken()

    if (!token) {
      setDocumentDetailsError(
        'Authentication token not found.',
      )
      return
    }

    setDocumentDetailsLoading(true)
    setDocumentDetailsError('')
    setSelectedDocumentDetails(null)

    try {
      const details =
        await getDocumentDetails(
          token,
          documentId,
        )

      setSelectedDocumentDetails(
        details,
      )
    } catch (error) {
      if (error instanceof Error) {
        setDocumentDetailsError(
          error.message,
        )
      } else {
        setDocumentDetailsError(
          'Unable to load document details',
        )
      }
    } finally {
      setDocumentDetailsLoading(false)
    }
  }

  function closeDocumentDetails() {
    setSelectedDocumentDetails(null)
    setDocumentDetailsError('')
  }

  async function handleDeleteDocument(
    document: Document,
  ) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.filename}"? This action cannot be undone.`,
    )

    if (!confirmed) {
      return
    }

    const token = getToken()

    if (!token) {
      setDeleteError(
        'Authentication token not found.',
      )
      return
    }

    setDeletingDocumentId(document.id)
    setDeleteError('')
    setDeleteSuccess('')

    try {
      await deleteDocument(
        token,
        document.id,
      )

      setDeleteSuccess(
        `${document.filename} deleted successfully.`,
      )

      setDocuments(
        (currentDocuments) =>
          currentDocuments.filter(
            (item) =>
              item.id !== document.id,
          ),
      )

      setSelectedDocumentIds(
        (currentIds) =>
          currentIds.filter(
            (id) =>
              id !== document.id,
          ),
      )

      if (
        selectedDocumentDetails?.id ===
        document.id
      ) {
        setSelectedDocumentDetails(null)
      }
    } catch (error) {
      if (error instanceof Error) {
        setDeleteError(error.message)
      } else {
        setDeleteError(
          'Unable to delete document',
        )
      }
    } finally {
      setDeletingDocumentId(null)
    }
  }

  function toggleDocument(
    documentId: string,
  ) {
    setSelectedDocumentIds(
      (currentIds) => {
        if (
          currentIds.includes(documentId)
        ) {
          return currentIds.filter(
            (id) => id !== documentId,
          )
        }

        return [
          ...currentIds,
          documentId,
        ]
      },
    )

    setChatError('')
  }

  function selectAllDocuments() {
    const processedIds = documents
      .filter(
        (document) =>
          document.status ===
          'processed',
      )
      .map(
        (document) => document.id,
      )

    setSelectedDocumentIds(
      processedIds,
    )

    setChatError('')
  }

  function clearDocumentSelection() {
    setSelectedDocumentIds([])
    setChatError('')
  }

  function getUniqueSources(
    sources:
      | QuerySource[]
      | undefined,
  ) {
    if (!sources) {
      return []
    }

    const unique =
      new Map<
        string,
        QuerySource
      >()

    for (const source of sources) {
      const key =
        `${source.document}|${source.page}`

      if (!unique.has(key)) {
        unique.set(key, source)
      }
    }

    return Array.from(
      unique.values(),
    )
  }

  async function handleAskQuestion(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const trimmedQuestion =
      question.trim()

    if (!trimmedQuestion) {
      return
    }

    const token = getToken()

    if (!token) {
      setChatError(
        'Authentication token not found.',
      )
      return
    }

    if (
      selectedDocumentIds.length === 0
    ) {
      setChatError(
        'Please select at least one document before asking a question.',
      )
      return
    }

    setChatError('')
    setChatLoading(true)

    setChatMessages(
      (previousMessages) => [
        ...previousMessages,
        {
          role: 'user',
          content: trimmedQuestion,
        },
      ],
    )

    setQuestion('')

    try {
      const result =
        await askQuestion(
          token,
          trimmedQuestion,
          conversationId,
          selectedDocumentIds,
        )

      setConversationId(
        result.conversation_id,
      )

      setChatMessages(
        (previousMessages) => [
          ...previousMessages,
          {
            role: 'assistant',
            content: result.answer,
            sources:
              getUniqueSources(
                result.sources,
              ),
          },
        ],
      )
    } catch (error) {
      if (error instanceof Error) {
        setChatError(error.message)
      } else {
        setChatError(
          'Unable to answer question',
        )
      }
    } finally {
      setChatLoading(false)
    }
  }

  function handleNewConversation() {
    setConversationId(null)
    setChatMessages([])
    setQuestion('')
    setChatError('')
  }

  function handleLogout() {
    removeToken()

    setUser(null)
    setDocuments([])
    setSelectedFile(null)
    setSelectedDocumentIds([])
    setConversationId(null)
    setChatMessages([])
    setSelectedDocumentDetails(null)
    setDeleteSuccess('')
    setDeleteError('')
    setProcessingStatus('')
    setProcessingError('')
    setActivePage('dashboard')

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const renderDashboard = () => {
    const processedCount =
      documents.filter(
        (document) =>
          document.status === 'processed',
      ).length

    return (
      <>
        <section className="welcome-card">
          <h2>
            Enterprise Multimodal RAG
          </h2>

          <p>
            Upload documents, build your
            knowledge base, and ask
            grounded AI questions.
          </p>
        </section>

        <section className="dashboard-grid">
          <div className="dashboard-card">
            <h3>Backend</h3>
            <p>{backendStatus}</p>
          </div>

          <div className="dashboard-card">
            <h3>Documents</h3>

            <p>
              {documentsLoading
                ? '...'
                : documents.length}
            </p>
          </div>

          <div className="dashboard-card">
            <h3>Processed</h3>

            <p>
              {documentsLoading
                ? '...'
                : processedCount}
            </p>
          </div>
        </section>

        {documentsError && (
          <section className="welcome-card">
            <p className="login-error">
              {documentsError}
            </p>
          </section>
        )}
      </>
    )
  }

  const renderDocuments = () => {
    if (documentsLoading) {
      return (
        <section className="welcome-card">
          <h2>Documents</h2>

          <p>Loading documents...</p>
        </section>
      )
    }

    if (documentsError) {
      return (
        <section className="welcome-card">
          <h2>Documents</h2>

          <p className="login-error">
            {documentsError}
          </p>
        </section>
      )
    }

    if (documents.length === 0) {
      return (
        <section className="welcome-card">
          <h2>Documents</h2>

          {deleteSuccess && (
            <p className="upload-success">
              {deleteSuccess}
            </p>
          )}

          <p>
            You do not have any
            documents yet. Upload your
            first document to begin
            building your knowledge
            base.
          </p>

          <button
            type="button"
            onClick={() =>
              setActivePage('upload')
            }
          >
            Upload Document
          </button>
        </section>
      )
    }

    return (
      <section className="welcome-card">
        <h2>Documents</h2>

        <p>
          View your uploaded documents,
          inspect their processing
          details, or remove documents
          from your knowledge base.
        </p>

        {documentDetailsError && (
          <p className="login-error">
            {documentDetailsError}
          </p>
        )}

        {deleteError && (
          <p className="login-error">
            {deleteError}
          </p>
        )}

        {deleteSuccess && (
          <p className="upload-success">
            {deleteSuccess}
          </p>
        )}

        <div className="documents-list">
          {documents.map(
            (document) => (
              <div
                className="document-card"
                key={document.id}
              >
                <h3>
                  {document.filename}
                </h3>

                <p>
                  Status:{' '}
                  <strong>
                    {document.status}
                  </strong>
                </p>

                <p>
                  Type:{' '}
                  {document.content_type}
                </p>

                <p>
                  Uploaded:{' '}
                  {new Date(
                    document.created_at,
                  ).toLocaleString()}
                </p>

                <div className="document-actions">
                  <button
                    type="button"
                    onClick={() =>
                      handleViewDetails(
                        document.id,
                      )
                    }
                    disabled={
                      documentDetailsLoading ||
                      deletingDocumentId ===
                        document.id
                    }
                  >
                    {documentDetailsLoading
                      ? 'Loading...'
                      : 'View Details'}
                  </button>

                  <button
                    type="button"
                    className="delete-button"
                    onClick={() =>
                      handleDeleteDocument(
                        document,
                      )
                    }
                    disabled={
                      deletingDocumentId ===
                      document.id
                    }
                  >
                    {deletingDocumentId ===
                    document.id
                      ? 'Deleting...'
                      : 'Delete'}
                  </button>
                </div>

                {selectedDocumentDetails?.id ===
                  document.id && (
                  <div className="document-details">
                    <h4>
                      Document Details
                    </h4>

                    <p>
                      <strong>
                        File:
                      </strong>{' '}
                      {
                        selectedDocumentDetails.filename
                      }
                    </p>

                    <p>
                      <strong>
                        Status:
                      </strong>{' '}
                      {
                        selectedDocumentDetails.status
                      }
                    </p>

                    <p>
                      <strong>
                        Chunks:
                      </strong>{' '}
                      {
                        selectedDocumentDetails.chunk_count
                      }
                    </p>

                    <p>
                      <strong>
                        Embedded Chunks:
                      </strong>{' '}
                      {
                        selectedDocumentDetails.embedded_chunks
                      }
                    </p>

                    <p>
                      <strong>
                        Content Type:
                      </strong>{' '}
                      {
                        selectedDocumentDetails.content_type
                      }
                    </p>

                    <p>
                      <strong>
                        Uploaded:
                      </strong>{' '}
                      {new Date(
                        selectedDocumentDetails.created_at,
                      ).toLocaleString()}
                    </p>

                    <button
                      type="button"
                      onClick={
                        closeDocumentDetails
                      }
                    >
                      Close
                    </button>
                  </div>
                )}
              </div>
            ),
          )}
        </div>
      </section>
    )
  }

  const renderUpload = () => {
    return (
      <section className="welcome-card">
        <h2>Upload Document</h2>

        <p>
          Upload PDF, DOCX, PNG, or JPEG
          files to your knowledge base.
        </p>

        <form
          className="upload-form"
          onSubmit={handleUpload}
        >
          <label htmlFor="document-file">
            Choose a document
          </label>

          <input
            ref={fileInputRef}
            id="document-file"
            type="file"
            accept=".pdf,.docx,.png,.jpg,.jpeg"
            onChange={(event) => {
              const file =
                event.target.files?.[0] ??
                null

              setSelectedFile(file)
              setUploadError('')
              setUploadSuccess('')
              setProcessingStatus('')
              setProcessingError('')
            }}
          />

          {selectedFile && (
            <div className="selected-file">
              <strong>
                Selected:
              </strong>{' '}
              {selectedFile.name}
            </div>
          )}

          {uploadError && (
            <p className="upload-error">
              {uploadError}
            </p>
          )}

          {uploadSuccess && (
            <p className="upload-success">
              {uploadSuccess}
            </p>
          )}

          {processingStatus && (
            <p>
              <strong>
                Processing Status:
              </strong>{' '}
              {processingStatus}
            </p>
          )}

          {processingError && (
            <p className="upload-error">
              {processingError}
            </p>
          )}

          <button
            type="submit"
            disabled={
              uploadLoading ||
              !selectedFile
            }
          >
            {uploadLoading
              ? 'Processing...'
              : 'Upload Document'}
          </button>
        </form>
      </section>
    )
  }

  const renderAskAI = () => {
    if (documentsLoading) {
      return (
        <section className="welcome-card">
          <h2>Ask AI</h2>

          <p>
            Loading your knowledge
            base...
          </p>
        </section>
      )
    }

    const processedDocuments =
      documents.filter(
        (document) =>
          document.status ===
          'processed',
      )

    if (
      processedDocuments.length === 0
    ) {
      return (
        <section className="welcome-card">
          <h2>Ask AI</h2>

          <p>
            You need at least one
            processed document before
            you can ask AI questions.
          </p>

          <button
            type="button"
            onClick={() =>
              setActivePage('upload')
            }
          >
            Upload Document
          </button>
        </section>
      )
    }

    return (
      <section className="chat-card">
        <div className="chat-header">
          <div>
            <h2>Ask AI</h2>

            <p>
              Select documents and ask
              grounded questions about
              their content.
            </p>
          </div>

          <button
            type="button"
            className="new-chat-button"
            onClick={
              handleNewConversation
            }
          >
            New Conversation
          </button>
        </div>

        <div className="document-selector">
          <div className="document-selector-header">
            <div>
              <h3>Knowledge Base</h3>

              <p>
                Choose which documents
                AI should search.
              </p>
            </div>

            <div className="document-selection-actions">
              <button
                type="button"
                onClick={
                  selectAllDocuments
                }
              >
                Select All
              </button>

              <button
                type="button"
                onClick={
                  clearDocumentSelection
                }
              >
                Clear
              </button>
            </div>
          </div>

          <div className="document-options">
            {processedDocuments.map(
              (document) => (
                <label
                  className="document-option"
                  key={document.id}
                >
                  <input
                    type="checkbox"
                    checked={selectedDocumentIds.includes(
                      document.id,
                    )}
                    onChange={() =>
                      toggleDocument(
                        document.id,
                      )
                    }
                  />

                  <div>
                    <strong>
                      {document.filename}
                    </strong>

                    <span>
                      {document.status}
                    </span>
                  </div>
                </label>
              ),
            )}
          </div>

          <p className="selection-count">
            {selectedDocumentIds.length}{' '}
            document(s) selected
          </p>
        </div>

        <div className="chat-messages">
          {chatMessages.length ===
            0 && (
            <div className="chat-empty">
              <h3>
                Ask your first question
              </h3>

              <p>
                AI will answer using
                only the selected
                documents.
              </p>
            </div>
          )}

          {chatMessages.map(
            (message, index) => {
              const sources =
                getUniqueSources(
                  message.sources,
                )

              return (
                <div
                  key={index}
                  className={`chat-message ${message.role}`}
                >
                  <div className="message-label">
                    {message.role ===
                    'user'
                      ? 'You'
                      : 'AI'}
                  </div>

                  <div className="message-content">
                    {message.role ===
                    'assistant' ? (
                      <ReactMarkdown>
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      message.content
                    )}
                  </div>

                  {message.role ===
                    'assistant' &&
                    sources.length >
                      0 && (
                      <div className="sources">
                        <h4>Sources</h4>

                        {sources.map(
                          (
                            source,
                            sourceIndex,
                          ) => (
                            <div
                              key={`${source.document}-${source.page}-${sourceIndex}`}
                              className="source-card"
                            >
                              <strong>
                                {
                                  source.document
                                }
                              </strong>

                              <span>
                                Page{' '}
                                {source.page}
                              </span>

                              {source.parent_section && (
                                <span>
                                  {
                                    source.parent_section
                                  }
                                </span>
                              )}

                              {source.section && (
                                <span>
                                  {
                                    source.section
                                  }
                                </span>
                              )}
                            </div>
                          ),
                        )}
                      </div>
                    )}
                </div>
              )
            },
          )}

          {chatLoading && (
            <div className="chat-message assistant">
              <div className="message-label">
                AI
              </div>

              <div className="message-content">
                Thinking...
              </div>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {chatError && (
          <p className="chat-error">
            {chatError}
          </p>
        )}

        <form
          className="chat-form"
          onSubmit={
            handleAskQuestion
          }
        >
          <textarea
            value={question}
            placeholder="Ask a question about the selected documents..."
            onChange={(event) =>
              setQuestion(
                event.target.value,
              )
            }
            disabled={chatLoading}
          />

          <button
            type="submit"
            disabled={
              chatLoading ||
              !question.trim()
            }
          >
            {chatLoading
              ? 'Asking...'
              : 'Ask AI'}
          </button>
        </form>
      </section>
    )
  }

  if (authLoading) {
    return (
      <div className="login-page">
        <div className="login-card">
          <h1>
            Enterprise Multimodal RAG
          </h1>

          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="login-page">
        <div className="login-card">
          <h1>
            Enterprise Multimodal RAG
          </h1>

          <p>
            Sign in to access your
            knowledge base.
          </p>

          <form
            className="login-form"
            onSubmit={handleLogin}
          >
            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value,
                )
              }
              required
            />

            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
              required
            />

            {loginError && (
              <p className="login-error">
                {loginError}
              </p>
            )}

            <button
              type="submit"
              disabled={loginLoading}
            >
              {loginLoading
                ? 'Signing in...'
                : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="sidebar-brand">
            <h2>Enterprise RAG</h2>

            <p>
              AI Knowledge Platform
            </p>
          </div>

          <nav className="sidebar-nav">
            <button
              type="button"
              className={
                activePage ===
                'dashboard'
                  ? 'active'
                  : ''
              }
              onClick={() =>
                setActivePage(
                  'dashboard',
                )
              }
            >
              Dashboard
            </button>

            <button
              type="button"
              className={
                activePage ===
                'documents'
                  ? 'active'
                  : ''
              }
              onClick={() =>
                setActivePage(
                  'documents',
                )
              }
            >
              Documents
            </button>

            <button
              type="button"
              className={
                activePage ===
                'upload'
                  ? 'active'
                  : ''
              }
              onClick={() =>
                setActivePage(
                  'upload',
                )
              }
            >
              Upload
            </button>

            <button
              type="button"
              className={
                activePage === 'ask'
                  ? 'active'
                  : ''
              }
              onClick={() =>
                setActivePage('ask')
              }
            >
              Ask AI
            </button>
          </nav>
        </div>

        <div className="sidebar-user">
          <p>{user.email}</p>

          <span>{user.role}</span>

          <button
            type="button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="top-bar">
          <div>
            <h1>
              {activePage ===
                'dashboard' &&
                'Dashboard'}

              {activePage ===
                'documents' &&
                'Documents'}

              {activePage ===
                'upload' &&
                'Upload Document'}

              {activePage ===
                'ask' &&
                'Ask AI'}
            </h1>
          </div>

          <div className="backend-status">
            Backend:{' '}
            <strong>
              {backendStatus}
            </strong>
          </div>
        </header>

        <div className="page-content">
          {activePage ===
            'dashboard' &&
            renderDashboard()}

          {activePage ===
            'documents' &&
            renderDocuments()}

          {activePage ===
            'upload' &&
            renderUpload()}

          {activePage === 'ask' &&
            renderAskAI()}
        </div>
      </main>
    </div>
  )
}

export default App