const NeteaseCloudMusicApi = require('NeteaseCloudMusicApi')
const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = 3000
const COOKIE_FILE = path.join(__dirname, 'cookie.txt')

function readCookie() {
  try {
    if (fs.existsSync(COOKIE_FILE)) {
      return fs.readFileSync(COOKIE_FILE, 'utf-8').trim()
    }
  } catch {}
  return ''
}

function writeCookie(cookie) {
  fs.writeFileSync(COOKIE_FILE, cookie, 'utf-8')
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    res.writeHead(200)
    res.end()
    return
  }

  const url = new URL(req.url, `http://localhost:${PORT}`)
  const pathName = url.pathname
  const params = {}
  for (const [key, value] of url.searchParams.entries()) {
    params[key] = value
  }

  if (pathName === '/') {
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ status: 'ok', service: 'NeteaseCloudMusicApi', hasCookie: !!readCookie() }))
    return
  }

  if (pathName === '/cookie' && req.method === 'GET') {
    const cookie = readCookie()
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ hasCookie: !!cookie, cookieLength: cookie.length }))
    return
  }

  if (pathName === '/cookie' && req.method === 'POST') {
    let body = ''
    req.on('data', chunk => { body += chunk })
    req.on('end', () => {
      try {
        const data = JSON.parse(body)
        if (data.cookie !== undefined) {
          writeCookie(data.cookie)
          res.writeHead(200, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ ok: true, hasCookie: !!data.cookie }))
        } else {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: 'Missing cookie field' }))
        }
      } catch {
        res.writeHead(400, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ error: 'Invalid JSON' }))
      }
    })
    return
  }

  const cookie = readCookie()
  if (cookie) {
    params.cookie = cookie
  }

  const routeMap = {
    '/search': 'search',
    '/song/url': 'song_url',
    '/song/detail': 'song_detail',
    '/lyric': 'lyric',
    '/personalized/newsong': 'personalized_newsong',
    '/playlist/detail': 'playlist_detail',
    '/top/playlist': 'top_playlist',
    '/toplist': 'toplist',
    '/search/hot': 'search_hot',
    '/search/suggest': 'search_suggest',
  }

  const apiPath = pathName.replace(/^\//, '')
  let apiName = routeMap[pathName]

  if (!apiName) {
    apiName = apiPath.replace(/\//g, '_')
  }

  try {
    if (typeof NeteaseCloudMusicApi[apiName] === 'function') {
      const result = await NeteaseCloudMusicApi[apiName](params)
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify(result.body || result))
    } else {
      const moduleMap = NeteaseCloudMusicApi.default || NeteaseCloudMusicApi
      let found = false
      for (const [key, fn] of Object.entries(moduleMap)) {
        if (typeof fn === 'function' && (key === apiName || key === apiPath)) {
          const result = await fn(params)
          res.writeHead(200, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify(result.body || result))
          found = true
          break
        }
      }
      if (!found) {
        res.writeHead(404, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ code: 404, message: `API not found: ${apiName}` }))
      }
    }
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ code: 500, message: err.message }))
  }
})

server.listen(PORT, () => {
  console.log(`Music API server running on http://localhost:${PORT}`)
  console.log(`Cookie configured: ${!!readCookie()}`)
})
