import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import StatusForm from './components/StatusForm'
import { Button } from '@/components/ui'
import { HiChevronRight } from 'react-icons/hi'
import toast from '@/components/ui/toast'
import { statusApi } from './api/apiStatus'
import { Notification } from '@/components/ui'

interface StatusFormData {
    status_name: string
    is_active: boolean
}

const initialFormData: StatusFormData = {
    status_name: '',
    is_active: true
}

const AddStatus = () => {
    const [formData, setFormData] = useState<StatusFormData>(initialFormData)
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleStatusDetailsChange = (statusDetails: StatusFormData) => {
        setFormData(statusDetails)
    }

    const validateForm = () => {
        if (!formData.status_name.trim()) {
            toast.push(
                <Notification title="Error" type="danger">
                    Please enter a status name
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
            await statusApi.createStatus(formData)
            
            toast.push(
                <Notification title="Success" type="success">
                    Status created successfully
                </Notification>
            )
            navigate('/status')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to create status'
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
        navigate('/status')
    }

    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                {/* Breadcrumbs */}
                <div className="mb-4">
                    <div className="flex items-center text-sm">
                        <Link 
                            to="/status" 
                            className="hover:text-primary-600 transition-colors"
                        >
                            Status
                        </Link>
                        <HiChevronRight className="mx-2" />
                        <span className="font-semibold">Add New Status</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <StatusForm 
                        statusDetails={formData}
                        onStatusDetailsChange={handleStatusDetailsChange}
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
                            Create Status
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AddStatus
