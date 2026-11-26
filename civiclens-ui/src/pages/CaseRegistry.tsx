import { useState, useMemo, useCallback } from 'react'
import { useCasesIndex } from '../data'
import { useNavigate } from 'react-router-dom'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from '@tanstack/react-table'
import type { CaseRow } from '../types'
import { TIER_COLOR, TIER_BG } from '../design'
import { useLocalCaseStore } from '../localCaseStore'

const col = createColumnHelper<CaseRow>()

const TIERS = ['HIGH', 'MEDIUM', 'LOW'] as const

function TierPill({ tier }: { tier: string }) {
  return (
    <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold tracking-wide"
      style={{ color: TIER_COLOR[tier], background: TIER_BG[tier] }}>
      {tier}
    </span>
  )
}

// ── Blank new-case template ──────────────────────────────────────────────────
function blankCase(): Omit<CaseRow, 'case_id'> {
  return {
    cluster_id: '',
    cluster_method: 'manual',
    problem_title: '',
    representative_subcategory: '',
    primary_ward_name: '',
    complaint_count: 0,
    unresolved_rate_pct: 0,
    open_count: 0,
    resolved_count: 0,
    reopened_count: 0,
    priority_tier: 'MEDIUM',
    priority_score: 0,
    ward_join_confidence: 'none',
    responsible_agency: 'BBMP',
    years_active: [],
    date_first_complaint: null,
    date_last_complaint: null,
    centroid_lat: null,
    centroid_lon: null,
    geographic_extent_km: null,
    has_gps: false,
  }
}

// ── CSV parser ───────────────────────────────────────────────────────────────
function parseImportCSV(text: string): { rows: CaseRow[]; errors: string[] } {
  const lines = text.trim().split(/\r?\n/)
  if (lines.length < 2) return { rows: [], errors: ['File has no data rows'] }
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''))
  const rows: CaseRow[] = []
  const errors: string[] = []

  lines.slice(1).forEach((line, li) => {
    if (!line.trim()) return
    // Handle quoted commas
    const cells: string[] = []
    let inQ = false, cur = ''
    for (const ch of line) {
      if (ch === '"') { inQ = !inQ; continue }
      if (ch === ',' && !inQ) { cells.push(cur.trim()); cur = ''; continue }
      cur += ch
    }
    cells.push(cur.trim())

    const get = (key: string) => cells[headers.indexOf(key)] ?? ''
    const title = get('problem_title') || get('title')
    if (!title) { errors.push(`Row ${li + 2}: missing problem_title`); return }

    rows.push({
      case_id: `LOCAL-${Date.now()}-${li}`,
      cluster_id: get('cluster_id') || `manual-${li}`,
      cluster_method: 'manual',
      problem_title: title,
      representative_subcategory: get('representative_subcategory') || get('subcategory') || '',
      primary_ward_name: get('primary_ward_name') || get('ward') || '',
      complaint_count: parseInt(get('complaint_count') || '0', 10) || 0,
      unresolved_rate_pct: parseFloat(get('unresolved_rate_pct') || '0') || 0,
      open_count: parseInt(get('open_count') || '0', 10) || 0,
      resolved_count: parseInt(get('resolved_count') || '0', 10) || 0,
      reopened_count: parseInt(get('reopened_count') || '0', 10) || 0,
      priority_tier: ((['HIGH', 'MEDIUM', 'LOW'].includes(get('priority_tier')) ? get('priority_tier') : 'MEDIUM') as 'HIGH' | 'MEDIUM' | 'LOW'),
      priority_score: parseFloat(get('priority_score') || '0') || 0,
      ward_join_confidence: 'none',
      responsible_agency: get('responsible_agency') || 'Unknown',
      years_active: [],
      date_first_complaint: null,
      date_last_complaint: null,
      centroid_lat: null,
      centroid_lon: null,
      geographic_extent_km: null,
      has_gps: false,
    })
  })
  return { rows, errors }
}

// ── Add / Edit modal ─────────────────────────────────────────────────────────
interface CaseFormProps {
  initial: Partial<CaseRow>
  mode: 'add' | 'edit'
  onSave: (data: Partial<CaseRow>) => void
  onClose: () => void
}

