import request from './request'

export const getPlans = (params) => request.get('/plans', { params })
export const createPlan = (data) => request.post('/plans', data)
export const updatePlan = (id, data) => request.put(`/plans/${id}`, data)
export const deletePlan = (id) => request.delete(`/plans/${id}`)
export const updatePlanStatus = (id, status) => request.put(`/plans/${id}/status`, null, { params: { status } })
