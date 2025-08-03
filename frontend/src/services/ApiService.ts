import AxiosBase from './axios/AxiosBase'
import type { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

const ApiService = {
    fetchDataWithAxios<Response = unknown, Request = unknown>(
        param: AxiosRequestConfig<Request> & { skipAuthHeader?: boolean },
    ) {
        return new Promise<Response>((resolve, reject) => {
            // Create a new config object without the skipAuthHeader property
            const { skipAuthHeader, ...axiosConfig } = param

            // Use the base axios instance
            AxiosBase(axiosConfig)
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
