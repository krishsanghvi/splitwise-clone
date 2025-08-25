import api from './api'

export interface GroupMember {
  id: string
  group_id: string
  user_id: string
  role: 'admin' | 'member'
  joined_at: string
  is_active: boolean
  user?: {
    id: string
    email: string
    full_name: string
  }
}

export interface AddMemberData {
  group_id: string
  user_id: string
  role?: 'admin' | 'member'
}

export const memberService = {
  // Get group members
  async getGroupMembers(groupId: string): Promise<GroupMember[]> {
    const response = await api.get(`/group_members/group/${groupId}/members`)
    return response.data
  },

  // Add member to group
  async addMember(data: AddMemberData): Promise<GroupMember> {
    const response = await api.post('/group_members/', data)
    return response.data
  },

  // Remove member from group
  async removeMember(groupId: string, userId: string): Promise<void> {
    await api.delete(`/group_members/group/${groupId}/member/${userId}`)
  },

  // Update member role
  async updateMemberRole(memberId: string, role: 'admin' | 'member'): Promise<GroupMember> {
    const response = await api.put(`/group_members/member/${memberId}/role`, { role })
    return response.data
  },

  // Check membership
  async checkMembership(groupId: string, userId: string): Promise<boolean> {
    try {
      await api.get(`/group_members/group/${groupId}/member/${userId}/check`)
      return true
    } catch {
      return false
    }
  }
}