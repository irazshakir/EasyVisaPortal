import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Card,
    Input,
    Button,
    Drawer,
    Pagination,
    Checkbox,
    Notification
} from '@/components/ui';
import {
    HiOutlineSearch,
    HiOutlineDownload,
    HiOutlinePlus,
    HiOutlineFilter,
    HiOutlinePencil,
    HiOutlineTrash,
    HiOutlineCheckCircle
} from 'react-icons/hi';
import toast from '@/components/ui/toast';
import dayjs from 'dayjs';
import { statusApi, Status } from '../api/apiStatus';

const StatusTable = () => {
    const navigate = useNavigate();
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedStatus, setSelectedStatus] = useState<boolean | null>(null);
    const [loading, setLoading] = useState(false);
    const [statuses, setStatuses] = useState<Status[]>([]);
    const [totalStatuses, setTotalStatuses] = useState(0);
    const pageSize = 10;

    const fetchStatuses = async () => {
        setLoading(true);
        try {
            const response = await statusApi.getStatuses({
                page: currentPage,
                search: searchQuery,
                is_active: selectedStatus !== null ? selectedStatus : undefined,
            });
            setStatuses(response.results);
            setTotalStatuses(response.count);
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch statuses
                </Notification>
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatuses();
    }, [currentPage, searchQuery, selectedStatus]);

    const handlePaginationChange = (page: number) => {
        setCurrentPage(page);
    };

    const handleAddNew = () => {
        navigate('/status/new');
    };

    const handleDeleteStatus = async (statusId: number) => {
        try {
            await statusApi.deleteStatus(statusId);
            toast.push(
                <Notification title="Success" type="success">
                    Status deleted successfully
                </Notification>
            );
            fetchStatuses();
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to delete status
                </Notification>
            );
        }
    };

    const getStatusColor = (isActive: boolean) => {
        return isActive
            ? 'bg-emerald-100 text-emerald-600'
            : 'bg-red-100 text-red-600';
    };

    const handleStatusFilter = (status: boolean | null) => {
        setSelectedStatus(status);
    };

    const handleApplyFilters = () => {
        setCurrentPage(1);
        fetchStatuses();
        setIsFilterOpen(false);
    };

    const handleResetFilters = () => {
        setSelectedStatus(null);
        setCurrentPage(1);
    };

    return (
        <Card>
            <div className="p-4">
                <div className="flex items-center justify-between mb-6">
                    <h4 className="text-lg font-semibold">Statuses</h4>
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
                            Add Status
                        </Button>
                    </div>
                </div>
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div className="flex-grow">
                        <Input
                            prefix={<HiOutlineSearch className="text-lg" />}
                            placeholder="Search statuses..."
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
                                <th className="px-4 py-3 text-left">STATUS</th>
                                <th className="px-4 py-3 text-left">ACTIVE</th>
                                <th className="px-4 py-3 text-left">TIMESTAMP</th>
                                <th className="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={4} className="text-center py-8">
                                        Loading...
                                    </td>
                                </tr>
                            ) : statuses.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="text-center py-8">
                                        No statuses found
                                    </td>
                                </tr>
                            ) : (
                                statuses.map((status) => (
                                    <tr key={status.id} className="border-b border-gray-200">
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                                                    <HiOutlineCheckCircle className="text-green-600 text-sm" />
                                                </div>
                                                <div>
                                                    <div className="font-semibold">{status.status_name}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className={`px-2 py-1 rounded-full text-xs inline-block ${getStatusColor(status.is_active)}`}>
                                                {status.is_active ? 'Active' : 'Inactive'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            {dayjs(status.timestamp).format('DD/MM/YYYY')}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2">
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlinePencil />}
                                                    onClick={() => navigate(`/status/${status.id}/edit`)}
                                                />
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlineTrash />}
                                                    onClick={() => handleDeleteStatus(status.id)}
                                                />
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                {totalStatuses > pageSize && (
                    <div className="mt-4 flex justify-end">
                        <Pagination
                            total={totalStatuses}
                            pageSize={pageSize}
                            currentPage={currentPage}
                            onChange={handlePaginationChange}
                        />
                    </div>
                )}
            </div>
            <Drawer
                title="Filter Statuses"
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                placement="right"
            >
                <div className="p-4">
                    <div className="space-y-6">
                        {/* Status Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Active Status</h6>
                            <div className="space-y-2">
                                <div className="flex items-center">
                                    <Checkbox
                                        checked={selectedStatus === true}
                                        onChange={() => handleStatusFilter(true)}
                                    >
                                        Active
                                    </Checkbox>
                                </div>
                                <div className="flex items-center">
                                    <Checkbox
                                        checked={selectedStatus === false}
                                        onChange={() => handleStatusFilter(false)}
                                    >
                                        Inactive
                                    </Checkbox>
                                </div>
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
    );
};

export default StatusTable;
