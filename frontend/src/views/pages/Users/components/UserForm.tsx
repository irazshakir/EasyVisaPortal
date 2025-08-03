import React, { useState, useEffect } from 'react'
import { Card, Input, Button, Select } from '@/components/ui'
import { userApi, Department, User } from '../api/userApi'

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

interface UserFormProps {
    className?: string
    userDetails: UserFormData
    onUserDetailsChange: (values: UserFormData) => void
    isEditMode?: boolean
}

const UserForm = ({ 
    className = '', 
    userDetails, 
    onUserDetailsChange,
    isEditMode = false 
}: UserFormProps) => {
    const [showPasswordFields, setShowPasswordFields] = useState(false)
    const [departments, setDepartments] = useState<Department[]>([])
    const [managers, setManagers] = useState<User[]>([])
    const [teamLeads, setTeamLeads] = useState<User[]>([])
    const [loadingDepartments, setLoadingDepartments] = useState(false)
    const [loadingManagers, setLoadingManagers] = useState(false)
    const [loadingTeamLeads, setLoadingTeamLeads] = useState(false)

    // Fetch departments on component mount
    useEffect(() => {
        const fetchDepartments = async () => {
            setLoadingDepartments(true)
            try {
                const deps = await userApi.getDepartments()
                setDepartments(deps.filter(dept => dept.is_active))
            } catch (error) {
                console.error('Failed to fetch departments:', error)
            } finally {
                setLoadingDepartments(false)
            }
        }

        fetchDepartments()
    }, [])

    // Fetch managers when department changes
    useEffect(() => {
        if (userDetails.department_id) {
            fetchManagers(userDetails.department_id)
        } else {
            setManagers([])
            setTeamLeads([])
        }
    }, [userDetails.department_id])

    // Fetch team leads when manager changes
    useEffect(() => {
        if (userDetails.manager_id) {
            fetchTeamLeads(userDetails.manager_id)
        } else {
            setTeamLeads([])
        }
    }, [userDetails.manager_id])

    const fetchManagers = async (departmentId: number) => {
        setLoadingManagers(true)
        try {
            const users = await userApi.getUsersByDepartment(departmentId)
            const managers = users.filter(user => user.role === 'manager')
            setManagers(managers)
        } catch (error) {
            console.error('Failed to fetch managers:', error)
        } finally {
            setLoadingManagers(false)
        }
    }

    const fetchTeamLeads = async (managerId: number) => {
        setLoadingTeamLeads(true)
        try {
            const users = await userApi.getUsersByManager(managerId)
            const teamLeads = users.filter(user => user.role === 'team_lead')
            setTeamLeads(teamLeads)
        } catch (error) {
            console.error('Failed to fetch team leads:', error)
        } finally {
            setLoadingTeamLeads(false)
        }
    }

    const handleInputChange = (field: keyof UserFormData, value: string | number) => {
        const newData = {
            ...userDetails,
            [field]: value
        }

        // Clear dependent fields when parent changes
        if (field === 'department_id') {
            newData.manager_id = undefined
            newData.team_lead_id = undefined
        } else if (field === 'manager_id') {
            newData.team_lead_id = undefined
        }

        onUserDetailsChange(newData)
    }

    const handleTogglePassword = () => {
        setShowPasswordFields(!showPasswordFields)
        if (!showPasswordFields) {
            onUserDetailsChange({
                ...userDetails,
                password: '',
                password2: ''
            })
        } else {
            onUserDetailsChange({
                ...userDetails,
                password: '',
                password2: ''
            })
        }
    }

    const shouldShowManagerField = () => {
        return ['manager', 'team_lead', 'consultant', 'support'].includes(userDetails.role)
    }

    const shouldShowTeamLeadField = () => {
        return ['consultant', 'support'].includes(userDetails.role)
    }

    return (
        <Card className={className}>
            <div className="p-4">
                <h5 className="mb-4 text-lg font-semibold">User Information</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="form-label mb-2">Full Name*</label>
                        <Input
                            type="text"
                            value={userDetails.name}
                            onChange={e => handleInputChange('name', e.target.value)}
                            placeholder="Enter full name"
                            required
                        />
                    </div>
                    <div>
                        <label className="form-label mb-2">Email*</label>
                        <Input
                            type="email"
                            value={userDetails.email}
                            onChange={e => handleInputChange('email', e.target.value)}
                            placeholder="Enter email address"
                            required
                            disabled={isEditMode}
                        />
                    </div>
                    <div>
                        <label className="form-label mb-2">Phone Number*</label>
                        <Input
                            type="tel"
                            value={userDetails.phone}
                            onChange={e => handleInputChange('phone', e.target.value)}
                            placeholder="Enter phone number"
                            required
                        />
                    </div>
                    <div>
                        <label className="form-label mb-2">Role*</label>
                        <select
                            className="input input-md h-11 focus:ring-primary-500 focus-within:ring-primary-500 focus-within:border-primary-500 focus:border-primary-500"
                            value={userDetails.role}
                            onChange={e => handleInputChange('role', e.target.value as UserFormData['role'])}
                            required
                        >
                            <option value="" disabled>Select Role</option>
                            <option value="admin">Admin</option>
                            <option value="department_head">Department Head</option>
                            <option value="manager">Manager</option>
                            <option value="team_lead">Team Lead</option>
                            <option value="consultant">Consultant</option>
                            <option value="support">Support</option>
                        </select>
                    </div>
                    <div>
                        <label className="form-label mb-2">Department</label>
                        <select
                            className="input input-md h-11 focus:ring-primary-500 focus-within:ring-primary-500 focus-within:border-primary-500 focus:border-primary-500"
                            value={userDetails.department_id !== undefined ? userDetails.department_id : ''}
                            onChange={e => handleInputChange('department_id', e.target.value ? parseInt(e.target.value) : '')}
                            disabled={loadingDepartments}
                        >
                            <option value="">Select Department (Optional)</option>
                            {departments.map((dept) => (
                                <option key={dept.id} value={dept.id}>
                                    {dept.department_name}
                                </option>
                            ))}
                        </select>
                        {loadingDepartments && (
                            <div className="text-sm text-gray-500 mt-1">Loading departments...</div>
                        )}
                    </div>

                    {shouldShowManagerField() && (
                        <div>
                            <label className="form-label mb-2">Manager</label>
                            <select
                                className="input input-md h-11 focus:ring-primary-500 focus-within:ring-primary-500 focus-within:border-primary-500 focus:border-primary-500"
                                value={userDetails.manager_id !== undefined ? userDetails.manager_id : ''}
                                onChange={e => handleInputChange('manager_id', e.target.value ? parseInt(e.target.value) : '')}
                                disabled={loadingManagers || !userDetails.department_id}
                            >
                                <option value="">Select Manager (Optional)</option>
                                {managers.map((manager) => (
                                    <option key={manager.id} value={manager.id}>
                                        {manager.name}
                                    </option>
                                ))}
                            </select>
                            {loadingManagers && (
                                <div className="text-sm text-gray-500 mt-1">Loading managers...</div>
                            )}
                        </div>
                    )}

                    {shouldShowTeamLeadField() && (
                        <div>
                            <label className="form-label mb-2">Team Lead</label>
                            <select
                                className="input input-md h-11 focus:ring-primary-500 focus-within:ring-primary-500 focus-within:border-primary-500 focus:border-primary-500"
                                value={userDetails.team_lead_id !== undefined ? userDetails.team_lead_id : ''}
                                onChange={e => handleInputChange('team_lead_id', e.target.value ? parseInt(e.target.value) : '')}
                                disabled={loadingTeamLeads || !userDetails.manager_id}
                            >
                                <option value="">Select Team Lead (Optional)</option>
                                {teamLeads.map((teamLead) => (
                                    <option key={teamLead.id} value={teamLead.id}>
                                        {teamLead.name}
                                    </option>
                                ))}
                            </select>
                            {loadingTeamLeads && (
                                <div className="text-sm text-gray-500 mt-1">Loading team leads...</div>
                            )}
                        </div>
                    )}
                </div>

                {isEditMode && (
                    <div className="mt-6">
                        <Button
                            variant="plain"
                            onClick={handleTogglePassword}
                            className="border border-gray-300 hover:border-gray-400 transition-colors"
                        >
                            {showPasswordFields ? 'Cancel Password Change' : 'Change Password'}
                        </Button>
                    </div>
                )}

                {(!isEditMode || showPasswordFields) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        <div>
                            <label className="form-label mb-2">Password*</label>
                            <Input
                                type="password"
                                value={userDetails.password}
                                onChange={e => handleInputChange('password', e.target.value)}
                                placeholder="Enter password"
                                required={!isEditMode}
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Confirm Password*</label>
                            <Input
                                type="password"
                                value={userDetails.password2}
                                onChange={e => handleInputChange('password2', e.target.value)}
                                placeholder="Confirm password"
                                required={!isEditMode}
                            />
                        </div>
                    </div>
                )}
            </div>
        </Card>
    )
}

export default UserForm
