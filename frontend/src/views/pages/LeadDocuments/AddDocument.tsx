import React, { useState, useEffect } from 'react'
import Upload from '@/components/ui/Upload'
import { leadDocumentApi } from './api/apiLeadDocument'
import type { LeadDocument, DocType } from './api/apiLeadDocument'
import { userApi, User } from '../Users/api/userApi'
import { VscFilePdf, VscFileZip, VscFile, VscTrash } from 'react-icons/vsc'
import { HiOutlineEye, HiOutlineDownload } from 'react-icons/hi'
import Dialog from '@/components/ui/Dialog/Dialog'

interface LeadDocumentUploadProps {
    leadId: number
    onNotify?: (message: string, type: 'success' | 'danger') => void
}

// Helper to get icon by doc type
const getFileIcon = (docType: string) => {
    switch (docType) {
        case 'pdf':
            return <VscFilePdf className="text-red-500 text-2xl" />
        case 'zip':
            return <VscFileZip className="text-yellow-600 text-2xl" />
        // For image, word, excel, fallback to generic file icon
        case 'image':
        case 'word':
        case 'excel':
        default:
            return <VscFile className="text-gray-500 text-2xl" />
    }
}

// Helper to get doc type from file
const getDocType = (file: File): DocType => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!ext) return 'other'
    if (['pdf'].includes(ext)) return 'pdf'
    if (['jpg', 'jpeg', 'png'].includes(ext)) return 'image'
    if (['doc', 'docx'].includes(ext)) return 'word'
    if (['xls', 'xlsx'].includes(ext)) return 'excel'
    if (['zip'].includes(ext)) return 'zip' as DocType // fallback, not in DocType union
    return 'other'
}

// Helper to get file URL (now uses the 'file' field from backend)
const getFileUrl = (doc: LeadDocument) => {
    // If the backend returns a full URL, use it directly. Otherwise, prepend /media/
    if (doc.file?.startsWith('http')) return doc.file;
    return doc.file ? `/media/${doc.file.replace(/^lead_documents\//, '')}` : '';
};

const isImage = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ['jpg', 'jpeg', 'png'].includes(ext || '');
};

const LeadDocumentUpload: React.FC<LeadDocumentUploadProps> = ({ leadId, onNotify }) => {
    const [uploadedDocs, setUploadedDocs] = useState<LeadDocument[]>([])
    const [users, setUsers] = useState<User[]>([])
    const [loading, setLoading] = useState(false)
    const [deletingId, setDeletingId] = useState<number | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [isDialogOpen, setIsDialogOpen] = useState(false)

    useEffect(() => {
        // Fetch all uploaded documents for this lead
        const fetchDocs = async () => {
            setLoading(true)
            try {
                const res = await leadDocumentApi.getDocuments({ lead: leadId })
                setUploadedDocs(res.results)
            } finally {
                setLoading(false)
            }
        }
        if (leadId) fetchDocs()
    }, [leadId])

    useEffect(() => {
        // Fetch all users for mapping uploader name
        const fetchUsers = async () => {
            const res = await userApi.getUsers({})
            setUsers(res.results)
        }
        fetchUsers()
    }, [])

    // Map user id to name
    const getUserName = (userId: number | null) => {
        if (!userId) return 'Unknown'
        const user = users.find(u => u.id === userId)
        return user ? user.name : 'Unknown'
    }

    // Format date/time
    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr)
        return date.toLocaleString()
    }

    // Handle file upload
    const handleUpload = async (files: File[]) => {
        let success = true
        for (const file of files) {
            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('lead_doc', file.name);
                formData.append('lead', String(leadId));
                formData.append('doc_type', getDocType(file));
                await leadDocumentApi.createDocument(formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                });
            } catch (e) {
                success = false
            }
        }
        // Refresh the list for this lead
        const res = await leadDocumentApi.getDocuments({ lead: leadId })
        setUploadedDocs(res.results)
        if (onNotify) {
            if (success) {
                onNotify('Document(s) uploaded successfully', 'success')
            } else {
                onNotify('Some documents failed to upload', 'danger')
            }
        }
    }

    // Handle delete
    const handleDelete = async (docId: number) => {
        setDeletingId(docId)
        try {
            await leadDocumentApi.deleteDocument(docId)
            const res = await leadDocumentApi.getDocuments({ lead: leadId })
            setUploadedDocs(res.results)
            if (onNotify) onNotify('Document deleted successfully', 'success')
        } catch (e) {
            if (onNotify) onNotify('Failed to delete document', 'danger')
        } finally {
            setDeletingId(null)
        }
    }

    const handleView = (doc: LeadDocument) => {
        const url = getFileUrl(doc)
        if (isImage(doc.lead_doc)) {
            setPreviewUrl(url)
            setIsDialogOpen(true)
        } else {
            // For non-images, trigger download
            const link = document.createElement('a')
            link.href = url
            link.download = doc.lead_doc
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
        }
    }

    return (
        <div className="space-y-8">
            <div className="bg-white rounded shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Upload Lead Documents</h2>
                <Upload
                    draggable
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
                    onChange={handleUpload}
                    tip={<span className="text-xs text-gray-500">Drag and drop files here, or click to select files</span>}
                />
            </div>
            <div className="bg-white rounded shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Uploaded Documents</h2>
                {loading ? (
                    <div>Loading...</div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead>
                                <tr>
                                    <th className="px-4 py-2 text-left">Type</th>
                                    <th className="px-4 py-2 text-left">File Name</th>
                                    <th className="px-4 py-2 text-left">Uploaded By</th>
                                    <th className="px-4 py-2 text-left">Uploaded At</th>
                                    <th className="px-4 py-2 text-left">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {uploadedDocs.map(doc => (
                                    <tr key={doc.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-2">{getFileIcon(doc.doc_type)}</td>
                                        <td className="px-4 py-2">{doc.lead_doc}</td>
                                        <td className="px-4 py-2">{getUserName(doc.added_by)}</td>
                                        <td className="px-4 py-2">{formatDate(doc.created_at)}</td>
                                        <td className="px-4 py-2 flex gap-2">
                                            <button
                                                onClick={() => handleView(doc)}
                                                className="text-blue-500 hover:text-blue-700 focus:outline-none"
                                                title="View"
                                                type="button"
                                            >
                                                <HiOutlineEye className="text-xl" />
                                            </button>
                                            <a
                                                href={getFileUrl(doc)}
                                                download
                                                className="text-green-600 hover:text-green-800 focus:outline-none"
                                                title="Download"
                                            >
                                                <HiOutlineDownload className="text-xl" />
                                            </a>
                                            <button
                                                className="text-red-500 hover:text-red-700 focus:outline-none"
                                                title="Delete"
                                                disabled={deletingId === doc.id}
                                                onClick={() => handleDelete(doc.id)}
                                            >
                                                <VscTrash className="text-xl" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {uploadedDocs.length === 0 && (
                            <div className="text-center text-gray-400 py-8">No documents uploaded yet.</div>
                        )}
                    </div>
                )}
            </div>
            <Dialog isOpen={isDialogOpen} onClose={() => setIsDialogOpen(false)} width={500}>
                {previewUrl && (
                    <img src={previewUrl} alt="Preview" className="max-w-full max-h-[70vh] mx-auto" />
                )}
            </Dialog>
        </div>
    )
}

export default LeadDocumentUpload
