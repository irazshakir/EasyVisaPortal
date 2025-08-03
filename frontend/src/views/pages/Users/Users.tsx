import React from 'react'
import UsersTable from './components/UsersTable'

const Users = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <UsersTable />
                </div>
            </div>
        </div>
    )
}

export default Users 