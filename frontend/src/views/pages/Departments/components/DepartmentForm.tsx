import React from 'react'
import { Card, Input, Button, Checkbox } from '@/components/ui'

interface DepartmentFormData {
    department_name: string
    is_active: boolean
}

interface DepartmentFormProps {
    className?: string
    departmentDetails: DepartmentFormData
    onDepartmentDetailsChange: (values: DepartmentFormData) => void
    isEditMode?: boolean
}

const DepartmentForm = ({ 
    className = '', 
    departmentDetails, 
    onDepartmentDetailsChange,
    isEditMode = false 
}: DepartmentFormProps) => {

    const handleInputChange = (field: keyof DepartmentFormData, value: string | boolean) => {
        onDepartmentDetailsChange({
            ...departmentDetails,
            [field]: value
        })
    }

    return (
        <Card className={className}>
            <div className="p-4">
                <h5 className="mb-4 text-lg font-semibold">Department Information</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="form-label mb-2">Department Name*</label>
                        <Input
                            type="text"
                            value={departmentDetails.department_name}
                            onChange={e => handleInputChange('department_name', e.target.value)}
                            placeholder="Enter department name"
                            required
                        />
                    </div>
                    <div className="flex items-center">
                        <Checkbox
                            checked={departmentDetails.is_active}
                            onChange={checked => handleInputChange('is_active', checked)}
                        >
                            <span className="ml-2">Active Department</span>
                        </Checkbox>
                    </div>
                </div>

                <div className="mt-6">
                    <p className="text-sm text-gray-500">
                        {isEditMode 
                            ? 'Update the department information below. Changes will be applied immediately.'
                            : 'Create a new department by filling in the information below.'
                        }
                    </p>
                </div>
            </div>
        </Card>
    )
}

export default DepartmentForm
