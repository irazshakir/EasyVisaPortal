import ApiService from '@/services/ApiService'

const getToken = () => {
    const auth = localStorage.getItem('auth')
    if (auth) {
        const parsed = JSON.parse(auth)
        return parsed.access_token
    }
    return ''
}

export interface Product {
    id: number
    product_name: string
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface ProductListResponse {
    count: number
    results: Product[]
}

export interface UpdateProductData {
    product_name: string
    is_active: boolean
}

export const productApi = {
    getProducts: async (params?: { page?: number, search?: string, is_active?: boolean }) => {
        const response = await ApiService.fetchDataWithAxios<ProductListResponse>({
            url: '/api/v1/products/',
            method: 'get',
            params
        })
        return response
    },

    getProductById: async (productId: number) => {
        const response = await ApiService.fetchDataWithAxios<Product>({
            url: `/api/v1/products/${productId}/`,
            method: 'get'
        })
        return response
    },

    createProduct: async (data: UpdateProductData) => {
        const response = await ApiService.fetchDataWithAxios<Product>({
            url: '/api/v1/products/',
            method: 'post',
            data
        })
        return response
    },

    updateProduct: async (productId: number, data: UpdateProductData) => {
        const response = await ApiService.fetchDataWithAxios<Product>({
            url: `/api/v1/products/${productId}/`,
            method: 'put',
            data
        })
        return response
    },

    deleteProduct: async (productId: number) => {
        await ApiService.fetchDataWithAxios({
            url: `/api/v1/products/${productId}/`,
            method: 'delete'
        })
    }
}
