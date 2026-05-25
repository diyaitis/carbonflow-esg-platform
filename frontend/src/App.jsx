import { useEffect, useState } from 'react'
import { fetchRows, ingestFile, fetchTravel, fetchTenants, updateRowStatus } from './api'

const defaultTenant = 1

function App() {
  const [tenantId, setTenantId] = useState(defaultTenant)
  const [tenants, setTenants] = useState([])
  const [rows, setRows] = useState([])
  const [sourceType, setSourceType] = useState('sap_fuel')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTenants().then(setTenants).catch(() => setTenants([]))
    loadRows()
  }, [])

  async function loadRows() {
    setLoading(true)
    try {
      const data = await fetchRows({ status: 'pending' })
      setRows(data)
    } catch (err) {
      setError('Unable to load rows')
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) {
      setError('Choose a file first')
      return
    }
    setLoading(true)
    try {
      await ingestFile({ tenantId, sourceType, file })
      setFile(null)
      loadRows()
    } catch (err) {
      setError('Upload failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleFetchTravel() {
    setLoading(true)
    try {
      await fetchTravel({ tenantId })
      loadRows()
    } catch (err) {
      setError('Travel fetch failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleReview(rowId, action) {
    setLoading(true)
    try {
      await updateRowStatus(rowId, action)
      loadRows()
    } catch (err) {
      setError('Review failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>Carbonflow ESG</h1>
        <p>Ingest SAP, utility, and corporate travel records for analyst review.</p>
      </header>

      <section className="upload-panel">
        <h2>Ingest source data</h2>
        <form onSubmit={handleUpload}>
          <label>
            Tenant
            <select value={tenantId} onChange={(e) => setTenantId(e.target.value)}>
              {tenants.map((tenant) => (
                <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
              ))}
            </select>
          </label>
          <label>
            Source type
            <select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              <option value="sap_fuel">SAP fuel/procurement CSV</option>
              <option value="utility_electricity">Utility electricity CSV</option>
            </select>
          </label>
          <label>
            Upload file
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>
          <button type="submit" disabled={loading}>Upload</button>
        </form>
        <div className="travel-action">
          <p>Travel data is fetched from a corporate travel platform API.</p>
          <button onClick={handleFetchTravel} disabled={loading}>Fetch travel records</button>
        </div>
      </section>

      <section className="review-panel">
        <h2>Pending rows</h2>
        {error && <div className="error">{error}</div>}
        {loading && <div className="status">Loading…</div>}
        {!loading && rows.length === 0 && <div className="status">No pending rows found.</div>}
        {rows.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Source</th>
                <th>Type</th>
                <th>Scope</th>
                <th>Date</th>
                <th>Quantity</th>
                <th>Emissions</th>
                <th>Suspicious</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className={row.suspicious_reason ? 'flagged' : ''}>
                  <td>{row.id}</td>
                  <td>{row.ingestion_source?.source_type}</td>
                  <td>{row.source_category}</td>
                  <td>{row.scope}</td>
                  <td>{row.activity_date || `${row.period_start} → ${row.period_end}`}</td>
                  <td>{row.quantity} {row.quantity_unit}</td>
                  <td>{row.emissions_kg_co2e?.toFixed(1)}</td>
                  <td>{row.suspicious_reason || '—'}</td>
                  <td>
                    <button onClick={() => handleReview(row.id, 'approve')}>Approve</button>
                    <button onClick={() => handleReview(row.id, 'reject')}>Reject</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}

export default App
