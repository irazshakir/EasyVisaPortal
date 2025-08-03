import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
    Card,
    Input,
    Button,
    Drawer,
    Pagination,
    Avatar,
    Checkbox,
    Notification,
    Select,
    DatePicker
} from '@/components/ui'
import { 
    HiOutlineSearch,
    HiOutlineDownload,
    HiOutlinePlus,
    HiOutlineFilter,
    HiOutlinePencil,
    HiOutlineTrash,
    HiOutlineMail,
    HiOutlinePhone,
    HiOutlineCalendar
} from 'react-icons/hi'
import { leadApi, Lead } from '../api/apiLead'
import toast from '@/components/ui/toast'
import dayjs from 'dayjs'
import { useAuth } from '@/auth'
import { productApi, Product } from '../../Products/api/apiProduct'
import { statusApi, Status } from '../../Status/api/apiStatus'
import debounce from 'lodash.debounce'
import { useWebSocket } from '@/contexts/WebSocketContext'

const LeadTable = () => {
    const navigate = useNavigate()
    const { user } = useAuth()
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [currentPage, setCurrentPage] = useState(1)
    const [selectedStatus, setSelectedStatus] = useState<string[]>([])
    const [loading, setLoading] = useState(false)
    const [leads, setLeads] = useState<Lead[]>([])
    const [totalLeads, setTotalLeads] = useState(0)
    const pageSize = 10
    const [products, setProducts] = useState<Product[]>([])
    const [statuses, setStatuses] = useState<Status[]>([])
    const [selectedProduct, setSelectedProduct] = useState<number | null>(null)
    const [selectedStatusId, setSelectedStatusId] = useState<number | null>(null)
    const [selectedFollowupDate, setSelectedFollowupDate] = useState<string>('')
    const { lastMessage } = useWebSocket()

    const fetchLeads = async () => {
        setLoading(true)
        try {
            // Prepare search params for name, email, phone
            let searchParams = {
                is_open: selectedStatus.length ? selectedStatus.includes('open') : undefined,
                product: selectedProduct || undefined,
                status: selectedStatusId || undefined,
                followup_date_filter: selectedFollowupDate || undefined,
                page: currentPage,
                page_size: pageSize
            };
            if (searchQuery.trim() !== '') {
                searchParams = {
                    ...searchParams,
                    search: searchQuery
                };
            }
            const response = await leadApi.filterLeads(searchParams)
            setLeads(response.results)
            setTotalLeads(response.count)
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch leads
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    // Debounced fetchLeads
    const debouncedFetchLeads = useCallback(
        debounce(() => {
            fetchLeads();
        }, 400),
        [searchQuery, currentPage, selectedStatus, selectedProduct, selectedStatusId, selectedFollowupDate]
    );

    useEffect(() => {
        debouncedFetchLeads();
        return debouncedFetchLeads.cancel;
    }, [searchQuery, currentPage, selectedStatus, selectedProduct, selectedStatusId, selectedFollowupDate, debouncedFetchLeads]);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const res = await productApi.getProducts({ is_active: true })
                setProducts(res.results)
            } catch {}
        }
        fetchProducts()
    }, [])

    useEffect(() => {
        const fetchStatuses = async () => {
            try {
                const res = await statusApi.getStatuses({ is_active: true })
                setStatuses(res.results)
            } catch {}
        }
        fetchStatuses()
    }, [])

    useEffect(() => {
        if (lastMessage && lastMessage.type === 'lead.assigned') {
            const newLead = lastMessage.lead;
            setLeads(prevLeads => {
                if (prevLeads.some(lead => lead.id === newLead.id)) {
                    return prevLeads;
                }
                return [newLead, ...prevLeads];
            });
            setTotalLeads(prev => prev + 1);
            toast.push(
                <Notification title="New Lead Assigned" type="info">
                    {`Lead "${newLead.name}" assigned to you.`}
                </Notification>
            );
        }
    }, [lastMessage]);

    const handlePaginationChange = (page: number) => {
        setCurrentPage(page)
    }

    const handleAddNew = () => {
        navigate('/leads/new')
    }

    const handleDeleteLead = async (leadId: number) => {
        try {
            await leadApi.deleteLead(leadId)
            toast.push(
                <Notification title="Success" type="success">
                    Lead deleted successfully
                </Notification>
            )
            fetchLeads() // Refresh the list
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to delete lead
                </Notification>
            )
        }
    }

    const getStatusColor = (isOpen: boolean) => {
        return isOpen
            ? 'bg-emerald-100 text-emerald-600'
            : 'bg-red-100 text-red-600'
    }

    const getLeadSourceColor = (source: string | null) => {
        if (!source) return 'bg-gray-100 text-gray-600'
        
        switch (source) {
            case 'youtube':
                return 'bg-red-100 text-red-600'
            case 'g_ads':
                return 'bg-blue-100 text-blue-600'
            case 'facebook_ads':
                return 'bg-indigo-100 text-indigo-600'
            case 'website':
                return 'bg-green-100 text-green-600'
            case 'walk_in':
                return 'bg-purple-100 text-purple-600'
            case 'referral':
                return 'bg-orange-100 text-orange-600'
            case 'tiktok':
                return 'bg-pink-100 text-pink-600'
            default:
                return 'bg-gray-100 text-gray-600'
        }
    }

    const handleStatusFilter = (status: string) => {
        setSelectedStatus(prev => {
            if (prev.includes(status)) {
                return prev.filter(s => s !== status)
            }
            return [...prev, status]
        })
    }

    const handleApplyFilters = () => {
        setCurrentPage(1)
        fetchLeads()
        setIsFilterOpen(false)
    }

    const handleResetFilters = () => {
        setSelectedStatus([])
        setCurrentPage(1)
        setSelectedProduct(null)
        setSelectedStatusId(null)
        setSelectedFollowupDate('')
    }

    const formatFollowupDate = (date: string | null, time: string | null) => {
        if (!date) return '-'
        const formattedDate = dayjs(date).format('DD/MM/YYYY')
        if (time) {
            return `${formattedDate} ${time}`
        }
        return formattedDate
    }

    const getProductName = (productId: number | null) => {
        if (!productId) return '-'
        const product = products.find(p => p.id === productId)
        return product ? product.product_name : productId
    }
    const getStatusName = (statusId: number | null) => {
        if (!statusId) return '-'
        const status = statuses.find(s => s.id === statusId)
        return status ? status.status_name : statusId
    }

    const handleProductFilter = (option: any) => {
        setSelectedProduct(option ? option.value : null)
    }
    const handleStatusIdFilter = (option: any) => {
        setSelectedStatusId(option ? option.value : null)
    }
    const handleFollowupDateFilter = (value: string) => {
        setSelectedFollowupDate(value)
    }

    return (
        <Card>
            <div className="p-4">
                <div className="flex items-center justify-between mb-6">
                    <h4 className="text-lg font-semibold">Leads</h4>
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
                            Add Lead
                        </Button>
                    </div>
                </div>
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div className="flex-grow">
                        <Input 
                            placeholder="Search leads..."
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
                                <th className="px-4 py-3 text-left">LEAD</th>
                                <th className="px-4 py-3 text-left">CONTACT</th>
                                <th className="px-4 py-3 text-left">PRODUCT</th>
                                <th className="px-4 py-3 text-left">STATUS</th>
                                <th className="px-4 py-3 text-left">FOLLOWUP</th>
                                <th className="px-4 py-3 text-left">LEAD STATUS</th>
                                <th className="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={7} className="text-center py-8">
                                        Loading...
                                    </td>
                                </tr>
                            ) : leads.length === 0 ? (
                                <tr>
                                    <td colSpan={7} className="text-center py-8">
                                        No leads found
                                    </td>
                                </tr>
                            ) : (
                                leads.map((lead) => (
                                    <tr key={lead.id} className="border-b border-gray-200">
                                        <td className="px-4 py-3">
                                            <div>
                                                <div className="font-semibold">{lead.name}</div>
                                                {lead.lead_source && (
                                                    <div className={`px-2 py-1 rounded-full text-xs inline-block mt-1 ${getLeadSourceColor(lead.lead_source)}`}>
                                                        {lead.lead_source.replace('_', ' ').toUpperCase()}
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1">
                                                    <HiOutlineMail className="text-gray-400" />
                                                    <span>{lead.email || '-'}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <HiOutlinePhone className="text-gray-400" />
                                                    <span>{lead.phone}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span>{getProductName(lead.product)}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span>{getStatusName(lead.status)}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-1">
                                                <HiOutlineCalendar className="text-gray-400" />
                                                <span>{formatFollowupDate(lead.followup_date, lead.followup_time)}</span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className={`px-2 py-1 rounded-full text-xs inline-block ${getStatusColor(lead.is_open)}`}>
                                                {lead.is_open ? 'Open' : 'Closed'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2">
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlinePencil />}
                                                    onClick={() => navigate(`/leads/${lead.id}/edit`)}
                                                />
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlineTrash />}
                                                    onClick={() => handleDeleteLead(lead.id)}
                                                />
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                {totalLeads > pageSize && (
                    <div className="mt-4 flex justify-end">
                        <Pagination
                            total={totalLeads}
                            pageSize={pageSize}
                            currentPage={currentPage}
                            onChange={handlePaginationChange}
                        />
                    </div>
                )}
            </div>
            <Drawer
                title="Filter Leads"
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                placement="right"
            >
                <div className="p-4">
                    <div className="space-y-6">
                        {/* Status Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Lead Status</h6>
                            <div className="space-y-2">
                                {['Open', 'Closed'].map(status => (
                                    <div key={status} className="flex items-center">
                                        <Checkbox
                                            checked={selectedStatus.includes(status.toLowerCase())}
                                            onChange={() => handleStatusFilter(status.toLowerCase())}
                                        >
                                            {status}
                                        </Checkbox>
                                    </div>
                                ))}
                            </div>
                        </div>
                        {/* Product Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Product</h6>
                            <Select
                                value={selectedProduct ? { value: selectedProduct, label: String(getProductName(selectedProduct)) } : null}
                                onChange={handleProductFilter}
                                options={products.map(p => ({ value: p.id, label: String(p.product_name) }))}
                                isClearable
                                placeholder="Select product"
                            />
                        </div>
                        {/* Status ID Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Status</h6>
                            <Select
                                value={selectedStatusId ? { value: selectedStatusId, label: String(getStatusName(selectedStatusId)) } : null}
                                onChange={handleStatusIdFilter}
                                options={statuses.map(s => ({ value: s.id, label: String(s.status_name) }))}
                                isClearable
                                placeholder="Select status"
                            />
                        </div>
                        {/* Followup Date Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Followup Date</h6>
                            <div className="space-y-2">
                                {[
                                    { value: '', label: 'All' },
                                    { value: 'today', label: 'Today' },
                                    { value: 'this_week', label: 'This Week' },
                                    { value: 'this_month', label: 'This Month' },
                                    { value: 'overdue', label: 'Overdue' },
                                ].map(opt => (
                                    <div key={opt.value} className="flex items-center">
                                        <Checkbox
                                            checked={selectedFollowupDate === opt.value}
                                            onChange={() => handleFollowupDateFilter(opt.value)}
                                        >
                                            {opt.label}
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

export default LeadTable
