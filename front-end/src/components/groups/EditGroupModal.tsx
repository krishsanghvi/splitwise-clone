import { useState } from 'react'
import { groupService, type Group, type CreateGroupData } from '../../services/groupService'
import { Button } from '../ui/Button'

interface EditGroupModalProps {
  isOpen: boolean
  onClose: () => void
  group: Group
  onGroupUpdated: (updatedGroup: Group) => void
}

export function EditGroupModal({ isOpen, onClose, group, onGroupUpdated }: EditGroupModalProps) {
  const [formData, setFormData] = useState<CreateGroupData>({
    group_name: group.group_name,
    group_description: group.group_description
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const updatedGroup = await groupService.updateGroup(group.id, formData)
      onGroupUpdated(updatedGroup)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to update group')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Edit Group</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="group_name" className="block text-sm font-medium text-gray-700 mb-1">
              Group Name
            </label>
            <input
              id="group_name"
              name="group_name"
              type="text"
              required
              value={formData.group_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="group_description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="group_description"
              name="group_description"
              value={formData.group_description}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}