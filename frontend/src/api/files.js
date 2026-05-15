import request from './request'

export const getFiles = (folderId) => {
  const params = folderId != null ? { folder_id: folderId } : {}
  return request.get('/files', { params })
}
export const uploadFile = (file, folderId) => {
  const formData = new FormData()
  formData.append('file', file)
  if (folderId != null) formData.append('folder_id', folderId)
  return request.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000,
  })
}
export const createFolder = (name, folderId) =>
  request.post('/files/folder', { name, folder_id: folderId })
export const renameFile = (id, name) =>
  request.put(`/files/${id}`, { name })
export const deleteFile = (id) => request.delete(`/files/${id}`)
export const getStorage = () => request.get('/files/storage')
