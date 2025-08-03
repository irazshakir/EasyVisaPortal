import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
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

const EditProduct = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [productDetails, setProductDetails] = useState<ProductFormData>({
        product_name: '',
        is_active: true
    })

    useEffect(() => {
        if (id) {
            fetchProductDetails()
        }
    }, [id])

    const fetchProductDetails = async () => {
        setLoading(true)
        try {
            const response = await productApi.getProductById(parseInt(id!))
            if (!response) {
                throw new Error('Failed to fetch product details')
            }
            setProductDetails({
                product_name: response.product_name,
                is_active: response.is_active
            })
        } catch (error) {
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to fetch product details
                </Notification>
            )
            navigate('/products')
        } finally {
            setLoading(false)
        }
    }

    const handleProductDetailsChange = (details: ProductFormData) => {
        setProductDetails(details)
    }

    const validateForm = () => {
        if (!productDetails.product_name.trim()) {
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
        if (!id || !validateForm()) return

        setLoading(true)
        try {
            await productApi.updateProduct(parseInt(id), productDetails)
            toast.push(
                <Notification title="Success" type="success">
                    Product updated successfully
                </Notification>
            )
            navigate('/products')
        } catch (error: any) {
            const errorMessage = error.response?.data?.message || 'Failed to update product'
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

    if (loading && !productDetails.product_name) {
        return (
            <div className="h-full">
                <div className="container mx-auto p-4">
                    <div className="text-center py-8">
                        Loading...
                    </div>
                </div>
            </div>
        )
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
                        <span className="font-semibold">Edit Product</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    <ProductForm 
                        productDetails={productDetails}
                        onProductDetailsChange={handleProductDetailsChange}
                        isEditMode={true}
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
                            Update Product
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default EditProduct
