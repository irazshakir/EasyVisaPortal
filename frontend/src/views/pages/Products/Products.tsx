import React from 'react'
import ProductTable from './components/ProductTable'

const Products = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <ProductTable />
                </div>
            </div>
        </div>
    )
}

export default Products
