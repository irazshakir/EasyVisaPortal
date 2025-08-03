import React from 'react'
import OverviewStats from './components/OverviewStats'
// import RecentOrders from './components/RecentOrders'

const Dashboard = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                <div className="mb-4">
                    <h3>Dashboard Overview</h3>
                    <p className="text-gray-500">Welcome back to your dashboard</p>
                </div>
                <div className="grid gap-4">
                    <OverviewStats />
                    {/* <RecentOrders /> */}
                </div>
            </div>
        </div>
    )
}

export default Dashboard 