import { type Expense } from '../../services/expenseService'
import { Button } from '../ui/Button'

interface ExpenseCardProps {
  expense: Expense
  currentUserId?: string
  onDelete: () => void
  canDelete: boolean
}

export function ExpenseCard({ expense, currentUserId, onDelete, canDelete }: ExpenseCardProps) {
  const isPaid = expense.paid_by === currentUserId
  const expenseDate = new Date(expense.expense_date).toLocaleDateString()

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            {expense.category && (
              <span className="text-lg">{expense.category.icon}</span>
            )}
            <h3 className="text-sm font-medium text-gray-900">
              {expense.description}
            </h3>
          </div>
          
          <div className="text-xs text-gray-600 mb-2">
            {isPaid ? 'You paid' : `${expense.paid_by_user?.full_name || 'Someone'} paid`} • {expenseDate}
            {expense.category && ` • ${expense.category.name}`}
          </div>

          {expense.notes && (
            <div className="text-xs text-gray-500 mb-2">
              {expense.notes}
            </div>
          )}
        </div>

        <div className="text-right ml-4">
          <div className="text-lg font-semibold text-gray-900">
            ${expense.amount.toFixed(2)}
          </div>
          <div className="text-xs text-gray-500">
            Split {expense.split_method}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center space-x-4 text-xs">
          {isPaid && (
            <span className="text-green-600 font-medium">
              ✓ You paid
            </span>
          )}
          {!isPaid && (
            <span className="text-orange-600 font-medium">
              You owe part of this
            </span>
          )}
        </div>

        {canDelete && (
          <Button
            size="sm"
            variant="outline"
            onClick={onDelete}
            className="text-red-600 border-red-300 hover:bg-red-50"
          >
            Delete
          </Button>
        )}
      </div>
    </div>
  )
}