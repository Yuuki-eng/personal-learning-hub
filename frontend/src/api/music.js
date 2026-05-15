import request from './request'

export const searchMusic = (keywords, limit = 30) =>
  request.get('/music/search', { params: { keywords, limit } })
export const getMusicUrl = (id) =>
  request.get('/music/url', { params: { id } })
export const getMusicDetail = (ids) =>
  request.get('/music/detail', { params: { ids } })
export const getLyric = (id) =>
  request.get('/music/lyric', { params: { id } })
export const getRecommend = () => request.get('/music/recommend')
export const getHotSearch = () => request.get('/music/hot')

export const getStreamUrl = (originalUrl) => {
  if (!originalUrl) return ''
  return `/api/music/stream?url=${encodeURIComponent(originalUrl)}`
}

export const getMusicCookieStatus = () => request.get('/music/cookie')
export const setMusicCookie = (cookie) => request.post('/music/cookie', { cookie })
