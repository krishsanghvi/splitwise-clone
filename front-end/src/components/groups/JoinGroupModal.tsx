import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { groupService } from '../../services/groupService'
import { Button } from '../ui/Button'

interface JoinGroupModalProps {
  isOpen: boolean
  onClose: () => void
}

export function JoinGroupModal({ isOpen, onClose }: JoinGroupModalProps) {
  const [inviteCode, setInviteCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const group = await groupService.joinGroup(inviteCode.trim())
      onClose()
      navigate(`/groups/${group.id}`)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Invalid invite code')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Join Group</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="inviteCode" className="block text-sm font-medium text-gray-700 mb-1">
              Invite Code
            </label>
            <input
              id="inviteCode"
              type="text"
              required
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter invite code"
            />
            <p className="text-sm text-gray-600 mt-1">
              Ask a group member for the invite code
            </p>
          </div>

          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || !inviteCode.trim()}
              className="flex-1"
            >
              {loading ? 'Joining...' : 'Join Group'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}