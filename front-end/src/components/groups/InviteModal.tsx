import { useState } from 'react'
import { type Group } from '../../services/groupService'
import { Button } from '../ui/Button'

interface InviteModalProps {
  isOpen: boolean
  onClose: () => void
  group: Group
}

export function InviteModal({ isOpen, onClose, group }: InviteModalProps) {
  const [copied, setCopied] = useState(false)

  const inviteLink = `${window.location.origin}/join/${group.invite_code}`

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(inviteLink)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Invite Members</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Invite Code
            </label>
            <div className="flex">
              <input
                type="text"
                readOnly
                value={group.invite_code}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md bg-gray-50 text-sm"
              />
              <Button onClick={handleCopy} className="rounded-l-none">
                {copied ? 'Copied!' : 'Copy'}
              </Button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Share Link
            </label>
            <div className="flex">
              <input
                type="text"
                readOnly
                value={inviteLink}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md bg-gray-50 text-sm"
              />
              <Button onClick={handleCopy} className="rounded-l-none">
                {copied ? 'Copied!' : 'Copy'}
              </Button>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-md">
            <p className="text-sm text-blue-800">
              Share this invite code or link with people you want to add to "{group.group_name}".
              They can join by entering the code or clicking the link.
            </p>
          </div>
        </div>

        <div className="flex justify-end pt-4">
          <Button variant="outline" onClick={onClose}>
            Done
          </Button>
        </div>
      </div>
    </div>
  )
}