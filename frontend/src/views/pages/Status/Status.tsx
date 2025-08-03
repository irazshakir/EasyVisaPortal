import React from 'react';
import StatusTable from './components/StatusTable';

const Status = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <StatusTable />
                </div>
            </div>
        </div>
    )
}

export default Status;
