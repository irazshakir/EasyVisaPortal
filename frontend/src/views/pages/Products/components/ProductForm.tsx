import React from 'react'
import { Card, Input, Button, Checkbox } from '@/components/ui'

interface ProductFormData {
    product_name: string
    is_active: boolean
}

interface ProductFormProps {
    className?: string
    productDetails: ProductFormData
    onProductDetailsChange: (values: ProductFormData) => void
    isEditMode?: boolean
}

const ProductForm = ({ 
    className = '', 
    productDetails, 
    onProductDetailsChange,
    isEditMode = false 
}: ProductFormProps) => {

    const handleInputChange = (field: keyof ProductFormData, value: string | boolean) => {
        onProductDetailsChange({
            ...productDetails,
            [field]: value
        })
    }

    return (
        <Card className={className}>
            <div className="p-4">
                <h5 className="mb-4 text-lg font-semibold">Product Information</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="form-label mb-2">Product Name*</label>
                        <Input
                            type="text"
                            value={productDetails.product_name}
                            onChange={e => handleInputChange('product_name', e.target.value)}
                            placeholder="Enter product name"
                            required
                        />
                    </div>
                    <div className="flex items-center">
                        <Checkbox
                            checked={productDetails.is_active}
                            onChange={checked => handleInputChange('is_active', checked)}
                        >
                            <span className="ml-2">Active Product</span>
                        </Checkbox>
                    </div>
                </div>

                <div className="mt-6">
                    <p className="text-sm text-gray-500">
                        {isEditMode 
                            ? 'Update the product information below. Changes will be applied immediately.'
                            : 'Create a new product by filling in the information below.'
                        }
                    </p>
                </div>
            </div>
        </Card>
    )
}

export default ProductForm
