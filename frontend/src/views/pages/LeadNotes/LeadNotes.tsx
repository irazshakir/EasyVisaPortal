import React from 'react';
import AddLeadNote from './AddLeadNote';

interface LeadNotesProps {
    leadId: number;
}

const LeadNotes: React.FC<LeadNotesProps> = ({ leadId }) => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <AddLeadNote leadId={leadId} />
                </div>
            </div>
        </div>
    );
};

export default LeadNotes;
