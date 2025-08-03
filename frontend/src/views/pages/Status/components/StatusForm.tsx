import React from 'react'
import { Card, Input, Button, Checkbox } from '@/components/ui'

interface StatusFormData {
    status_name: string
    is_active: boolean
}

interface StatusFormProps {
    className?: string
    statusDetails: StatusFormData
    onStatusDetailsChange: (values: StatusFormData) => void
    isEditMode?: boolean
}

const StatusForm = ({
    className = '',
    statusDetails,
    onStatusDetailsChange,
    isEditMode = false
}: StatusFormProps) => {

    const handleInputChange = (field: keyof StatusFormData, value: string | boolean) => {
        onStatusDetailsChange({
            ...statusDetails,
            [field]: value
        })
    }

    return (
        <Card className={className}>
            <div className="p-4">
                <h5 className="mb-4 text-lg font-semibold">Status Information</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="form-label mb-2">Status Name*</label>
                        <Input
                            type="text"
                            value={statusDetails.status_name}
                            onChange={e => handleInputChange('status_name', e.target.value)}
                            placeholder="Enter status name"
                            required
                        />
                    </div>
                    <div className="flex items-center">
                        <Checkbox
                            checked={statusDetails.is_active}
                            onChange={checked => handleInputChange('is_active', checked)}
                        >
                            <span className="ml-2">Active Status</span>
                        </Checkbox>
                    </div>
                </div>

                <div className="mt-6">
                    <p className="text-sm text-gray-500">
                        {isEditMode
                            ? 'Update the status information below. Changes will be applied immediately.'
                            : 'Create a new status by filling in the information below.'
                        }
                    </p>
                </div>
            </div>
        </Card>
    )
}

export default StatusForm
