import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Notification, Switcher } from '@/components/ui'
import UserForm from './components/UserForm'
import { userApi } from './api/userApi'
import toast from '@/components/ui/toast'

interface UserFormData {
    name: string
    email: string
    phone: string
    role: 'admin' | 'department_head' | 'manager' | 'team_lead' | 'consultant' | 'support'
    password: string
    password2: string
    department_id?: number
    manager_id?: number;
    team_lead_id?: number;
}

const EditUser = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [userDetails, setUserDetails] = useState<UserFormData>({
        name: '',
        email: '',
        phone: '',
        role: 'consultant',
        password: '',
        password2: ''
    })
    const [isActive, setIsActive] = useState(true)

    useEffect(() => {
        if (id) {
            fetchUserDetails()
        }
    }, [id])

    const fetchUserDetails = async () => {
        setLoading(true)
        try {
            const response = await userApi.getUserById(parseInt(id!))
            if (!response) {
                throw new Error('Failed to fetch user details')
            }
            setUserDetails({
                name: response.name,
                email: response.email,
                phone: response.phone,
                role: response.role as 'admin' | 'department_head' | 'manager' | 'team_lead' | 'consultant' | 'support',
                password: '',
                password2: '',
                department_id: response.department_id,
                manager_id: response.manager_id,
                team_lead_id: response.team_lead_id
            })
            setIsActive(response.is_active)
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch user details
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async () => {
        if (!id) return

        // Only validate passwords if both fields have values (password is being changed)
        const isChangingPassword = userDetails.password.trim() !== '' || userDetails.password2.trim() !== ''
        
        if (isChangingPassword) {
            // If one password field is filled but the other isn't
            if (!userDetails.password || !userDetails.password2) {
                toast.push(
                    <Notification title="Error" type="danger">
                        Both password fields are required when changing password
                    </Notification>
                )
                return
            }
            // If both password fields are filled but don't match
            if (userDetails.password !== userDetails.password2) {
                toast.push(
                    <Notification title="Error" type="danger">
                        Passwords do not match
                    </Notification>
                )
                return
            }
        }

        try {
            // Only send fields that can be updated
            const updateData = {
                name: userDetails.name,
                phone: userDetails.phone,
                role: userDetails.role,
                is_active: isActive,
                ...(userDetails.department_id ? { department: userDetails.department_id } : {}),
                // Only include password if it's provided and not empty
                ...(userDetails.password && userDetails.password.trim() !== '' ? { password: userDetails.password } : {})
            }
            await userApi.updateUser(parseInt(id), updateData)
            toast.push(
                <Notification title="Success" type="success">
                    User updated successfully
                </Notification>
            )
            navigate('/users')
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to update user
                </Notification>
            )
        }
    }

    if (loading) {
        return <div>Loading...</div>
    }

    return (
        <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center">
                <h3>Edit User</h3>
                <Button variant="solid" onClick={() => navigate('/users')}>
                    Back to Users
                </Button>
            </div>

            <UserForm
                userDetails={userDetails}
                onUserDetailsChange={setUserDetails}
                isEditMode={true}
            />

            <Card>
                <div className="p-4">
                    <div className="flex items-center justify-between">
                        <h5 className="mb-4 text-lg font-semibold">Account Status</h5>
                        <Switcher
                            checked={isActive}
                            onChange={checked => setIsActive(checked)}
                        />
                    </div>
                    <p className="text-gray-500 text-sm">
                        {isActive 
                            ? 'User account is currently active and can access the system'
                            : 'User account is currently inactive and cannot access the system'
                        }
                    </p>
                </div>
            </Card>

            <div className="flex justify-end gap-2">
                <Button variant="plain" onClick={() => navigate('/users')}>
                    Cancel
                </Button>
                <Button variant="solid" onClick={handleSubmit}>
                    Save Changes
                </Button>
            </div>
        </div>
    )
}

export default EditUser
