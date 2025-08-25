import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Layout } from '../components/layout/Layout'
import { Button } from '../components/ui/Button'
import { groupService, type Group } from '../services/groupService'
import { memberService, type GroupMember } from '../services/memberService'
import { expenseService, type Expense } from '../services/expenseService'
import { MembersList } from '../components/groups/MembersList'
import { InviteModal } from '../components/groups/InviteModal'
import { EditGroupModal } from '../components/groups/EditGroupModal'
import { AddExpenseModal } from '../components/expenses/AddExpenseModal'
import { ExpenseList } from '../components/expenses/ExpenseList'

export function GroupDetails() {
  const { groupId } = useParams<{ groupId: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [group, setGroup] = useState<Group | null>(null)
  const [members, setMembers] = useState<GroupMember[]>([])
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAddExpenseModal, setShowAddExpenseModal] = useState(false)

  const currentUserMember = members.find(m => m.user_id === user?.id)
  const isAdmin = currentUserMember?.role === 'admin'

  useEffect(() => {
    if (groupId) {
      fetchAllData()
    }
  }, [groupId])

  const fetchAllData = async () => {
    if (!groupId || !user) return

    try {
      setLoading(true)
      await Promise.all([
        fetchGroupData(),
        fetchExpenses()
      ])
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load group data')
    } finally {
      setLoading(false)
    }
  }

  const fetchGroupData = async () => {
    if (!groupId) return

    const [groupData, membersData] = await Promise.all([
      groupService.getGroup(groupId),
      memberService.getGroupMembers(groupId)
    ])
    
    setGroup(groupData)
    setMembers(membersData)
  }

  const fetchExpenses = async () => {
    if (!groupId) return

    try {
      const expensesData = await expenseService.getGroupExpenses(groupId)
      setExpenses(expensesData)
    } catch (error) {
      console.error('Failed to fetch expenses:', error)
    }
  }

  const handleLeaveGroup = async () => {
    if (!groupId || !user || !confirm('Are you sure you want to leave this group?')) return

    try {
      await memberService.removeMember(groupId, user.id)
      navigate('/dashboard')
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to leave group')
    }
  }

  const handleDeleteGroup = async () => {
    if (!groupId || !confirm('Are you sure you want to delete this group? This cannot be undone.')) return

    try {
      await groupService.deleteGroup(groupId)
      navigate('/dashboard')
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to delete group')
    }
  }

  const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0)

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    )
  }

  if (error || !group) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-red-600 mb-4">
            {error || 'Group not found'}
          </div>
          <Button onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{group.group_name}</h1>
            <p className="text-gray-600">{group.group_description}</p>
          </div>
          <div className="flex space-x-3">
            <Button onClick={() => setShowAddExpenseModal(true)}>
              Add Expense
            </Button>
            {isAdmin && (
              <>
                <Button onClick={() => setShowInviteModal(true)}>
                  Invite Members
                </Button>
                <Button variant="outline" onClick={() => setShowEditModal(true)}>
                  Edit Group
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Group Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-gray-900">{members.length}</div>
            <div className="text-sm text-gray-600">Members</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-gray-900">${totalExpenses.toFixed(2)}</div>
            <div className="text-sm text-gray-600">Total Expenses</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-gray-900">
              {new Date(group.created_at).toLocaleDateString()}
            </div>
            <div className="text-sm text-gray-600">Created</div>
          </div>
        </div>

        {/* Expenses Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Expenses</h2>
              <Button onClick={() => setShowAddExpenseModal(true)}>
                Add Expense
              </Button>
            </div>
          </div>
          <div className="p-6">
            <ExpenseList 
              expenses={expenses} 
              onExpenseUpdated={() => {
                fetchExpenses()
                fetchGroupData()
              }}
            />
          </div>
        </div>

        {/* Members Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Members</h2>
          </div>
          <MembersList
            members={members}
            currentUserId={user?.id}
            isAdmin={isAdmin}
            onMemberRemoved={fetchGroupData}
            onRoleUpdated={fetchGroupData}
          />
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-red-600 mb-4">Danger Zone</h2>
          <div className="space-y-3">
            <Button
              variant="outline"
              onClick={handleLeaveGroup}
              className="text-red-600 border-red-300 hover:bg-red-50"
            >
              Leave Group
            </Button>
            {isAdmin && (
              <Button
                variant="outline"
                onClick={handleDeleteGroup}
                className="text-red-600 border-red-300 hover:bg-red-50 ml-3"
              >
                Delete Group
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <InviteModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        group={group}
      />
      <EditGroupModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        group={group}
        onGroupUpdated={(updatedGroup) => {
          setGroup(updatedGroup)
          setShowEditModal(false)
        }}
      />
      <AddExpenseModal
        isOpen={showAddExpenseModal}
        onClose={() => setShowAddExpenseModal(false)}
        groupId={groupId!}
        members={members}
        onExpenseAdded={() => {
          fetchExpenses()
          fetchGroupData()
          setShowAddExpenseModal(false)
        }}
      />
    </Layout>
  )
}