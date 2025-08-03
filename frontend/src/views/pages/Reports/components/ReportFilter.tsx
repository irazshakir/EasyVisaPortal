import React, { useState } from 'react';
import { Drawer, Button, DatePicker } from '@/components/ui';

const quickRanges = [
    { label: 'Today', value: 'today' },
    { label: 'This Week', value: 'week' },
    { label: 'This Month', value: 'month' },
    { label: 'This Year', value: 'year' },
];

const ReportFilter = ({ isOpen, onClose, onApply }: {
    isOpen: boolean;
    onClose: () => void;
    onApply?: (range: { from: Date | null, to: Date | null, quick: string | null }) => void;
}) => {
    const [from, setFrom] = useState<Date | null>(null);
    const [to, setTo] = useState<Date | null>(null);
    const [selectedQuick, setSelectedQuick] = useState<string | null>(null);

    const handleQuickSelect = (value: string) => {
        setSelectedQuick(value);
        // Optionally set from/to here based on quick range
    };

    const handleApply = () => {
        if (onApply) onApply({ from, to, quick: selectedQuick });
        onClose();
    };

    const handleReset = () => {
        setFrom(null);
        setTo(null);
        setSelectedQuick(null);
    };

    return (
        <Drawer
            title="Filter Reports"
            isOpen={isOpen}
            onClose={onClose}
            placement="right"
        >
            <div className="p-4 space-y-6">
                <div>
                    <h6 className="font-semibold mb-2">Date Range</h6>
                    <div className="flex gap-2">
                        <DatePicker
                            value={from}
                            onChange={setFrom}
                            placeholder="From"
                        />
                        <DatePicker
                            value={to}
                            onChange={setTo}
                            placeholder="To"
                        />
                    </div>
                </div>
                <div>
                    <h6 className="font-semibold mb-2">Quick Options</h6>
                    <div className="flex gap-2 flex-wrap">
                        {quickRanges.map(opt => (
                            <Button
                                key={opt.value}
                                variant={selectedQuick === opt.value ? 'solid' : 'plain'}
                                onClick={() => handleQuickSelect(opt.value)}
                                size="sm"
                            >
                                {opt.label}
                            </Button>
                        ))}
                    </div>
                </div>
                <div className="flex gap-2 mt-6">
                    <Button variant="solid" className="w-full" onClick={handleApply}>Apply</Button>
                    <Button variant="plain" className="w-full" onClick={handleReset}>Reset</Button>
                </div>
            </div>
        </Drawer>
    );
};

export default ReportFilter;
