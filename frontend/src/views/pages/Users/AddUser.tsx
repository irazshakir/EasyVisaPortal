import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import UserForm from './components/UserForm'
import { Button } from '@/components/ui'
import { HiChevronRight } from 'react-icons/hi'
import toast from '@/components/ui/toast'
import ApiService from '@/services/ApiService'
import { Notification } from '@/components/ui'

interface UserFormData {
    name: string
    email: string
    phone: string
    role: 'admin' | 'department_head' | 'manager' | 'team_lead' | 'consultant' | 'support'
    password: string
    password2: string
    department_id?: number
    manager_id?: number
    team_lead_id?: number
}

const initialFormData: UserFormData = {
    name: '',
    email: '',
    phone: '',
    role: 'consultant',
    password: '',
    password2: '',
    department_id: undefined,
    manager_id: undefined,
    team_lead_id: undefined
}

const AddUser = () => {
    const [formData, setFormData] = useState<UserFormData>(initialFormData)
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleUserDetailsChange = (userDetails: UserFormData) => {
        setFormData(userDetails)
    }

    const validateForm = () => {
        if (!formData.name || !formData.email || !formData.phone || !formData.password || !formData.password2) {
            toast.push(
                <Notification title="Error" type="danger">
                    Please fill in all required fields
                </Notification>
            )
            return false
        }
        if (formData.password !== formData.password2) {
            toast.push(
                <Notification title="Error" type="danger">
                    Passwords do not match
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
            // Prepare data for API (exclude password2 and include department_id, manager_id, and team_lead_id)
            const apiData = {
                name: formData.name,
                email: formData.email,
                phone: formData.phone,
                role: formData.role,
                password: formData.password,
                password2: formData.password2,
                ...(formData.department_id ? { department: formData.department_id } : {}),
                ...(formData.manager_id ? { manager: formData.manager_id } : {}),
                ...(formData.team_lead_id ? { team_lead: formData.team_lead_id } : {})
            }

            await ApiService.fetchDataWithAxios({
                url: '/api/v1/auth/register/',
                method: 'post',
                data: apiData
            })
            
            toast.push(
                <Notification title="Success" type="success">
                    User created successfully
                </Notification>
            )
            navigate('/users')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to create user'
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
        navigate('/users')
    }

    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                {/* Breadcrumbs */}
                <div className="mb-4">
                    <div className="flex items-center text-sm">
                        <Link 
                            to="/users" 
                            className="hover:text-primary-600 transition-colors"
                        >
                            Users
                        </Link>
                        <HiChevronRight className="mx-2" />
                        <span className="font-semibold">Add New User</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <UserForm 
                        userDetails={formData}
                        onUserDetailsChange={handleUserDetailsChange}
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
                            Create User
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AddUser
