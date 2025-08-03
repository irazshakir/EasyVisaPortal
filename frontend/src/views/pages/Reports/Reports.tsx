import React from 'react';
import ReportProduct from './components/ReportProduct';
import ReportUser from './components/ReportUser';

const Reports = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <ReportProduct />
                    <ReportUser />
                </div>
            </div>
        </div>
    )
}

export default Reports;
