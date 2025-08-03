import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ProductForm from './components/ProductForm'
import { Button } from '@/components/ui'
import { HiChevronRight } from 'react-icons/hi'
import toast from '@/components/ui/toast'
import { productApi } from './api/apiProduct'
import { Notification } from '@/components/ui'

interface ProductFormData {
    product_name: string
    is_active: boolean
}

const initialFormData: ProductFormData = {
    product_name: '',
    is_active: true
}

const AddProduct = () => {
    const [formData, setFormData] = useState<ProductFormData>(initialFormData)
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleProductDetailsChange = (productDetails: ProductFormData) => {
        setFormData(productDetails)
    }

    const validateForm = () => {
        if (!formData.product_name.trim()) {
            toast.push(
                <Notification title="Error" type="danger">
                    Please enter a product name
                </Notification>
            )
            return false
        }
        return true
    }

    const handleSubmit = async () => {
        if (!validateForm()) return

        setLoading(true)
        try {
            await productApi.createProduct(formData)
            
            toast.push(
                <Notification title="Success" type="success">
                    Product created successfully
                </Notification>
            )
            navigate('/products')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to create product'
            toast.push(
                <Notification title="Error" type="danger">
                    {errorMessage}
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    const handleDiscard = () => {
        navigate('/products')
    }

    return (
        <div className="h-full">
            <div className="container mx-auto p-4">
                {/* Breadcrumbs */}
                <div className="mb-4">
                    <div className="flex items-center text-sm">
                        <Link 
                            to="/products" 
                            className="hover:text-primary-600 transition-colors"
                        >
                            Products
                        </Link>
                        <HiChevronRight className="mx-2" />
                        <span className="font-semibold">Add New Product</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <ProductForm 
                        productDetails={formData}
                        onProductDetailsChange={handleProductDetailsChange}
                    />
                    <div className="flex items-center justify-end gap-2">
                        <Button
                            variant="plain"
                            onClick={handleDiscard}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="solid"
                            onClick={handleSubmit}
                            loading={loading}
                        >
                            Create Product
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AddProduct