function CaseForm({ initial, mode, onSave, onClose }: CaseFormProps) {
  const [form, setForm] = useState<Partial<CaseRow>>({ ...blankCase(), ...initial })
  const set = (k: keyof CaseRow, v: any) => setForm(f => ({ ...f, [k]: v }))

  const valid = !!(form.problem_title?.trim() && form.primary_ward_name?.trim())

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-[560px] max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-[15px] font-bold text-gray-900">
            {mode === 'add' ? '+ Add New Case' : 'Edit Case'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        <div className="px-6 py-5 space-y-4">
          {/* Problem title */}
          <div>
            <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Problem title <span className="text-red-500">*</span>
            </label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
              value={form.problem_title ?? ''}
              onChange={e => set('problem_title', e.target.value)}
              placeholder="e.g. Recurring Potholes — Whitefield (2022–2024)"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Ward */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Ward <span className="text-red-500">*</span>
              </label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
                value={form.primary_ward_name ?? ''}
                onChange={e => set('primary_ward_name', e.target.value)}
                placeholder="Ward name"
              />
            </div>

            {/* Priority tier */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Priority tier</label>
              <select
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40 bg-white"
                value={form.priority_tier ?? 'MEDIUM'}
                onChange={e => set('priority_tier', e.target.value)}
              >
                {TIERS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          {/* Subcategory */}
          <div>
            <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Problem type / subcategory</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
              value={form.representative_subcategory ?? ''}
              onChange={e => set('representative_subcategory', e.target.value)}
              placeholder="e.g. Pothole Repairs"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Complaint count */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Complaints</label>
              <input type="number" min={0}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
                value={form.complaint_count ?? 0}
                onChange={e => set('complaint_count', parseInt(e.target.value) || 0)}
              />
            </div>
            {/* Unresolved % */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Unresolved %</label>
              <input type="number" min={0} max={100}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
                value={form.unresolved_rate_pct ?? 0}
                onChange={e => set('unresolved_rate_pct', parseFloat(e.target.value) || 0)}
              />
            </div>
            {/* Priority score */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Score (0–1)</label>
              <input type="number" min={0} max={1} step={0.01}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
                value={form.priority_score ?? 0}
                onChange={e => set('priority_score', parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>

          {/* Agency */}
          <div>
            <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Responsible agency</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-400/40"
              value={form.responsible_agency ?? ''}
              onChange={e => set('responsible_agency', e.target.value)}
              placeholder="e.g. BBMP"
            />
          </div>

          {/* Note */}
          {mode === 'add' && (
            <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 leading-relaxed">
              Cases added manually are stored in your browser only (localStorage). They are <strong>not</strong> written to the pipeline data. Clear browser data to remove them.
            </p>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-end gap-2">
          <button onClick={onClose} className="px-4 py-1.5 text-[13px] text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            Cancel
          </button>
          <button
            disabled={!valid}
            onClick={() => { if (valid) { onSave(form); onClose() } }}
            className="px-5 py-1.5 text-[13px] font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
          >
            {mode === 'add' ? 'Add Case' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Import modal ─────────────────────────────────────────────────────────────
function ImportModal({ onClose, onImport }: { onClose: () => void; onImport: (rows: CaseRow[]) => void }) {
  const [result, setResult] = useState<{ rows: CaseRow[]; errors: string[] } | null>(null)
  const [preview, setPreview] = useState(false)

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    const reader = new FileReader()
    reader.onload = ev => {
      const text = ev.target?.result as string
      setResult(parseImportCSV(text))
      setPreview(true)
    }
    reader.readAsText(f)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-[560px] max-h-[80vh] overflow-y-auto">
        <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-[15px] font-bold text-gray-900">Bulk Import via CSV</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        <div className="px-6 py-5">
          <p className="text-[12px] text-gray-600 mb-4 leading-relaxed">
            Upload a CSV with these columns (all optional except <code className="bg-gray-100 px-1 rounded font-mono">problem_title</code>):
          </p>
          <div className="bg-gray-50 rounded-lg px-3 py-2 font-mono text-[11px] text-gray-500 mb-4 overflow-x-auto whitespace-nowrap">
            problem_title, primary_ward_name, representative_subcategory, complaint_count, unresolved_rate_pct, priority_tier, priority_score, responsible_agency
          </div>

          <input type="file" accept=".csv" onChange={handleFile}
            className="text-[13px] text-gray-600 file:mr-3 file:py-1.5 file:px-4 file:rounded-lg file:border file:border-gray-200 file:bg-white file:text-[12px] file:font-semibold file:text-gray-700 hover:file:bg-gray-50"
          />

          {preview && result && (
            <div className="mt-4">
              {result.errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-3">
                  {result.errors.map((e, i) => (
                    <p key={i} className="text-[12px] text-red-700">{e}</p>
                  ))}
                </div>
              )}
              {result.rows.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg px-3 py-2">
                  <p className="text-[12px] text-green-700 font-semibold">{result.rows.length} valid row(s) ready to import</p>
                  <p className="text-[11px] text-green-600 mt-0.5">Preview: {result.rows.slice(0, 3).map(r => r.problem_title).join(' · ')}{result.rows.length > 3 ? '…' : ''}</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-end gap-2">
          <button onClick={onClose} className="px-4 py-1.5 text-[13px] text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            Cancel
          </button>
          <button
            disabled={!result || result.rows.length === 0}
            onClick={() => { if (result?.rows.length) { onImport(result.rows); onClose() } }}
            className="px-5 py-1.5 text-[13px] font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
          >
            Import {result?.rows.length ?? 0} Cases
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function CaseRegistry() {
  const { data: baseCases, error } = useCasesIndex()
  const { overlay, addCase, editCase, deleteCase, resetOverlay, applyOverlay } = useLocalCaseStore()
  const navigate = useNavigate()

  const [sorting, setSorting] = useState<SortingState>([{ id: 'priority_score', desc: true }])
  const [globalFilter, setGlobalFilter] = useState('')
  const [tierFilter, setTierFilter] = useState<string[]>([])
  const [wardFilter, setWardFilter] = useState('')

  const [addOpen, setAddOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<CaseRow | null>(null)
  const [importOpen, setImportOpen] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const cases = useMemo(() => {
    if (!baseCases) return []
    return applyOverlay(baseCases)
  }, [baseCases, applyOverlay, overlay])

  const filteredData = useMemo(() => {
    return cases.filter(c => {
      if (tierFilter.length > 0 && !tierFilter.includes(c.priority_tier)) return false
      if (wardFilter && !c.primary_ward_name.toLowerCase().includes(wardFilter.toLowerCase())) return false
      if (globalFilter) {
        const q = globalFilter.toLowerCase()
        return c.problem_title.toLowerCase().includes(q) ||
          c.primary_ward_name.toLowerCase().includes(q) ||
          c.representative_subcategory.toLowerCase().includes(q)
      }
      return true
    })
  }, [cases, tierFilter, wardFilter, globalFilter])

  const handleImport = useCallback((rows: CaseRow[]) => {
    rows.forEach(r => addCase(r))
  }, [addCase])

  const columns = useMemo(() => [
    col.accessor('priority_tier', {
      header: 'Priority',
      cell: i => <TierPill tier={i.getValue()} />,
    }),
    col.accessor('priority_score', {
      header: 'Score',
      cell: i => <span className="tabular-nums font-semibold text-gray-800">{i.getValue().toFixed(3)}</span>,
    }),
    col.accessor('problem_title', {
      header: 'Case Title',
      cell: i => <span className="text-gray-800 hover:text-blue-700 cursor-pointer truncate block max-w-[280px] font-medium">{i.getValue()}</span>,
    }),
    col.accessor('primary_ward_name', {
      header: 'Ward',
      cell: i => <span className="text-gray-600">{i.getValue()}</span>,
    }),
    col.accessor('representative_subcategory', {
      header: 'Type',
      cell: i => <span className="text-gray-500 truncate block max-w-[160px]">{i.getValue()}</span>,
    }),
    col.accessor('complaint_count', {
      header: 'Complaints',
      cell: i => <span className="tabular-nums text-right block text-gray-700">{i.getValue()}</span>,
    }),
    col.accessor('unresolved_rate_pct', {
      header: 'Unresolved',
      cell: i => <span className="tabular-nums text-right block text-gray-700">{i.getValue()}%</span>,
    }),
    // Actions column — not sortable
    col.display({
      id: 'actions',
      header: '',
      cell: ({ row }) => {
        const c = row.original
        const isLocal = c.case_id.startsWith('LOCAL-')
        return (
          <div className="flex items-center gap-1 justify-end" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setEditTarget(c)}
              className="px-2 py-1 text-[11px] text-gray-500 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
              title="Edit"
            >
              ✎ Edit
            </button>
            {isLocal && (
              <button
                onClick={() => setDeleteConfirm(c.case_id)}
                className="px-2 py-1 text-[11px] text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                title="Delete"
              >
                ✕
              </button>
            )}
            {!isLocal && (
              <button
                onClick={() => setDeleteConfirm(c.case_id)}
                className="px-2 py-1 text-[11px] text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                title="Hide from registry"
              >
                Hide
              </button>
            )}
          </div>
        )
      },
    }),
  ], [])

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 50 } },
  })

  if (error) return <div className="p-10 text-red-600 text-sm font-medium">Failed to load: {error}</div>
  if (!baseCases) return (
    <div className="p-10 text-gray-400 text-sm flex items-center gap-2">
      <span className="animate-spin">⟳</span> Loading…
    </div>
  )

  const pageIndex = table.getState().pagination.pageIndex
  const pageCount = table.getPageCount()
  const localCount = overlay.added.length
  const hiddenCount = overlay.deleted.length
  const editedCount = Object.keys(overlay.edited).length

  return (
    <div className="px-8 py-7">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-[22px] font-bold text-gray-900 tracking-tight">Case Registry</h1>
          <p className="text-[13px] text-gray-500 mt-0.5">
            {filteredData.length} of {cases.length} cases shown
            {(localCount > 0 || hiddenCount > 0 || editedCount > 0) && (
              <span className="ml-2 text-amber-700 bg-amber-50 border border-amber-100 rounded px-2 py-0.5 text-[11px]">
                {localCount > 0 && `${localCount} added`}
                {editedCount > 0 && ` · ${editedCount} edited`}
                {hiddenCount > 0 && ` · ${hiddenCount} hidden`}
              </span>
            )}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2">
          {(localCount > 0 || hiddenCount > 0 || editedCount > 0) && (
            <button
              onClick={() => { if (confirm('Reset all local changes (added, edited, hidden)?')) resetOverlay() }}
              className="text-[12px] border border-red-200 rounded-lg px-4 py-1.5 text-red-600 hover:bg-red-50 bg-white shadow-sm transition-colors"
            >
              ↺ Reset changes
            </button>
          )}
          <button
            onClick={() => setImportOpen(true)}
            className="text-[12px] border border-gray-200 rounded-lg px-4 py-1.5 text-gray-600 hover:bg-white bg-white shadow-sm transition-colors"
          >
            ↑ Import CSV
          </button>
          <button
            onClick={() => {
              const csv = [
                ['case_id','priority_tier','priority_score','problem_title','primary_ward_name','complaint_count','unresolved_rate_pct'].join(','),
                ...filteredData.map(c => [
                  c.case_id, c.priority_tier, c.priority_score,
                  `"${c.problem_title}"`, c.primary_ward_name,
                  c.complaint_count, c.unresolved_rate_pct
                ].join(','))
              ].join('\n')
              const a = document.createElement('a')
              a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
              a.download = 'civiclens_cases.csv'
              a.click()
            }}
            className="text-[12px] border border-gray-200 rounded-lg px-4 py-1.5 text-gray-600 hover:bg-white bg-white shadow-sm transition-colors"
          >
            ↓ Export CSV
          </button>
          <button
            onClick={() => setAddOpen(true)}
            className="text-[12px] font-semibold bg-blue-600 text-white rounded-lg px-4 py-1.5 hover:bg-blue-700 shadow-sm transition-colors"
          >
            + Add Case
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap items-end gap-3 mb-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
        <div className="flex flex-col gap-1">
          <label className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">Search</label>
          <input
            type="search"
            placeholder="Title, ward, type…"
            value={globalFilter}
            onChange={e => setGlobalFilter(e.target.value)}
            className="text-[13px] border border-gray-200 rounded-lg px-3 py-1.5 w-60 bg-white focus:outline-none focus:ring-2 focus:ring-blue-400/40 shadow-sm"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">Ward</label>
          <input
            type="search"
            placeholder="Filter by ward…"
            value={wardFilter}
            onChange={e => setWardFilter(e.target.value)}
            className="text-[13px] border border-gray-200 rounded-lg px-3 py-1.5 w-44 bg-white focus:outline-none focus:ring-2 focus:ring-blue-400/40 shadow-sm"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">Priority</label>
          <div className="flex gap-1.5 items-center h-[34px]">
            {(['HIGH', 'MEDIUM', 'LOW'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTierFilter(prev =>
                  prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]
                )}
                className="px-2.5 py-1 rounded-md text-[11px] font-semibold tracking-wide border transition-all"
                style={tierFilter.includes(t)
                  ? { color: '#fff', background: TIER_COLOR[t], borderColor: TIER_COLOR[t] }
                  : { color: TIER_COLOR[t], background: TIER_BG[t], borderColor: 'transparent' }}
              >
                {t}
              </button>
            ))}
            {tierFilter.length > 0 && (
              <button onClick={() => setTierFilter([])} className="text-[11px] text-gray-400 hover:text-gray-600 px-1 transition-colors">
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-[12px] border-collapse">
            <thead>
              {table.getHeaderGroups().map((hg: { id: string; headers: any[] }) => (
                <tr key={hg.id} className="bg-gray-50 border-b border-gray-200">
                  {hg.headers.map((h: any) => (
                    <th
                      key={h.id}
                      onClick={h.column.getToggleSortingHandler()}
                      className="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap select-none"
                      style={{ cursor: h.column.getCanSort() ? 'pointer' : 'default' }}
                    >
                      <span className="flex items-center gap-1">
                        {flexRender(h.column.columnDef.header, h.getContext())}
                        {h.column.getIsSorted() === 'asc'  && <span className="text-blue-500 text-[10px]">▲</span>}
                        {h.column.getIsSorted() === 'desc' && <span className="text-blue-500 text-[10px]">▼</span>}
                        {!h.column.getIsSorted() && h.column.getCanSort() && <span className="text-gray-300 text-[10px]">⇅</span>}
                      </span>
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row: any, i: number) => {
                const isLocal  = row.original.case_id.startsWith('LOCAL-')
                const isEdited = !!overlay.edited[row.original.case_id]
                return (
                  <tr
                    key={row.id}
                    onClick={() => !isLocal && navigate(`/cases/${row.original.case_id}`)}
                    className={[
                      'border-b border-gray-100 transition-colors',
                      !isLocal ? 'cursor-pointer hover:bg-blue-50' : 'hover:bg-gray-50',
                      isLocal ? 'bg-blue-50/40' : i % 2 === 0 ? 'bg-white' : 'bg-gray-50/30',
                    ].join(' ')}
                  >
                    {row.getVisibleCells().map((cell: any) => (
                      <td key={cell.id} className="px-4 py-2.5 whitespace-nowrap">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                    {isLocal && (
                      <td className="px-2">
                        <span className="text-[9px] font-semibold text-blue-600 bg-blue-100 px-1 rounded">LOCAL</span>
                      </td>
                    )}
                    {isEdited && !isLocal && (
                      <td className="px-2">
                        <span className="text-[9px] font-semibold text-amber-600 bg-amber-100 px-1 rounded">EDITED</span>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-5 py-3 bg-gray-50 border-t border-gray-200 text-[12px] text-gray-500">
          <span>
            Page <strong className="text-gray-700">{pageIndex + 1}</strong> of <strong className="text-gray-700">{pageCount}</strong>
            &ensp;·&ensp;{filteredData.length} cases
          </span>
          <div className="flex items-center gap-1.5">
            <button onClick={() => table.setPageIndex(0)} disabled={!table.getCanPreviousPage()}
              className="px-2.5 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-100 disabled:opacity-30 text-gray-600 transition-colors">«</button>
            <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}
              className="px-3 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-100 disabled:opacity-30 text-gray-600 transition-colors">Prev</button>
            <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}
              className="px-3 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-100 disabled:opacity-30 text-gray-600 transition-colors">Next</button>
            <button onClick={() => table.setPageIndex(pageCount - 1)} disabled={!table.getCanNextPage()}
              className="px-2.5 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-100 disabled:opacity-30 text-gray-600 transition-colors">»</button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {addOpen && (
        <CaseForm
          initial={{}}
          mode="add"
          onSave={data => addCase({
            ...blankCase(),
            ...data,
            case_id: `LOCAL-${Date.now()}`,
            cluster_id: `manual-${Date.now()}`,
            cluster_method: 'manual',
          } as CaseRow)}
          onClose={() => setAddOpen(false)}
        />
      )}

      {editTarget && (
        <CaseForm
          initial={editTarget}
          mode="edit"
          onSave={patch => editCase(editTarget.case_id, patch)}
          onClose={() => setEditTarget(null)}
        />
      )}

      {importOpen && (
        <ImportModal onClose={() => setImportOpen(false)} onImport={handleImport} />
      )}

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-[400px] px-6 py-6">
            <h2 className="text-[15px] font-bold text-gray-900 mb-2">
              {deleteConfirm.startsWith('LOCAL-') ? 'Delete case?' : 'Hide case?'}
            </h2>
            <p className="text-[13px] text-gray-500 leading-relaxed mb-5">
              {deleteConfirm.startsWith('LOCAL-')
                ? 'This locally-added case will be permanently removed.'
                : 'This pipeline case will be hidden from the registry. You can restore it by clicking "Reset changes".'}
            </p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setDeleteConfirm(null)}
                className="px-4 py-1.5 text-[13px] border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                Cancel
              </button>
              <button
                onClick={() => { deleteCase(deleteConfirm); setDeleteConfirm(null) }}
                className="px-4 py-1.5 text-[13px] font-semibold bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                {deleteConfirm.startsWith('LOCAL-') ? 'Delete' : 'Hide'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
