import api from './api'

export interface Category {
  id: string
  name: string
  icon: string
  color: string
  is_default: boolean
}

export const categoryService = {
  // Get all categories
  async getCategories(): Promise<Category[]> {
    const response = await api.get('/categories/')
    return response.data
  },

  // Get default categories
  async getDefaultCategories(): Promise<Category[]> {
    const response = await api.get('/categories/default/list')
    return response.data
  }
}