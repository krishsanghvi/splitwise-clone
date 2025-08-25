import { useState } from 'react'
import { memberService, type GroupMember } from '../../services/memberService'
import { Button } from '../ui/Button'

interface MembersListProps {
  members: GroupMember[]
  currentUserId?: string
  isAdmin: boolean
  onMemberRemoved: () => void
  onRoleUpdated: () => void
}

export function MembersList({ 
  members, 
  currentUserId, 
  isAdmin, 
  onMemberRemoved, 
  onRoleUpdated 
}: MembersListProps) {
  const [loadingActions, setLoadingActions] = useState<Record<string, boolean>>({})

  const handleRemoveMember = async (member: GroupMember) => {
    if (!confirm(`Remove ${member.user?.full_name || member.user?.email} from the group?`)) return

    setLoadingActions(prev => ({ ...prev, [member.id]: true }))
    try {
      await memberService.removeMember(member.group_id, member.user_id)
      onMemberRemoved()
    } catch (error) {
      console.error('Failed to remove member:', error)
    } finally {
      setLoadingActions(prev => ({ ...prev, [member.id]: false }))
    }
  }

  const handleUpdateRole = async (member: GroupMember) => {
    const newRole = member.role === 'admin' ? 'member' : 'admin'
    
    setLoadingActions(prev => ({ ...prev, [member.id]: true }))
    try {
      await memberService.updateMemberRole(member.id, newRole)
      onRoleUpdated()
    } catch (error) {
      console.error('Failed to update role:', error)
    } finally {
      setLoadingActions(prev => ({ ...prev, [member.id]: false }))
    }
  }

  return (
    <div className="divide-y divide-gray-200">
      {members.map((member) => (
        <div key={member.id} className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
              {(member.user?.full_name || member.user?.email || 'U').charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900">
                {member.user?.full_name || member.user?.email}
                {member.user_id === currentUserId && ' (You)'}
              </div>
              <div className="text-sm text-gray-500">
                {member.role === 'admin' ? 'Administrator' : 'Member'} • 
                Joined {new Date(member.joined_at).toLocaleDateString()}
              </div>
            </div>
          </div>

          {isAdmin && member.user_id !== currentUserId && (
            <div className="flex space-x-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleUpdateRole(member)}
                disabled={loadingActions[member.id]}
              >
                {member.role === 'admin' ? 'Remove Admin' : 'Make Admin'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleRemoveMember(member)}
                disabled={loadingActions[member.id]}
                className="text-red-600 border-red-300 hover:bg-red-50"
              >
                Remove
              </Button>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}