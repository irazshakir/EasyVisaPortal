import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
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

const EditStatus = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [statusDetails, setStatusDetails] = useState<StatusFormData>({
        status_name: '',
        is_active: true
    })

    useEffect(() => {
        if (id) {
            fetchStatusDetails()
        }
    }, [id])

    const fetchStatusDetails = async () => {
        setLoading(true)
        try {
            const response = await statusApi.getStatusById(parseInt(id!))
            if (!response) {
                throw new Error('Failed to fetch status details')
            }
            setStatusDetails({
                status_name: response.status_name,
                is_active: response.is_active
            })
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch status details
                </Notification>
            )
            navigate('/status')
        } finally {
            setLoading(false)
        }
    }

    const handleStatusDetailsChange = (details: StatusFormData) => {
        setStatusDetails(details)
    }

    const validateForm = () => {
        if (!statusDetails.status_name.trim()) {
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
        if (!id || !validateForm()) return

        setLoading(true)
        try {
            await statusApi.updateStatus(parseInt(id), statusDetails)
            toast.push(
                <Notification title="Success" type="success">
                    Status updated successfully
                </Notification>
            )
            navigate('/status')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to update status'
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

    if (loading && !statusDetails.status_name) {
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
                        <span className="font-semibold">Edit Status</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <StatusForm 
                        statusDetails={statusDetails}
                        onStatusDetailsChange={handleStatusDetailsChange}
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
                            Update Status
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default EditStatus
