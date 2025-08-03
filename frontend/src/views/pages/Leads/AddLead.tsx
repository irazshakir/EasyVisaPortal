import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import LeadForm, { LeadFormData } from './components/LeadForm'
import { Button } from '@/components/ui'
import { HiChevronRight } from 'react-icons/hi'
import toast from '@/components/ui/toast'
import { leadApi } from './api/apiLead'
import { Notification } from '@/components/ui'

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
}

const AddLead = () => {
    const [formData, setFormData] = useState<LeadFormData>(initialFormData)
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

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
        if (!validateForm()) return

        setLoading(true)
        try {
            // Prepare payload (strip Option fields)
            const payload = { ...formData }
            delete payload.productOption
            delete payload.statusOption
            delete payload.assignedUserOption
            delete payload.leadSourceOption

            await leadApi.createLead(payload)
            toast.push(
                <Notification title="Success" type="success">
                    Lead created successfully
                </Notification>
            )
            navigate('/leads')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to create lead'
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

    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                {/* Breadcrumbs */}
                <div className="mb-4">
                    <div className="flex items-center text-sm">
                        <Link 
                            to="/leads" 
                            className="hover:text-primary-600 transition-colors"
                        >
                            Leads
                        </Link>
                        <HiChevronRight className="mx-2" />
                        <span className="font-semibold">Add New Lead</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <LeadForm 
                        leadDetails={formData}
                        onLeadDetailsChange={handleLeadDetailsChange}
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
                            Create Lead
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AddLead
