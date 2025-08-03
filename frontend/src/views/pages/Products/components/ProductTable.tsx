import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
    Card,
    Input,
    Button,
    Drawer,
    Pagination,
    Checkbox,
    Notification
} from '@/components/ui'
import { 
    HiOutlineSearch,
    HiOutlineDownload,
    HiOutlinePlus,
    HiOutlineFilter,
    HiOutlinePencil,
    HiOutlineTrash,
    HiOutlineCube
} from 'react-icons/hi'
import { productApi, Product } from '../api/apiProduct'
import toast from '@/components/ui/toast'
import dayjs from 'dayjs'

const ProductTable = () => {
    const navigate = useNavigate()
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [currentPage, setCurrentPage] = useState(1)
    const [selectedStatus, setSelectedStatus] = useState<boolean | null>(null)
    const [loading, setLoading] = useState(false)
    const [products, setProducts] = useState<Product[]>([])
    const [totalProducts, setTotalProducts] = useState(0)
    const pageSize = 10

    const fetchProducts = async () => {
        setLoading(true)
        try {
            const response = await productApi.getProducts({
                page: currentPage,
                search: searchQuery,
                is_active: selectedStatus !== null ? selectedStatus : undefined
            })
            setProducts(response.results)
            setTotalProducts(response.count)
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch products
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchProducts()
    }, [currentPage, searchQuery, selectedStatus])

    const handlePaginationChange = (page: number) => {
        setCurrentPage(page)
    }

    const handleAddNew = () => {
        navigate('/products/new')
    }

    const handleDeleteProduct = async (productId: number) => {
        try {
            await productApi.deleteProduct(productId)
            toast.push(
                <Notification title="Success" type="success">
                    Product deleted successfully
                </Notification>
            )
            fetchProducts() // Refresh the list
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to delete product
                </Notification>
            )
        }
    }

    const getStatusColor = (isActive: boolean) => {
        return isActive
            ? 'bg-emerald-100 text-emerald-600'
            : 'bg-red-100 text-red-600'
    }

    const handleStatusFilter = (status: boolean | null) => {
        setSelectedStatus(status)
    }

    const handleApplyFilters = () => {
        setCurrentPage(1)
        fetchProducts()
        setIsFilterOpen(false)
    }

    const handleResetFilters = () => {
        setSelectedStatus(null)
        setCurrentPage(1)
    }

    return (
        <Card>
            <div className="p-4">
                <div className="flex items-center justify-between mb-6">
                    <h4 className="text-lg font-semibold">Products</h4>
                    <div className="flex items-center gap-4">
                        <Button
                            variant="plain"
                            size="sm"
                            icon={<HiOutlineDownload />}
                            className="border border-gray-300 hover:border-gray-400 transition-colors"
                        >
                            Export
                        </Button>
                        <Button
                            variant="solid"
                            size="sm"
                            icon={<HiOutlinePlus />}
                            onClick={handleAddNew}
                        >
                            Add Product
                        </Button>
                    </div>
                </div>
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div className="flex-grow">
                        <Input 
                            prefix={<HiOutlineSearch className="text-lg" />}
                            placeholder="Search products..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <Button
                        variant="plain"
                        size="sm"
                        icon={<HiOutlineFilter />}
                        className="border border-gray-300 hover:border-gray-400 transition-colors whitespace-nowrap"
                        onClick={() => setIsFilterOpen(true)}
                    >
                        Filter
                    </Button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-200">
                                <th className="px-4 py-3 text-left">PRODUCT</th>
                                <th className="px-4 py-3 text-left">STATUS</th>
                                <th className="px-4 py-3 text-left">CREATED DATE</th>
                                <th className="px-4 py-3 text-left">UPDATED DATE</th>
                                <th className="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={5} className="text-center py-8">
                                        Loading...
                                    </td>
                                </tr>
                            ) : products.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="text-center py-8">
                                        No products found
                                    </td>
                                </tr>
                            ) : (
                                products.map((product) => (
                                    <tr key={product.id} className="border-b border-gray-200">
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                                    <HiOutlineCube className="text-blue-600 text-sm" />
                                                </div>
                                                <div>
                                                    <div className="font-semibold">{product.product_name}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className={`px-2 py-1 rounded-full text-xs inline-block ${getStatusColor(product.is_active)}`}>
                                                {product.is_active ? 'Active' : 'Inactive'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            {dayjs(product.created_at).format('DD/MM/YYYY')}
                                        </td>
                                        <td className="px-4 py-3">
                                            {dayjs(product.updated_at).format('DD/MM/YYYY')}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2">
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlinePencil />}
                                                    onClick={() => navigate(`/products/${product.id}/edit`)}
                                                />
                                                <Button
                                                    variant="plain"
                                                    size="sm"
                                                    icon={<HiOutlineTrash />}
                                                    onClick={() => handleDeleteProduct(product.id)}
                                                />
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                {totalProducts > pageSize && (
                    <div className="mt-4 flex justify-end">
                        <Pagination
                            total={totalProducts}
                            pageSize={pageSize}
                            currentPage={currentPage}
                            onChange={handlePaginationChange}
                        />
                    </div>
                )}
            </div>
            <Drawer
                title="Filter Products"
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                placement="right"
            >
                <div className="p-4">
                    <div className="space-y-6">
                        {/* Status Filter */}
                        <div>
                            <h6 className="font-semibold mb-3">Status</h6>
                            <div className="space-y-2">
                                <div className="flex items-center">
                                    <Checkbox
                                        checked={selectedStatus === true}
                                        onChange={() => handleStatusFilter(true)}
                                    >
                                        Active
                                    </Checkbox>
                                </div>
                                <div className="flex items-center">
                                    <Checkbox
                                        checked={selectedStatus === false}
                                        onChange={() => handleStatusFilter(false)}
                                    >
                                        Inactive
                                    </Checkbox>
                                </div>
                            </div>
                        </div>

                        {/* Filter Actions */}
                        <div className="flex items-center gap-2 mt-6">
                            <Button
                                variant="solid"
                                onClick={handleApplyFilters}
                                className="w-full"
                            >
                                Apply Filters
                            </Button>
                            <Button
                                variant="plain"
                                onClick={handleResetFilters}
                                className="w-full"
                            >
                                Reset
                            </Button>
                        </div>
                    </div>
                </div>
            </Drawer>
        </Card>
    )
}

export default ProductTable
