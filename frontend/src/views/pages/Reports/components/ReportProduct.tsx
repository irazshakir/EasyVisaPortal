import React, { useEffect, useState, useCallback } from 'react';
import { Card, Spinner, Button } from '@/components/ui';
import Table from '@/components/ui/Table';
import { HiOutlineFilter } from 'react-icons/hi';
import ReportFilter from './ReportFilter';
import { reportsApi, ProductStatusReportResponse, ProductStatusReportParams } from '../api/apiReports';

const { THead, TBody, Tr, Th, Td } = Table;

const ReportProduct = () => {
    const [data, setData] = useState<ProductStatusReportResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [filterParams, setFilterParams] = useState<ProductStatusReportParams>({ range: 'month' });

    const fetchReport = useCallback(async (params: ProductStatusReportParams) => {
        setLoading(true);
        setError(null);
        try {
            const response = await reportsApi.getProductStatusReport(params);
            setData(response);
        } catch (err) {
            setError('Failed to load report data');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchReport(filterParams);
    }, [fetchReport, filterParams]);

    // Handle filter apply from ReportFilter
    const handleFilterApply = (range: { from: Date | null, to: Date | null, quick: string | null }) => {
        if (range.quick) {
            setFilterParams({ range: range.quick as ProductStatusReportParams['range'] });
        } else if (range.from && range.to) {
            setFilterParams({
                start_date: range.from.toISOString().slice(0, 10),
                end_date: range.to.toISOString().slice(0, 10),
            });
        } else {
            setFilterParams({ range: 'month' });
        }
    };

    return (
        <Card>
            <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold">Product x Status Report</h4>
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
                {loading ? (
                    <div className="flex justify-center items-center h-32"><Spinner size="lg" /></div>
                ) : error ? (
                    <div className="text-red-500 text-center py-4">{error}</div>
                ) : data && data.products.length && data.statuses.length ? (
                    <Table>
                        <THead>
                            <Tr>
                                <Th>Product</Th>
                                <Th>New Leads</Th>
                                {/* Ordered status columns */}
                                {(() => {
                                    const desiredOrder = [
                                        'New Query',
                                        'Not Qualified',
                                        'Qualified',
                                        'Lost',
                                        'Final Stage',
                                        'Sale',
                                    ];
                                    // Map status_name to status object
                                    const statusMap = Object.fromEntries(data.statuses.map(s => [s.status_name, s]));
                                    // First, statuses in desired order if present
                                    const ordered = desiredOrder
                                        .map(name => statusMap[name])
                                        .filter(Boolean);
                                    // Then, any remaining statuses
                                    const remaining = data.statuses.filter(s => !desiredOrder.includes(s.status_name));
                                    return [...ordered, ...remaining].map(status => (
                                        <Th key={status.id}>{status.status_name}</Th>
                                    ));
                                })()}
                            </Tr>
                        </THead>
                        <TBody>
                            {data.matrix.map(row => {
                                const newLeads = data.new_leads?.find((nl) => nl.product_id === row.product_id)?.new_leads ?? 0;
                                // Reorder counts to match the header order
                                const desiredOrder = [
                                    'New Query',
                                    'Not Qualified',
                                    'Qualified',
                                    'Lost',
                                    'Final Stage',
                                    'Sale',
                                ];
                                const countMap = Object.fromEntries(row.counts.map(c => [c.status_name, c]));
                                const orderedCounts = [
                                    ...desiredOrder.map(name => countMap[name]).filter(Boolean),
                                    ...row.counts.filter(c => !desiredOrder.includes(c.status_name)),
                                ];
                                return (
                                    <Tr key={row.product_id}>
                                        <Td>{row.product_name}</Td>
                                        <Td className="text-center font-semibold bg-gray-100 text-gray-800">{newLeads}</Td>
                                        {orderedCounts.map(cell => {
                                            let cellClass = 'text-center';
                                            if (cell.status_name === 'Sale') cellClass += ' bg-emerald-100 text-emerald-700 font-semibold';
                                            if (cell.status_name === 'Lost') cellClass += ' bg-red-100 text-red-700 font-semibold';
                                            return (
                                                <Td key={cell.status_id} className={cellClass}>
                                                    {cell.count}
                                                </Td>
                                            );
                                        })}
                                    </Tr>
                                );
                            })}
                        </TBody>
                    </Table>
                ) : (
                    <div className="text-center text-gray-500 py-8">No data found.</div>
                )}
            </div>
            <ReportFilter
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                onApply={handleFilterApply}
            />
        </Card>
    );
};

export default ReportProduct;
