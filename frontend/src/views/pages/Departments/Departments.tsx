import React from 'react'
import DepartmentTable from './components/DepartmentTable'

const Departments = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <DepartmentTable />
                </div>
            </div>
        </div>
    )
}

export default Departments
