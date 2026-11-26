/* CivicLens — data fetching hooks */
import { useState, useEffect } from 'react'
import type { CaseRow, CaseFull, WardMetric } from './types'

export const BASE = import.meta.env.BASE_URL

/** Non-hook fetch helper — for use outside React components (e.g. AI chat) */
export async function fetchCaseFull(caseId: string): Promise<CaseFull> {
  const r = await fetch(`${BASE}data/cases/${caseId}.json`)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

export function useCasesIndex() {
  const [data, setData] = useState<CaseRow[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${BASE}data/cases_index.json`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  return { data, error }
}

export function useCaseFull(caseId: string | null) {
  const [data, setData] = useState<CaseFull | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!caseId) return
    setLoading(true)
    setData(null)
    fetch(`${BASE}data/cases/${caseId}.json`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [caseId])

  return { data, loading, error }
}

export function useWardMetrics() {
  const [data, setData] = useState<WardMetric[] | null>(null)

  useEffect(() => {
    fetch(`${BASE}data/ward_metrics.json`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
  }, [])

  return data
}
