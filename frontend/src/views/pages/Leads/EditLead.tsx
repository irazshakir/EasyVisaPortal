import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import LeadForm, { LeadFormData } from './components/LeadForm'
import { Button } from '@/components/ui'
import { HiChevronRight } from 'react-icons/hi'
import toast from '@/components/ui/toast'
import { leadApi } from './api/apiLead'
import { Notification } from '@/components/ui'
import LeadDocumentUpload from '../LeadDocuments/AddDocument'
import AddLeadNote from '../LeadNotes/AddLeadNote'
import LeadNotes from '../LeadNotes/LeadNotes'

const initialFormData: LeadFormData = {
    name: '',
    email: '',
    phone: '',
    product: undefined,
    status: undefined,
    assigned_user: undefined,
    lead_source: undefined,
    is_open: true,
    followup_date: '',
    followup_time: '',
    lead_potential: undefined,
    leadPotentialOption: null,
}

const EditLead = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState<LeadFormData>(initialFormData)
    const [showAddNoteModal, setShowAddNoteModal] = useState(false)

    useEffect(() => {
        if (id) {
            fetchLeadDetails()
        }
        // eslint-disable-next-line
    }, [id])

    const fetchLeadDetails = async () => {
        setLoading(true)
        try {
            const response = await leadApi.getLeadById(Number(id))
            if (!response) {
                throw new Error('Failed to fetch lead details')
            }
            setFormData({
                name: response.name,
                email: response.email || '',
                phone: response.phone,
                product: response.product || undefined,
                status: response.status || undefined,
                assigned_user: response.assigned_user || undefined,
                lead_source: response.lead_source || undefined,
                is_open: response.is_open,
                followup_date: response.followup_date || '',
                followup_time: response.followup_time || '',
                lead_potential: response.lead_potential || undefined,
                leadPotentialOption: response.lead_potential ? { value: response.lead_potential, label: response.lead_potential } : null,
            })
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch lead details
                </Notification>
            )
            navigate('/leads')
        } finally {
            setLoading(false)
        }
    }

    const handleLeadDetailsChange = (leadDetails: LeadFormData) => {
        setFormData(leadDetails)
    }

    const validateForm = () => {
        if (!formData.name.trim()) {
            toast.push(
                <Notification title="Error" type="danger">
                    Please enter a name
                </Notification>
            )
            return false
        }
        if (!formData.phone.trim()) {
            toast.push(
                <Notification title="Error" type="danger">
                    Please enter a phone number
                </Notification>
            )
            return false
        }
        return true
    }

    const handleSubmit = async () => {
        if (!id || !validateForm()) return

        setLoading(true)
        try {
            // Prepare payload (strip Option fields)
            const payload = { ...formData }
            delete payload.productOption
            delete payload.statusOption
            delete payload.assignedUserOption
            delete payload.leadSourceOption
            delete payload.leadPotentialOption

            await leadApi.updateLead(Number(id), payload)
            toast.push(
                <Notification title="Success" type="success">
                    Lead updated successfully
                </Notification>
            )
            navigate('/leads')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to update lead'
            toast.push(
                <Notification title="Error" type="danger">
                    {errorMessage}
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    const handleDiscard = () => {
        navigate('/leads')
    }

    // Notification handler for document upload/delete
    const handleDocumentNotify = (message: string, type: 'success' | 'danger') => {
        toast.push(
            <Notification title={type === 'success' ? 'Success' : 'Error'} type={type}>
                {message}
            </Notification>
        )
    }

    if (loading && !formData.name) {
        return (
            <div className="h-full">
                <div className="container mx-auto p-4">
                    <div className="text-center py-8">
                        Loading...
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                {/* Add Note Button and Modal */}
                <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center text-sm">
                        <Link 
                            to="/leads" 
                            className="hover:text-primary-600 transition-colors"
                        >
                            Leads
                        </Link>
                        <HiChevronRight className="mx-2" />
                        <span className="font-semibold">Edit Lead</span>
                    </div>
                    <Button
                        variant="solid"
                        onClick={() => setShowAddNoteModal(true)}
                    >
                        Add Note
                    </Button>
                </div>

                {/* Add Note Modal */}
                {showAddNoteModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(46, 45, 45, 0.5)' }}>
                        <div className="bg-white rounded shadow-lg p-6 min-w-[350px] relative">
                            <button
                                className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
                                onClick={() => setShowAddNoteModal(false)}
                                aria-label="Close"
                            >
                                ×
                            </button>
                            <div className="mb-2 font-semibold text-lg">Add Note</div>
                            {id && <LeadNotes leadId={Number(id)} />}
                        </div>
                    </div>
                )}

                <div className="grid gap-4">
                    <LeadForm 
                        leadDetails={formData}
                        onLeadDetailsChange={handleLeadDetailsChange}
                        isEditMode={true}
                    />
                    <div className="flex items-center justify-end gap-2">
                        <Button
                            variant="plain"
                            onClick={handleDiscard}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="solid"
                            onClick={handleSubmit}
                            loading={loading}
                        >
                            Update Lead
                        </Button>
                    </div>
                    {/* Show Lead Documents for this lead below the update button */}
                    {id && <LeadDocumentUpload leadId={Number(id)} onNotify={handleDocumentNotify} />}
                </div>
            </div>
        </div>
    )
}

export default EditLead
