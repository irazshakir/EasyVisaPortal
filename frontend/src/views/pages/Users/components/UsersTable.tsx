import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
    Card,
    Input,
    Button,
    Drawer,
    Pagination,
    Avatar,
    Checkbox,
    Notification
} from '@/components/ui'
import { 
    HiOutlineSearch,
    HiOutlineDownload,
    HiOutlinePlus,
    HiOutlineFilter,
    HiOutlinePencil,
    HiOutlineTrash,
    HiOutlineMail,
    HiOutlinePhone
} from 'react-icons/hi'
import { userApi, User } from '../api/userApi'
import toast from '@/components/ui/toast'
import dayjs from 'dayjs'

const UsersTable = () => {
    const navigate = useNavigate()
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [currentPage, setCurrentPage] = useState(1)
    const [selectedRoles, setSelectedRoles] = useState<string[]>([])
    const [loading, setLoading] = useState(false)
    const [users, setUsers] = useState<User[]>([])
    const [totalUsers, setTotalUsers] = useState(0)
    const pageSize = 10

    const fetchUsers = async () => {
        setLoading(true)
        try {
            const response = await userApi.getUsers({
                page: currentPage,
                search: searchQuery,
                role: selectedRoles.length ? selectedRoles[0].toLowerCase() : undefined
            })
            setUsers(response.results)
            setTotalUsers(response.count)
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch users
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchUsers()
    }, [currentPage, searchQuery, selectedRoles])

    const handlePaginationChange = (page: number) => {
        setCurrentPage(page)
    }

    const handleAddNew = () => {
        navigate('/users/new')
    }

    const handleDeleteUser = async (userId: number) => {
        try {
            await userApi.deleteUser(userId)
            toast.push(
                <Notification title="Success" type="success">
                    User deleted successfully
                </Notification>
            )
            fetchUsers() // Refresh the list
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to delete user
                </Notification>
            )
        }
    }

    const getRoleColor = (role: string) => {
        switch (role) {
            case 'admin':
                return 'bg-purple-100 text-purple-600'
            case 'consultant':
                return 'bg-blue-100 text-blue-600'
            case 'support':
                return 'bg-gray-100 text-gray-600'
            default:
                return 'bg-gray-100 text-gray-600'
        }
    }

    const getStatusColor = (isActive: boolean) => {
        return isActive
            ? 'bg-emerald-100 text-emerald-600'
            : 'bg-red-100 text-red-600'
    }

    const handleRoleFilter = (role: string) => {
        setSelectedRoles(prev => {
            if (prev.includes(role)) {
                return prev.filter(r => r !== role)
            }
            return [...prev, role]
        })
    }

    const handleApplyFilters = () => {
        setCurrentPage(1)
        fetchUsers()
        setIsFilterOpen(false)
    }

    const handleResetFilters = () => {
        setSelectedRoles([])
        setCurrentPage(1)
    }

    return (
        <Card>
            <div className="p-4">
                <div className="flex items-center justify-between mb-6">
                    <h4 className="text-lg font-semibold">Users</h4>
                    <div className="flex items-center gap-4">
                        <Button
                            variant="plain"
                            size="sm"
                            icon={<HiOutlineDownload />}
                            className="border border-gray-300 hover:border-gray-400 transition-colors"
                        >
                            Export
                        </Button>
                        <Button
                            variant="solid"
                            size="sm"
                            icon={<HiOutlinePlus />}
                            onClick={handleAddNew}
                        >
                            Add User
                        </Button>
                    </div>
                </div>
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div className="flex-grow">
                        <Input 
                            prefix={<HiOutlineSearch className="text-lg" />}
                            placeholder="Search users..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <Button
                        variant="plain"
                        size="sm"
                        icon={<HiOutlineFilter />}
                        className="border border-gray-300 hover:border-gray-400 transition-colors whitespace-nowrap"
                        onClick={() => setIsFilterOpen(true)}
                    >
                        Filter
                    </Button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-200">
                                <th className="px-4 py-3 text-left">USER</th>
                                <th className="px-4 py-3 text-left">CONTACT</th>
                                <th className="px-4 py-3 text-left">ROLE</th>
                                <th className="px-4 py-3 text-left">STATUS</th>
                                <th className="px-4 py-3 text-left">JOIN DATE</th>
                                <th className="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="text-center py-8">
                                        Loading...
                                    </td>
                                </tr>
                            ) : users.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="text-center py-8">
                                        No users found
                                    </td>
                                </tr>
                            ) : (
                                users.map((user) => (
                                    <tr key={user.id} className="border-b border-gray-200">
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-3">
                                                <Avatar 
                                                    size={32} 
                                                    shape="circle"
                                                >
                                                    {user.name.split(' ').map(n => n[0]).join('')}
                                                </Avatar>
                                                <div>
                                                    <div className="font-semibold">{user.name}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1">
                                                    <HiOutlineMail className="text-gray-400" />
                                                    <span>{user.email}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <HiOutlinePhone className="text-gray-400" />
                                                    <span>{user.phone}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className={`px-2 py-1 rounded-full text-xs inline-block ${getRoleColor(user.role)}`}>
                                                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className={`px-2 py-1 rounded-full text-xs inline-block ${getStatusColor(user.is_active)}`}>
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            {dayjs(user.created_at).format('DD/MM/YYYY')}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2">
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlinePencil />}
                                                    onClick={() => navigate(`/users/${user.id}/edit`)}
                                                />
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlineTrash />}
                                                    onClick={() => handleDeleteUser(user.id)}
                                                />
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                {totalUsers > pageSize && (
                    <div className="mt-4 flex justify-end">
                        <Pagination
                            total={totalUsers}
                            pageSize={pageSize}
                            currentPage={currentPage}
                            onChange={handlePaginationChange}
                        />
                    </div>
                )}
            </div>
            <Drawer
                title="Filter Users"
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                placement="right"
            >
                <div className="p-4">
                    <div className="space-y-6">
                        {/* Role Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Role</h6>
                            <div className="space-y-2">
                                {['Admin', 'Consultant', 'Support'].map(role => (
                                    <div key={role} className="flex items-center">
                                        <Checkbox
                                            checked={selectedRoles.includes(role)}
                                            onChange={() => handleRoleFilter(role)}
                                        >
                                            {role}
                                        </Checkbox>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Filter Actions */}
                        <div className="flex items-center gap-2 mt-6">
                            <Button
                                variant="solid"
                                onClick={handleApplyFilters}
                                className="w-full"
                            >
                                Apply Filters
                            </Button>
                            <Button
                                variant="plain"
                                onClick={handleResetFilters}
                                className="w-full"
                            >
                                Reset
                            </Button>
                        </div>
                    </div>
                </div>
            </Drawer>
        </Card>
    )
}

export default UsersTable
