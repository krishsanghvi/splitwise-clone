import api from './api'

export interface Expense {
  id: string
  group_id: string
  paid_by: string
  category_id?: string
  amount: number
  description: string
  receipt_url?: string
  notes?: string
  split_method: 'equal' | 'exact' | 'percentage' | 'shares'
  expense_date: string
  created_at: string
  updated_at: string
  paid_by_user?: {
    id: string
    full_name: string
    email: string
  }
  category?: {
    id: string
    name: string
    icon: string
    color: string
  }
}

export interface ExpenseShare {
  id: string
  expense_id: string
  user_id: string
  amount_owed: number
  is_settled: boolean
  created_at: string
  user?: {
    id: string
    full_name: string
    email: string
  }
}

export interface CreateExpenseData {
  group_id: string
  category_id?: string
  amount: number
  description: string
  receipt_url?: string
  notes?: string
  split_method: 'equal' | 'exact' | 'percentage' | 'shares'
  expense_date?: string
  participants?: string[]
  custom_amounts?: Record<string, number>
}

export const expenseService = {
  // Create expense
  async createExpense(data: CreateExpenseData): Promise<Expense> {
    const response = await api.post('/expenses/', data)
    return response.data
  },

  // Get group expenses
  async getGroupExpenses(groupId: string): Promise<Expense[]> {
    const response = await api.get(`/expenses/group/${groupId}`)
    return response.data
  },

  // Get expense by ID
  async getExpense(expenseId: string): Promise<Expense> {
    const response = await api.get(`/expenses/${expenseId}`)
    return response.data
  },

  // Update expense
  async updateExpense(expenseId: string, data: Partial<CreateExpenseData>): Promise<Expense> {
    const response = await api.put(`/expenses/${expenseId}`, data)
    return response.data
  },

  // Delete expense
  async deleteExpense(expenseId: string): Promise<void> {
    await api.delete(`/expenses/${expenseId}`)
  },

  // Get expense shares
  async getExpenseShares(expenseId: string): Promise<ExpenseShare[]> {
    const response = await api.get(`/expense_shares/expense/${expenseId}`)
    return response.data
  }
}