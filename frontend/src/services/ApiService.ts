import AxiosBase from './axios/AxiosBase'
import type { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import axios from 'axios'

const ApiService = {
    fetchDataWithAxios<Response = unknown, Request = unknown>(
        param: AxiosRequestConfig<Request> & { skipAuthHeader?: boolean; withCredentials?: boolean },
    ) {
        return new Promise<Response>((resolve, reject) => {
            // Create a new config object without the custom properties
            const { skipAuthHeader, withCredentials, ...axiosConfig } = param

            // Create a custom axios instance for this request if withCredentials is specified
            let axiosInstance = AxiosBase
            
            if (withCredentials !== undefined) {
                axiosInstance = axios.create({
                    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
                    timeout: 30000,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    withCredentials: withCredentials
                })
            }

            // Use the appropriate axios instance
            axiosInstance(axiosConfig)
                .then((response: AxiosResponse<Response>) => {
                    resolve(response.data)
                })
                .catch((errors: AxiosError) => {
                    console.error('API Error:', errors.response?.data || errors.message)
                    reject(errors)
                })
        })
    },
}

export default ApiService
