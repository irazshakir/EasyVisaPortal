import React from 'react'
import LeadDocumentUpload from './AddDocument'

const LeadDocument = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <LeadDocumentUpload />
                </div>
            </div>
        </div>
    )
}

export default LeadDocument
