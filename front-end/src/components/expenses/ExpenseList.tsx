import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { expenseService, type Expense } from '../../services/expenseService'
import { Button } from '../ui/Button'
import { ExpenseCard } from './ExpenseCard'

interface ExpenseListProps {
  expenses: Expense[]
  onExpenseUpdated: () => void
}

export function ExpenseList({ expenses, onExpenseUpdated }: ExpenseListProps) {
  const { user } = useAuth()
  const [filter, setFilter] = useState<'all' | 'paid' | 'owed'>('all')

  const handleDeleteExpense = async (expenseId: string) => {
    if (!confirm('Are you sure you want to delete this expense?')) return

    try {
      await expenseService.deleteExpense(expenseId)
      onExpenseUpdated()
    } catch (error) {
      console.error('Failed to delete expense:', error)
    }
  }

  const filteredExpenses = expenses.filter(expense => {
    if (filter === 'paid') return expense.paid_by === user?.id
    if (filter === 'owed') return expense.paid_by !== user?.id
    return true
  })

  const sortedExpenses = filteredExpenses.sort((a, b) => 
    new Date(b.expense_date).getTime() - new Date(a.expense_date).getTime()
  )

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex space-x-4 border-b border-gray-200">
        {[
          { key: 'all', label: 'All Expenses', count: expenses.length },
          { key: 'paid', label: 'You Paid', count: expenses.filter(e => e.paid_by === user?.id).length },
          { key: 'owed', label: 'You Owe', count: expenses.filter(e => e.paid_by !== user?.id).length }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key as any)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              filter === tab.key
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {/* Expense Cards */}
      {sortedExpenses.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {filter === 'all' ? 'No expenses yet' : `No expenses in this category`}
        </div>
      ) : (
        <div className="space-y-3">
          {sortedExpenses.map(expense => (
            <ExpenseCard
              key={expense.id}
              expense={expense}
              currentUserId={user?.id}
              onDelete={() => handleDeleteExpense(expense.id)}
              canDelete={expense.paid_by === user?.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}