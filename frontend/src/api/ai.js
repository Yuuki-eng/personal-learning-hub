import request from './request'

export const getSessions = () => request.get('/ai/sessions')
export const createSession = (title) => request.post('/ai/sessions', { title })
export const getMessages = (sessionId) => request.get(`/ai/sessions/${sessionId}/messages`)
export const deleteSession = (sessionId) => request.delete(`/ai/sessions/${sessionId}`)
export const getAISettings = () => request.get('/ai/settings')
export const updateAISettings = (data) => request.put('/ai/settings', data)
export const getDocuments = () => request.get('/ai/documents')
export const uploadDocument = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/ai/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  })
}
export const deleteDocument = (name) => request.delete(`/ai/documents/${encodeURIComponent(name)}`)
export const getUsageStats = () => request.get('/ai/usage-stats')
export const getLearningGraph = () => request.get('/ai/learning-graph')

export async function streamChat(sessionId, content, onToken, onError, onDone) {
  const backendBase = window.__BACKEND_URL__ || 'http://localhost:8000'
  try {
    const resp = await fetch(`${backendBase}/api/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, content }),
    })
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: '请求失败' }))
      onError(err.detail || '请求失败')
      return
    }
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (payload === '[DONE]') { onDone(); return }
        try {
          const parsed = JSON.parse(payload)
          if (parsed.error) { onError(parsed.error); return }
          if (parsed.content) onToken(parsed.content)
        } catch {}
      }
    }
    onDone()
  } catch (e) {
    onError(e.message)
  }
}
