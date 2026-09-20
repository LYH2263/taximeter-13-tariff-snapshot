export class APIError extends Error {
  constructor(message, data) {
    super(message)
    this.data = data
  }
}

async function parseError(r) {
  const text = await r.text()
  let data
  try { data = JSON.parse(text) } catch { data = text }
  const errors = data?.detail?.errors
  throw new APIError(errors?.length ? errors.join('；') : (data?.detail || text || `请求失败 ${r.status}`), data)
}

export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) return parseError(r)
  return r.json()
}
export async function postJSON(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) return parseError(r)
  return r.json()
}
