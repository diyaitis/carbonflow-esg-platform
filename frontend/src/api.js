const apiBase = '/api'

export async function fetchTenants() {
  const response = await fetch(`${apiBase}/tenants/`)
  if (!response.ok) throw new Error('tenants failed')
  return response.json()
}

export async function fetchRows(params = {}) {
  const query = new URLSearchParams(params).toString()
  const response = await fetch(`${apiBase}/rows/?${query}`)
  if (!response.ok) throw new Error('rows failed')
  const data = await response.json()
  return data.results || data
}

export async function ingestFile({ tenantId, sourceType, file }) {
  const form = new FormData()
  form.append('tenant_id', tenantId)
  form.append('source_type', sourceType)
  form.append('file', file)
  form.append('name', `${sourceType} upload`)
  const response = await fetch(`${apiBase}/ingest/`, {
    method: 'POST',
    body: form,
  })
  if (!response.ok) throw new Error('ingest failed')
  return response.json()
}

export async function fetchTravel({ tenantId }) {
  const response = await fetch(`${apiBase}/travel/fetch/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tenant_id: tenantId }),
  })
  if (!response.ok) throw new Error('travel failed')
  return response.json()
}

export async function updateRowStatus(id, action) {
  const response = await fetch(`${apiBase}/rows/${id}/${action}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reviewed_by: 'analyst@example.com' }),
  })
  if (!response.ok) throw new Error('review failed')
  return response.json()
}
