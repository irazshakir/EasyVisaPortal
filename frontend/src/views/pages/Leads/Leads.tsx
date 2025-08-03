import React from 'react'
import LeadTable from './components/LeadTable'

const Leads = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <LeadTable />
                </div>
            </div>
        </div>
    )
}

export default Leads
