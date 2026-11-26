/**
 * Local case store — an overlay on top of the static pipeline data.
 *
 * Changes (add / edit / delete) are stored in localStorage so they survive
 * page refresh. The pipeline data itself is never mutated.
 *
 * Data model:
 *   - _added:   CaseRow[] added by the user (new IDs prefixed "LOCAL-")
 *   - _edited:  Record<case_id, Partial<CaseRow>> — field overrides
 *   - _deleted: Set<case_id> — cases hidden from the registry
 */
import {
  createContext, useContext, useEffect, useState, useCallback,
  type ReactNode,
} from 'react'
import type { CaseRow } from './types'

const LS_KEY = 'civiclens_local_overlay'

interface Overlay {
  added:   CaseRow[]
  edited:  Record<string, Partial<CaseRow>>
  deleted: string[]
}

function loadOverlay(): Overlay {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return { added: [], edited: {}, deleted: [] }
}

function saveOverlay(o: Overlay) {
  localStorage.setItem(LS_KEY, JSON.stringify(o))
}

interface LocalCaseStore {
  overlay: Overlay
  addCase:    (c: CaseRow) => void
  editCase:   (id: string, patch: Partial<CaseRow>) => void
  deleteCase: (id: string) => void
  resetOverlay: () => void
  applyOverlay: (base: CaseRow[]) => CaseRow[]
}

const Ctx = createContext<LocalCaseStore | null>(null)

export function LocalCaseProvider({ children }: { children: ReactNode }) {
  const [overlay, setOverlay] = useState<Overlay>(loadOverlay)

  const persist = useCallback((o: Overlay) => {
    setOverlay(o)
    saveOverlay(o)
  }, [])

  const addCase = useCallback((c: CaseRow) => {
    const o = loadOverlay()
    persist({ ...o, added: [...o.added, c] })
  }, [persist])

  const editCase = useCallback((id: string, patch: Partial<CaseRow>) => {
    const o = loadOverlay()
    persist({ ...o, edited: { ...o.edited, [id]: { ...(o.edited[id] ?? {}), ...patch } } })
  }, [persist])

  const deleteCase = useCallback((id: string) => {
    const o = loadOverlay()
    if (!o.deleted.includes(id)) {
      persist({ ...o, deleted: [...o.deleted, id] })
    }
  }, [persist])

  const resetOverlay = useCallback(() => {
    persist({ added: [], edited: {}, deleted: [] })
  }, [persist])

  const applyOverlay = useCallback((base: CaseRow[]): CaseRow[] => {
    const o = loadOverlay()
    const deletedSet = new Set(o.deleted)
    const result = base
      .filter(c => !deletedSet.has(c.case_id))
      .map(c => o.edited[c.case_id] ? { ...c, ...o.edited[c.case_id] } : c)
    return [...result, ...o.added.filter(c => !deletedSet.has(c.case_id))]
  }, [])

  // Reload from localStorage if changed in another tab
  useEffect(() => {
    const handler = () => setOverlay(loadOverlay())
    window.addEventListener('storage', handler)
    return () => window.removeEventListener('storage', handler)
  }, [])

  return (
    <Ctx.Provider value={{ overlay, addCase, editCase, deleteCase, resetOverlay, applyOverlay }}>
      {children}
    </Ctx.Provider>
  )
}

export function useLocalCaseStore() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useLocalCaseStore used outside LocalCaseProvider')
  return ctx
}
