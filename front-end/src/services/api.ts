import axios, { type AxiosRequestConfig, type AxiosResponse, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { supabase } from '../lib/supabase'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const api = axios.create({
    baseURL: API_BASE_URL,
})

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`
    }
    return config
})

api.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError) => {
        if (error.response?.status === 401) {
            await supabase.auth.signOut()
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
