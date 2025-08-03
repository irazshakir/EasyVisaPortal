import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DepartmentForm from './components/DepartmentForm'
import { Button } from '@/components/ui'
import { HiChevronRight } from 'react-icons/hi'
import toast from '@/components/ui/toast'
import { departmentApi } from './api/departmentApi'
import { Notification } from '@/components/ui'

interface DepartmentFormData {
    department_name: string
    is_active: boolean
}

const initialFormData: DepartmentFormData = {
    department_name: '',
    is_active: true
}

const AddDepartment = () => {
    const [formData, setFormData] = useState<DepartmentFormData>(initialFormData)
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleDepartmentDetailsChange = (departmentDetails: DepartmentFormData) => {
        setFormData(departmentDetails)
    }

    const validateForm = () => {
        if (!formData.department_name.trim()) {
            toast.push(
                <Notification title="Error" type="danger">
                    Please enter a department name
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
            await departmentApi.createDepartment(formData)
            
            toast.push(
                <Notification title="Success" type="success">
                    Department created successfully
                </Notification>
            )
            navigate('/departments')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to create department'
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
        navigate('/departments')
    }

    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                {/* Breadcrumbs */}
                <div className="mb-4">
                    <div className="flex items-center text-sm">
                        <Link 
                            to="/departments" 
                            className="hover:text-primary-600 transition-colors"
                        >
                            Departments
                        </Link>
                        <HiChevronRight className="mx-2" />
                        <span className="font-semibold">Add New Department</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <DepartmentForm 
                        departmentDetails={formData}
                        onDepartmentDetailsChange={handleDepartmentDetailsChange}
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
                            Create Department
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AddDepartment
