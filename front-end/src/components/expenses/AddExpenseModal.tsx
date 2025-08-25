import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { expenseService, type CreateExpenseData } from '../../services/expenseService'
import { categoryService, type Category } from '../../services/categoryService'
import { type GroupMember } from '../../services/memberService'
import { Button } from '../ui/Button'

interface AddExpenseModalProps {
  isOpen: boolean
  onClose: () => void
  groupId: string
  members: GroupMember[]
  onExpenseAdded: () => void
}

export function AddExpenseModal({ 
  isOpen, 
  onClose, 
  groupId, 
  members, 
  onExpenseAdded 
}: AddExpenseModalProps) {
  const { user } = useAuth()
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState<CreateExpenseData>({
    group_id: groupId,
    amount: 0,
    description: '',
    split_method: 'equal',
    expense_date: new Date().toISOString().split('T')[0],
    participants: members.map(m => m.user_id)
  })

  const [customAmounts, setCustomAmounts] = useState<Record<string, number>>({})

  useEffect(() => {
    if (isOpen) {
      fetchCategories()
    }
  }, [isOpen])

  const fetchCategories = async () => {
    try {
      const cats = await categoryService.getDefaultCategories()
      setCategories(cats)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return

    setLoading(true)
    setError('')

    try {
      const expenseData = {
        ...formData,
        ...(formData.split_method === 'exact' && { custom_amounts: customAmounts })
      }

      await expenseService.createExpense(expenseData)
      onExpenseAdded()
      onClose()
      resetForm()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to create expense')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      group_id: groupId,
      amount: 0,
      description: '',
      split_method: 'equal',
      expense_date: new Date().toISOString().split('T')[0],
      participants: members.map(m => m.user_id)
    })
    setCustomAmounts({})
    setError('')
  }

  const handleParticipantToggle = (userId: string) => {
    setFormData(prev => ({
      ...prev,
      participants: prev.participants?.includes(userId)
        ? prev.participants.filter(id => id !== userId)
        : [...(prev.participants || []), userId]
    }))
  }

  const handleCustomAmountChange = (userId: string, amount: number) => {
    setCustomAmounts(prev => ({
      ...prev,
      [userId]: amount
    }))
  }

  const totalCustomAmount = Object.values(customAmounts).reduce((sum, amount) => sum + amount, 0)
  const remainingAmount = formData.amount - totalCustomAmount

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Add Expense</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <input
                type="text"
                required
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="What was this expense for?"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Amount *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                required
                value={formData.amount || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={formData.category_id || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, category_id: e.target.value || undefined }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select category</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.icon} {category.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <input
                type="date"
                value={formData.expense_date}
                onChange={(e) => setFormData(prev => ({ ...prev, expense_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Split Method */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Split Method
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="equal"
                  checked={formData.split_method === 'equal'}
                  onChange={(e) => setFormData(prev => ({ ...prev, split_method: e.target.value as any }))}
                  className="mr-2"
                />
                Equal Split
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="exact"
                  checked={formData.split_method === 'exact'}
                  onChange={(e) => setFormData(prev => ({ ...prev, split_method: e.target.value as any }))}
                  className="mr-2"
                />
                Custom Amounts
              </label>
            </div>
          </div>

          {/* Participants */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Split Between ({formData.participants?.length || 0} people)
            </label>
            <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-200 rounded-md p-3">
              {members.map(member => {
                const isSelected = formData.participants?.includes(member.user_id) || false
                const memberAmount = customAmounts[member.user_id] || 0
                
                return (
                  <div key={member.id} className="flex items-center justify-between">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleParticipantToggle(member.user_id)}
                        className="mr-3"
                      />
                      <span className="text-sm">
                        {member.user?.full_name || member.user?.email}
                        {member.user_id === user?.id && ' (You)'}
                      </span>
                    </label>
                    
                    {formData.split_method === 'exact' && isSelected && (
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={memberAmount || ''}
                        onChange={(e) => handleCustomAmountChange(member.user_id, parseFloat(e.target.value) || 0)}
                        className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="0.00"
                      />
                    )}
                    
                    {formData.split_method === 'equal' && isSelected && (
                      <span className="text-sm text-gray-600">
                        ${((formData.amount || 0) / (formData.participants?.length || 1)).toFixed(2)}
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
            
            {formData.split_method === 'exact' && (
              <div className="mt-2 text-sm">
                <span className={remainingAmount === 0 ? 'text-green-600' : 'text-red-600'}>
                  Total: ${totalCustomAmount.toFixed(2)} / ${formData.amount.toFixed(2)}
                  {remainingAmount !== 0 && ` (${remainingAmount > 0 ? 'Remaining' : 'Over'}: $${Math.abs(remainingAmount).toFixed(2)})`}
                </span>
              </div>
            )}
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Additional notes about this expense..."
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="flex space-x-3 pt-4">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading || !formData.description || formData.amount <= 0 || (formData.split_method === 'exact' && remainingAmount !== 0)}
              className="flex-1"
            >
              {loading ? 'Creating...' : 'Create Expense'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}