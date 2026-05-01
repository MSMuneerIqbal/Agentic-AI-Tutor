'use client'

import { useState, useEffect, useRef } from 'react'
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  TrashIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'
import { ragAdminAPI } from '@/lib/api'

const CONTENT_TYPES = [
  'lesson', 'example', 'explanation', 'tutorial',
  'overview', 'structure', 'curriculum', 'roadmap',
  'concept', 'definition', 'comparison', 'best_practice',
  'command', 'configuration', 'introduction', 'welcome',
]

interface Document {
  doc_id: string
  title: string
  content_preview: string
  content_type: string
  topic: string
  source: string
  total_chunks: number
}

type Tab = 'upload' | 'browse'
type UploadMode = 'text' | 'file'

export function RagManager() {
  const [activeTab, setActiveTab] = useState<Tab>('upload')
  const [uploadMode, setUploadMode] = useState<UploadMode>('text')

  // upload form state
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [contentType, setContentType] = useState('lesson')
  const [topic, setTopic] = useState('')
  const [source, setSource] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // async state
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<{ ok: boolean; message: string } | null>(null)

  // browse state
  const [documents, setDocuments] = useState<Document[]>([])
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null)
  const [confirmDeleteAll, setConfirmDeleteAll] = useState(false)

  useEffect(() => {
    if (activeTab === 'browse') fetchDocuments()
  }, [activeTab])

  async function fetchDocuments() {
    setLoadingDocs(true)
    try {
      const res = await ragAdminAPI.listDocuments()
      setDocuments(res.data.documents || [])
    } catch {
      setDocuments([])
    } finally {
      setLoadingDocs(false)
    }
  }

  async function handleUpload() {
    setUploadResult(null)
    setUploading(true)
    try {
      if (uploadMode === 'text') {
        await ragAdminAPI.uploadText({ title, content, content_type: contentType, topic, source })
      } else {
        if (!selectedFile) throw new Error('No file selected')
        const fd = new FormData()
        fd.append('file', selectedFile)
        fd.append('title', title)
        fd.append('content_type', contentType)
        fd.append('topic', topic)
        fd.append('source', source || selectedFile.name)
        await ragAdminAPI.uploadFile(fd)
      }
      setUploadResult({ ok: true, message: 'Content uploaded to Pinecone successfully.' })
      setTitle(''); setContent(''); setTopic(''); setSource(''); setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || 'Upload failed'
      setUploadResult({ ok: false, message: typeof detail === 'string' ? detail : JSON.stringify(detail) })
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(docId: string) {
    setDeletingId(docId)
    try {
      await ragAdminAPI.deleteDocument(docId)
      setDocuments(prev => prev.filter(d => d.doc_id !== docId))
      if (previewDoc?.doc_id === docId) setPreviewDoc(null)
    } catch (err: any) {
      alert('Delete failed: ' + (err?.response?.data?.detail || err?.message))
    } finally {
      setDeletingId(null)
    }
  }

  async function handleDeleteAll() {
    try {
      await ragAdminAPI.deleteAll()
      setDocuments([])
      setPreviewDoc(null)
    } catch (err: any) {
      alert('Delete all failed: ' + (err?.response?.data?.detail || err?.message))
    } finally {
      setConfirmDeleteAll(false)
    }
  }

  const isUploadReady =
    title.trim() &&
    contentType &&
    topic.trim() &&
    (uploadMode === 'text' ? content.trim() : !!selectedFile)

  return (
    <div className="space-y-6">
      {/* Tab switcher */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
        {([
          { id: 'upload', label: 'Upload Content', icon: CloudArrowUpIcon },
          { id: 'browse', label: 'Browse & Manage', icon: DocumentTextIcon },
        ] as const).map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === id
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* ── UPLOAD TAB ── */}
      {activeTab === 'upload' && (
        <div className="card space-y-5">
          <h2 className="text-xl font-semibold text-gray-900">Upload Learning Content</h2>

          {/* Upload mode toggle */}
          <div className="flex space-x-3">
            {(['text', 'file'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => { setUploadMode(mode); setUploadResult(null) }}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                  uploadMode === mode
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-primary-400'
                }`}
              >
                {mode === 'text' ? 'Paste Text' : 'Upload File'}
              </button>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                className="input"
                placeholder="e.g. Python Basics Chapter 1"
                value={title}
                onChange={e => setTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Topic *</label>
              <input
                className="input"
                placeholder="e.g. Python, Machine Learning"
                value={topic}
                onChange={e => setTopic(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content Type *</label>
              <select className="select" value={contentType} onChange={e => setContentType(e.target.value)}>
                {CONTENT_TYPES.map(ct => (
                  <option key={ct} value={ct}>{ct}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Source (optional)</label>
              <input
                className="input"
                placeholder="e.g. Textbook Chapter 3"
                value={source}
                onChange={e => setSource(e.target.value)}
              />
            </div>
          </div>

          {uploadMode === 'text' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content *</label>
              <textarea
                className="input min-h-[200px] resize-y"
                placeholder="Paste your learning content here..."
                value={content}
                onChange={e => setContent(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">{content.length} characters</p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">File * (.txt, .md, .pdf, .docx)</label>
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-400 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <CloudArrowUpIcon className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                {selectedFile ? (
                  <p className="text-sm font-medium text-primary-600">{selectedFile.name}</p>
                ) : (
                  <p className="text-sm text-gray-500">Click to choose a file</p>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".txt,.md,.pdf,.docx"
                  onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                />
              </div>
            </div>
          )}

          {uploadResult && (
            <div className={`flex items-start space-x-2 p-4 rounded-lg ${uploadResult.ok ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
              {uploadResult.ok
                ? <CheckCircleIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                : <ExclamationTriangleIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />}
              <p className="text-sm">{uploadResult.message}</p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!isUploadReady || uploading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <ArrowPathIcon className="w-4 h-4 animate-spin" />
            ) : (
              <CloudArrowUpIcon className="w-4 h-4" />
            )}
            <span>{uploading ? 'Uploading…' : 'Upload to Pinecone'}</span>
          </button>
        </div>
      )}

      {/* ── BROWSE TAB ── */}
      {activeTab === 'browse' && (
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Knowledge Base
              {!loadingDocs && <span className="ml-2 text-sm font-normal text-gray-500">({documents.length} documents)</span>}
            </h2>
            <div className="flex items-center space-x-2">
              <button onClick={fetchDocuments} className="btn-secondary flex items-center space-x-1 text-sm">
                <ArrowPathIcon className={`w-4 h-4 ${loadingDocs ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              {documents.length > 0 && (
                <button
                  onClick={() => setConfirmDeleteAll(true)}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <TrashIcon className="w-4 h-4" />
                  <span>Delete All</span>
                </button>
              )}
            </div>
          </div>

          {loadingDocs ? (
            <div className="flex items-center justify-center py-12">
              <ArrowPathIcon className="w-6 h-6 animate-spin text-primary-600" />
              <span className="ml-2 text-gray-600">Loading documents…</span>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <DocumentTextIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="font-medium">No content yet</p>
              <p className="text-sm mt-1">Upload content from the Upload tab to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map(doc => (
                <div
                  key={doc.doc_id}
                  className="flex items-start justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
                >
                  <div className="flex-1 min-w-0 mr-4">
                    <div className="flex items-center flex-wrap gap-2 mb-1">
                      <h3 className="font-medium text-gray-900 truncate">{doc.title}</h3>
                      <span className="px-2 py-0.5 text-xs bg-primary-100 text-primary-700 rounded-full">{doc.content_type}</span>
                      <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">{doc.topic}</span>
                      <span className="text-xs text-gray-400">{doc.total_chunks} chunk{doc.total_chunks !== 1 ? 's' : ''}</span>
                    </div>
                    <p className="text-sm text-gray-500 line-clamp-2">{doc.content_preview}</p>
                    {doc.source && <p className="text-xs text-gray-400 mt-1">Source: {doc.source}</p>}
                  </div>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <button
                      onClick={() => setPreviewDoc(previewDoc?.doc_id === doc.doc_id ? null : doc)}
                      className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                      title="Preview"
                    >
                      <EyeIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.doc_id)}
                      disabled={deletingId === doc.doc_id}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                      title="Delete"
                    >
                      {deletingId === doc.doc_id
                        ? <ArrowPathIcon className="w-4 h-4 animate-spin" />
                        : <TrashIcon className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Preview panel */}
          {previewDoc && (
            <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{previewDoc.title}</h4>
                <button onClick={() => setPreviewDoc(null)} className="text-gray-400 hover:text-gray-600 text-sm">Close</button>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{previewDoc.content_preview}</p>
              {previewDoc.content_preview.length === 300 && (
                <p className="text-xs text-gray-400 mt-2">Preview truncated to 300 characters.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Delete All confirmation modal */}
      {confirmDeleteAll && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40" onClick={() => setConfirmDeleteAll(false)} />
          <div className="relative bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
            <ExclamationTriangleIcon className="w-10 h-10 text-red-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-center text-gray-900 mb-2">Delete All Content?</h3>
            <p className="text-sm text-gray-600 text-center mb-5">
              This will permanently remove all {documents.length} documents from Pinecone. This cannot be undone.
            </p>
            <div className="flex space-x-3">
              <button onClick={() => setConfirmDeleteAll(false)} className="btn-secondary flex-1">Cancel</button>
              <button onClick={handleDeleteAll} className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium">
                Delete All
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
