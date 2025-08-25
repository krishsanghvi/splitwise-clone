import api from './api'

export interface Group {
  id: string
  created_by: string
  group_name: string
  group_description: string
  invite_code: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateGroupData {
  group_name: string
  group_description?: string
}

export const groupService = {
  // Create new group
  async createGroup(data: CreateGroupData): Promise<Group> {
    const response = await api.post('/groups/', data)
    return response.data
  },

  // Get user's groups
  async getUserGroups(userId: string): Promise<Group[]> {
    const response = await api.get(`/groups/user/${userId}`)
    return response.data
  },

  // Get group by ID
  async getGroup(groupId: string): Promise<Group> {
    const response = await api.get(`/groups/id/${groupId}`)
    return response.data
  },

  // Join group by invite code
  async joinGroup(inviteCode: string): Promise<Group> {
    const response = await api.get(`/groups/invite/${inviteCode}`)
    return response.data
  },

  // Update group
  async updateGroup(groupId: string, data: Partial<CreateGroupData>): Promise<Group> {
    const response = await api.put(`/groups/${groupId}`, data)
    return response.data
  },

  // Delete group
  async deleteGroup(groupId: string): Promise<void> {
    await api.delete(`/groups/${groupId}`)
  }
}