import request from './request'

export const getBlogs = (params) => request.get('/blogs', { params })
export const getBlog = (id) => request.get(`/blogs/${id}`)
export const createBlog = (data) => request.post('/blogs', data)
export const updateBlog = (id, data) => request.put(`/blogs/${id}`, data)
export const deleteBlog = (id) => request.delete(`/blogs/${id}`)
export const getCategories = () => request.get('/blogs/categories')
export const getTags = () => request.get('/blogs/tags')
