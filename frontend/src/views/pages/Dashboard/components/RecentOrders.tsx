import React from 'react'
import { Card, Table, Badge } from '@/components/ui'
import { HiOutlineEye } from 'react-icons/hi'

const { Tr, Th, Td, THead, TBody } = Table

const orderStatusMap = {
    'paid': { label: 'Paid', color: 'success' },
    'pending': { label: 'Pending', color: 'warning' },
    'failed': { label: 'Failed', color: 'error' }
} as const

type OrderStatus = keyof typeof orderStatusMap

interface Order {
    id: string
    customer: string
    date: string
    amount: string
    status: OrderStatus
}

const RecentOrders = () => {
    const orders: Order[] = [
        {
            id: '#12345',
            customer: 'John Doe',
            date: '2024-03-12',
            amount: '$234.50',
            status: 'paid'
        },
        {
            id: '#12346',
            customer: 'Jane Smith',
            date: '2024-03-12',
            amount: '$125.00',
            status: 'pending'
        },
        {
            id: '#12347',
            customer: 'Mike Johnson',
            date: '2024-03-11',
            amount: '$545.00',
            status: 'paid'
        },
        {
            id: '#12348',
            customer: 'Sarah Williams',
            date: '2024-03-11',
            amount: '$89.99',
            status: 'failed'
        },
        {
            id: '#12349',
            customer: 'Tom Brown',
            date: '2024-03-10',
            amount: '$332.50',
            status: 'paid'
        }
    ]

    return (
        <Card>
            <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold">Recent Orders</h4>
                    <button className="text-primary hover:underline text-sm">View All</button>
                </div>
                <Table>
                    <THead>
                        <Tr>
                            <Th>Order ID</Th>
                            <Th>Customer</Th>
                            <Th>Date</Th>
                            <Th>Amount</Th>
                            <Th>Status</Th>
                            <Th>Action</Th>
                        </Tr>
                    </THead>
                    <TBody>
                        {orders.map(order => (
                            <Tr key={order.id}>
                                <Td>{order.id}</Td>
                                <Td>{order.customer}</Td>
                                <Td>{order.date}</Td>
                                <Td>{order.amount}</Td>
                                <Td>
                                    <Badge className={`bg-${orderStatusMap[order.status].color}-subtle text-${orderStatusMap[order.status].color}`}>
                                        {orderStatusMap[order.status].label}
                                    </Badge>
                                </Td>
                                <Td>
                                    <button className="text-primary hover:text-primary-deep">
                                        <HiOutlineEye className="text-lg" />
                                    </button>
                                </Td>
                            </Tr>
                        ))}
                    </TBody>
                </Table>
            </div>
        </Card>
    )
}

export default RecentOrders 