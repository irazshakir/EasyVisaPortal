import React, { useEffect, useState } from 'react'
import { Card, Input, Button, Select, DatePicker, Checkbox } from '@/components/ui'
import { productApi, Product } from '../../Products/api/apiProduct'
import { statusApi, Status } from '../../Status/api/apiStatus'
import { userApi, User } from '../../Users/api/userApi'
import { Lead } from '../api/apiLead'

const LEAD_SOURCE_OPTIONS = [
    { value: 'youtube', label: 'Youtube' },
    { value: 'g_ads', label: 'G Ads' },
    { value: 'facebook_ads', label: 'Facebook Ads' },
    { value: 'website', label: 'Website' },
    { value: 'walk_in', label: 'Walk In' },
    { value: 'referral', label: 'Referral' },
    { value: 'tiktok', label: 'TikTok' },
]

const LEAD_POTENTIAL_OPTIONS = [
    { value: 'A', label: 'A' },
    { value: 'B', label: 'B' },
    { value: 'C', label: 'C' },
]

type OptionType = { value: number | string; label: string }

export interface LeadFormData {
    name: string
    email?: string
    phone: string
    product?: number
    status?: number
    assigned_user?: number
    lead_source?: string
    is_open?: boolean
    followup_date?: string
    followup_time?: string
    lead_potential?: string
    // For Select UI
    productOption?: OptionType | null
    statusOption?: OptionType | null
    assignedUserOption?: OptionType | null
    leadSourceOption?: OptionType | null
    leadPotentialOption?: OptionType | null
}

interface LeadFormProps {
    className?: string
    leadDetails: LeadFormData
    onLeadDetailsChange: (values: LeadFormData) => void
    isEditMode?: boolean
}

