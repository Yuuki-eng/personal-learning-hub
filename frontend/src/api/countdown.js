import request from './request'

export const getCountdowns = () => request.get('/countdowns')
export const createCountdown = (data) => request.post('/countdowns', data)
export const updateCountdown = (id, data) => request.put(`/countdowns/${id}`, data)
export const deleteCountdown = (id) => request.delete(`/countdowns/${id}`)
