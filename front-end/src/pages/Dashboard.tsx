import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Layout } from '../components/layout/Layout'
import { Button } from '../components/ui/Button'
import { CreateGroupModal } from '../components/groups/CreateGroupModal'
import { JoinGroupModal } from '../components/groups/JoinGroupModal'
import { groupService, type Group } from '../services/groupService'

interface Balance {
  total_owed: number
  total_owing: number
  net_balance: number
}

export function Dashboard() {
  const { user } = useAuth()
  const [groups, setGroups] = useState<Group[]>([])
  const [balance, setBalance] = useState<Balance>({ total_owed: 0, total_owing: 0, net_balance: 0 })
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)

  useEffect(() => {
    fetchUserData()
  }, [user])

  const fetchUserData = async () => {
    if (!user) return
    
    try {
      const userGroups = await groupService.getUserGroups(user.id)
      setGroups(userGroups)
      
      // TODO: Replace with actual balance API call
      setBalance({
        total_owed: 125.50,
        total_owing: 89.25,
        net_balance: 36.25
      })
    } catch (error) {
      console.error('Error fetching user data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.user_metadata?.full_name || user?.email}
          </h1>
          <p className="text-gray-600">Here's an overview of your expenses and groups.</p>
        </div>

        {/* Quick actions */}
        <div className="flex space-x-4">
          <Button onClick={() => setShowCreateModal(true)}>
            Create Group
          </Button>
          <Button variant="outline" onClick={() => setShowJoinModal(true)}>
            Join Group
          </Button>
        </div>

        {/* Balance summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Balance Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                ${balance.total_owed.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">You are owed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                ${balance.total_owing.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">You owe</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${balance.net_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${Math.abs(balance.net_balance).toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">
                Net {balance.net_balance >= 0 ? 'positive' : 'negative'}
              </div>
            </div>
          </div>
        </div>

        {/* Groups section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Your Groups</h2>
              <Link to="/groups">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </div>
          </div>
          
          {groups.length === 0 ? (
            <div className="p-6 text-center">
              <div className="text-gray-500 mb-4">
                <span className="text-4xl">👥</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No groups yet</h3>
              <p className="text-gray-600 mb-4">
                Create your first group to start tracking shared expenses.
              </p>
              <Button onClick={() => setShowCreateModal(true)}>
                Create Your First Group
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {groups.map((group) => (
                <Link
                  key={group.id}
                  to={`/groups/${group.id}`}
                  className="block px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">
                        {group.group_name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {group.group_description}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">
                        Created {new Date(group.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent activity placeholder */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="text-center text-gray-500 py-8">
            <span className="text-4xl mb-4 block">📋</span>
            <p>Recent expenses and settlements will appear here</p>
          </div>
        </div>
      </div>

      {/* Modals */}
      <CreateGroupModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
      <JoinGroupModal
        isOpen={showJoinModal}
        onClose={() => setShowJoinModal(false)}
      />
    </Layout>
  )
}