const LeadForm = ({
    className = '',
    leadDetails,
    onLeadDetailsChange,
    isEditMode = false
}: LeadFormProps) => {
    const [products, setProducts] = useState<Product[]>([])
    const [statuses, setStatuses] = useState<Status[]>([])
    const [users, setUsers] = useState<User[]>([])
    const [loadingProducts, setLoadingProducts] = useState(false)
    const [loadingStatuses, setLoadingStatuses] = useState(false)
    const [loadingUsers, setLoadingUsers] = useState(false)

    useEffect(() => {
        const fetchProducts = async () => {
            setLoadingProducts(true)
            try {
                const res = await productApi.getProducts({ is_active: true })
                setProducts(res.results)
            } finally {
                setLoadingProducts(false)
            }
        }
        fetchProducts()
    }, [])

    useEffect(() => {
        const fetchStatuses = async () => {
            setLoadingStatuses(true)
            try {
                const res = await statusApi.getStatuses({ is_active: true })
                setStatuses(res.results)
            } finally {
                setLoadingStatuses(false)
            }
        }
        fetchStatuses()
    }, [])

    useEffect(() => {
        const fetchUsers = async () => {
            setLoadingUsers(true)
            try {
                const res = await userApi.getUsers({})
                setUsers(res.results)
            } finally {
                setLoadingUsers(false)
            }
        }
        fetchUsers()
    }, [])

    // Helper to convert string to Date and back
    const getDateValue = (dateStr?: string) => (dateStr ? new Date(dateStr) : undefined)
    const getDateString = (date: Date | null) => (date ? date.toISOString().split('T')[0] : '')

    // Map value to option for Selects
    const getOption = (options: OptionType[], value?: number | string) =>
        options.find(opt => opt.value === value) || null

    // Prepare options
    const productOptions: OptionType[] = products.map(p => ({ value: p.id, label: p.product_name }))
    const statusOptions: OptionType[] = statuses.map(s => ({ value: s.id, label: s.status_name }))
    const userOptions: OptionType[] = users.map(u => ({ value: u.id, label: u.name }))

    // Handlers for Selects
    const handleSelectChange = (field: keyof LeadFormData, option: OptionType | null) => {
        onLeadDetailsChange({
            ...leadDetails,
            [field]: option ? option.value : undefined,
            [`${field}Option`]: option
        })
    }

    const handleInputChange = (field: keyof LeadFormData, value: any) => {
        onLeadDetailsChange({
            ...leadDetails,
            [field]: value
        })
    }

    return (
        <Card className={className}>
            <div className="p-4 space-y-8">
                {/* General Section */}
                <div>
                    <h5 className="mb-4 text-lg font-semibold">General</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="form-label mb-2">Name*</label>
                            <Input
                                type="text"
                                value={leadDetails.name}
                                onChange={e => handleInputChange('name', e.target.value)}
                                placeholder="Enter name"
                                required
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Email</label>
                            <Input
                                type="email"
                                value={leadDetails.email || ''}
                                onChange={e => handleInputChange('email', e.target.value)}
                                placeholder="Enter email address"
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Phone*</label>
                            <Input
                                type="tel"
                                value={leadDetails.phone}
                                onChange={e => handleInputChange('phone', e.target.value)}
                                placeholder="Enter phone number"
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Product Section */}
                <div>
                    <h5 className="mb-4 text-lg font-semibold">Product</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="form-label mb-2">Product</label>
                            <Select<OptionType>
                                value={getOption(productOptions, leadDetails.product)}
                                onChange={option => handleSelectChange('product', option)}
                                isLoading={loadingProducts}
                                placeholder="Select product"
                                options={productOptions}
                                isClearable
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Status</label>
                            <Select<OptionType>
                                value={getOption(statusOptions, leadDetails.status)}
                                onChange={option => handleSelectChange('status', option)}
                                isLoading={loadingStatuses}
                                placeholder="Select status"
                                options={statusOptions}
                                isClearable
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Lead Potential</label>
                            <Select<OptionType>
                                value={getOption(LEAD_POTENTIAL_OPTIONS, leadDetails.lead_potential)}
                                onChange={option => handleSelectChange('lead_potential', option)}
                                options={LEAD_POTENTIAL_OPTIONS}
                                placeholder="Select lead potential"
                                isClearable
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Lead Source</label>
                            <Select<OptionType>
                                value={getOption(LEAD_SOURCE_OPTIONS, leadDetails.lead_source)}
                                onChange={option => handleSelectChange('lead_source', option)}
                                options={LEAD_SOURCE_OPTIONS}
                                placeholder="Select lead source"
                                isClearable
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Assigned User</label>
                            <Select<OptionType>
                                value={getOption(userOptions, leadDetails.assigned_user)}
                                onChange={option => handleSelectChange('assigned_user', option)}
                                isLoading={loadingUsers}
                                placeholder="Select user"
                                options={userOptions}
                                isClearable
                            />
                        </div>
                    </div>
                </div>

                {/* Meetings Section */}
                <div>
                    <h5 className="mb-4 text-lg font-semibold">Meetings</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="form-label mb-2">Followup Date</label>
                            <DatePicker
                                value={getDateValue(leadDetails.followup_date)}
                                onChange={(val: Date | null) => handleInputChange('followup_date', getDateString(val))}
                                placeholder="Select date"
                            />
                        </div>
                        <div>
                            <label className="form-label mb-2">Followup Time</label>
                            <Input
                                type="time"
                                value={leadDetails.followup_time || ''}
                                onChange={e => handleInputChange('followup_time', e.target.value)}
                                placeholder="Select time"
                            />
                        </div>
                        <div className="flex items-center mt-6">
                            <Checkbox
                                checked={!!leadDetails.is_open}
                                onChange={(checked: boolean) => handleInputChange('is_open', checked)}
                            >
                                {leadDetails.is_open ? 'Open' : 'Closed'}
                            </Checkbox>
                        </div>
                    </div>
                </div>
            </div>
        </Card>
    )
}

export default LeadForm
