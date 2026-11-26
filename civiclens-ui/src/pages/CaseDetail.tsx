import { useParams, useNavigate } from 'react-router-dom'
import { useCaseFull } from '../data'
import { useEffect, useRef, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { TIER_COLOR, TIER_BG, FACTOR_LABEL, fmt } from '../design'
import type { CaseFull } from '../types'
import L from 'leaflet'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const STATUS_COLOR: Record<string, string> = {
  open: '#EF4444', resolved: '#22C55E', 're-opened': '#F59E0B',
  'on-the-job': '#3B82F6', rejected: '#9CA3AF', in_progress: '#6366F1',
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-7">
      <h2 className="text-[13px] font-semibold text-gray-700 tracking-tight mb-3 pb-2 border-b border-gray-100 flex items-center gap-2">
        <span className="inline-block w-1 h-3.5 rounded-full bg-blue-400 shrink-0" />
        {title}
      </h2>
      {children}
    </div>
  )
}

function TierPill({ tier }: { tier: string }) {
  return (
    <span className="px-2.5 py-0.5 rounded-md text-[12px] font-semibold tracking-wide"
      style={{ color: TIER_COLOR[tier], background: TIER_BG[tier] }}>
      {tier}
    </span>
  )
}

function JoinBadge({ conf, note }: { conf: string; note: string }) {
  const cfg: Record<string, { label: string; color: string; bg: string }> = {
    exact_name: { label: 'Exact ward match', color: '#15803D', bg: '#F0FDF4' },
    fuzzy_name: { label: 'Fuzzy ward match', color: '#B45309', bg: '#FFFBEB' },
    none:        { label: 'Ward unmatched',   color: '#6B7280', bg: '#F9FAFB' },
  }
  const c = cfg[conf] ?? cfg.none
  return (
    <span title={note}
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium border"
      style={{ color: c.color, background: c.bg, borderColor: c.bg }}>
      {c.label}
    </span>
  )
}

function CaseMap({ c }: { c: CaseFull }) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstance = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!mapRef.current) return
    if (mapInstance.current) { mapInstance.current.remove(); mapInstance.current = null }
    if (!c.centroid_lat || !c.centroid_lon) return

    const map = L.map(mapRef.current).setView([c.centroid_lat, c.centroid_lon], 14)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors', maxZoom: 19,
    }).addTo(map)
    mapInstance.current = map

    c.representative_complaints.forEach(r => {
      if (!r.latitude || !r.longitude) return
      const color = STATUS_COLOR[r.status?.toLowerCase() ?? ''] ?? '#9CA3AF'
      L.circleMarker([r.latitude, r.longitude], {
        radius: 6, color, fillColor: color, fillOpacity: 0.8, weight: 1.5,
      }).addTo(map).bindPopup(
        `<div style="font:12px/1.6 Inter,sans-serif;padding:2px 0">
          <strong>${r.complaint_id}</strong><br/>
          ${r.subcategory ?? ''}<br/>
          Status: <strong>${r.status ?? '—'}</strong><br/>
          ${r.description_excerpt.substring(0, 120)}…
        </div>`
      )
    })

    L.marker([c.centroid_lat, c.centroid_lon]).addTo(map)
      .bindPopup(`<strong>Case centroid</strong><br/>${c.case_id}`)

    return () => { map.remove(); mapInstance.current = null }
  }, [c.case_id, c.centroid_lat, c.centroid_lon])

  if (!c.centroid_lat) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-center h-[280px] text-[12px] text-gray-400">
        No GPS centroid — ward-temporal cluster
      </div>
    )
  }

  return (
    <div>
      <div ref={mapRef} style={{ height: 320 }} className="rounded-lg border border-gray-200 overflow-hidden" />
      <p className="text-[11px] text-gray-400 mt-1.5 leading-relaxed">
        {c.cluster_method === 'ward_temporal'
          ? 'Ward-temporal cluster — centroid is ward-averaged, not GPS-precise.'
          : `Geographic cluster · ${c.geographic_extent_km?.toFixed(1) ?? '?'} km bounding box · ${c.representative_complaints.filter(r => r.latitude).length} GPS points shown`}
      </p>
    </div>
  )
}

const COMPLAINTS_PAGE_SIZE = 25

function AllComplaintsTable({ c }: { c: import('../types').CaseFull }) {
  const [page, setPage] = useState(0)
  const complaints = c.all_complaints ?? []
  const total = complaints.length
  const pageCount = Math.ceil(total / COMPLAINTS_PAGE_SIZE)
  const slice = complaints.slice(page * COMPLAINTS_PAGE_SIZE, (page + 1) * COMPLAINTS_PAGE_SIZE)

  if (total === 0) {
    return (
      <div className="border border-gray-200 rounded-lg px-4 py-6 text-center text-[12px] text-gray-400">
        No complaint records available.
      </div>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full text-[12px]">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              {['ID', 'Date', 'Subcategory', 'Status', 'Ward', 'Description'].map(h => (
                <th key={h} className="px-3 py-2.5 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.map((r, i) => (
              <tr key={r.complaint_id} className={`border-b border-gray-50 ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'}`}>
                <td className="px-3 py-2.5 font-mono text-[11px] text-gray-500 whitespace-nowrap">{r.complaint_id.slice(-12)}</td>
                <td className="px-3 py-2.5 whitespace-nowrap text-gray-600">{r.created_at || '—'}</td>
                <td className="px-3 py-2.5 max-w-[160px] truncate text-gray-700">{r.subcategory || '—'}</td>
                <td className="px-3 py-2.5 whitespace-nowrap">
                  <span
                    style={{ color: STATUS_COLOR[r.status?.toLowerCase() ?? ''] ?? '#6B7280' }}
                    className="font-semibold text-[11px]"
                  >
                    {r.status || '—'}
                  </span>
                </td>
                <td className="px-3 py-2.5 whitespace-nowrap text-gray-600">{r.ward_name || '—'}</td>
                <td className="px-3 py-2.5 max-w-[240px] truncate text-gray-500" title={r.description}>
                  {r.description}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pageCount > 1 && (
        <div className="flex items-center justify-between mt-2 text-[12px] text-gray-500">
          <span>
            Showing {page * COMPLAINTS_PAGE_SIZE + 1}–{Math.min((page + 1) * COMPLAINTS_PAGE_SIZE, total)} of{' '}
            <strong className="text-gray-700">{total}</strong> complaints
          </span>
          <div className="flex gap-1.5">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-100 disabled:opacity-30 transition-colors"
            >
              Prev
            </button>
            <button
              onClick={() => setPage(p => Math.min(pageCount - 1, p + 1))}
              disabled={page >= pageCount - 1}
              className="px-3 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-100 disabled:opacity-30 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
      <p className="text-[11px] text-gray-400 mt-2">
        All {total} complaints for this case. Sorted by original cluster order.
      </p>
    </div>
  )
}

export default function CaseDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: c, loading, error } = useCaseFull(id ?? null)
  const navigate = useNavigate()

  if (loading) return (
    <div className="p-10 text-gray-400 text-sm flex items-center gap-2">
      <span className="animate-spin">⟳</span> Loading case…
    </div>
  )
  if (error) return <div className="p-10 text-red-600 text-sm font-medium">Error: {error}</div>
  if (!c) return <div className="p-10 text-gray-400 text-sm">Case not found.</div>

  const factorData = Object.entries(c.priority_factors)
    .map(([k, v]) => ({ name: FACTOR_LABEL[k] ?? k, value: Math.round(v * 100) }))
    .sort((a, b) => b.value - a.value)

  const evidenceDirect = c.evidence_items.filter(e => ['complaint_volume', 'complaint_status'].includes(e.type))
  const evidenceContextual = c.evidence_items.filter(e => !['complaint_volume', 'complaint_status'].includes(e.type))

  const keyMetrics = [
    { label: 'Score',        value: c.priority_score.toFixed(3) },
    { label: 'Complaints',   value: fmt(c.complaint_count) },
    { label: 'Unresolved',   value: `${c.unresolved_rate_pct}%` },
    { label: 'Open',         value: fmt(c.open_count) },
    { label: 'Re-opened',    value: fmt(c.reopened_count) },
    { label: 'Years active', value: c.years_active.join(', ') },
    { label: 'Agency',       value: c.responsible_agency ?? '—' },
  ]

  return (
    <div className="px-8 py-7 max-w-[1200px]">
      {/* Back */}
      <button onClick={() => navigate(-1)}
        className="text-[12px] text-gray-400 hover:text-blue-600 mb-5 flex items-center gap-1 transition-colors">
        ← Back to Registry
      </button>

      {/* Case header */}
      <div className="mb-7 pb-6 border-b border-gray-100">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <TierPill tier={c.priority_tier} />
          <JoinBadge conf={c.ward_join_confidence} note={c.ward_join_note} />
          <span className="text-[11px] text-gray-400 font-mono">{c.case_id}</span>
        </div>
        <h1 className="text-[21px] font-bold text-gray-900 tracking-tight leading-snug mb-2">
          {c.problem_title}
        </h1>
        <p className="text-[13px] text-gray-500 leading-relaxed max-w-[720px]">{c.problem_summary}</p>

        {/* Key metrics strip */}
        <div className="grid grid-cols-4 sm:grid-cols-7 gap-2.5 mt-5">
          {keyMetrics.map(({ label, value }) => (
            <div key={label} className="bg-gray-50 rounded-lg px-3 py-2.5 border border-gray-100">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-0.5">{label}</p>
              <p className="text-[13px] font-semibold text-gray-800 leading-tight truncate" title={String(value)}>{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-[1fr_320px] gap-8">
        {/* Left column */}
        <div>
          {/* Map */}
          <Section title="Geographic Evidence">
            <CaseMap c={c} />
          </Section>

          {/* Timeline */}
          <Section title="Complaint Timeline">
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={c.complaint_chronology} margin={{ left: -10, right: 4 }}>
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6 }} />
                <Bar dataKey="count" fill="#1D6FBF" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-[11px] text-gray-400 mt-1.5">
              Complaint volume by year. Data covers 2019–2022.
            </p>
          </Section>

          {/* Evidence assessment */}
          <Section title="Evidence Assessment">
            {evidenceDirect.length > 0 && (
              <div className="mb-4">
                <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-2">Direct evidence</p>
                <div className="space-y-1.5">
                  {evidenceDirect.map((e, i) => (
                    <div key={i} className="flex gap-2 text-[12px]">
                      <span className="text-blue-400 shrink-0 mt-0.5">•</span>
                      <span className="text-gray-700">{e.description}
                        <span className="text-gray-400 ml-1 text-[11px]">[{e.traceable_to}]</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {evidenceContextual.length > 0 && (
              <div className="mb-4">
                <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-2">
                  Contextual evidence
                  {c.ward_join_confidence === 'fuzzy_name' && (
                    <span className="ml-2 text-amber-600 normal-case font-normal">— fuzzy ward match, verify independently</span>
                  )}
                </p>
                <div className="space-y-1.5">
                  {evidenceContextual.map((e, i) => (
                    <div key={i} className="flex gap-2 text-[12px]">
                      <span className="text-green-400 shrink-0 mt-0.5">•</span>
                      <span className="text-gray-700">{e.description}
                        <span className="text-gray-400 ml-1 text-[11px]">[{e.traceable_to}]</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {c.hypotheses.length > 0 && (
              <div className="mb-4">
                <p className="text-[11px] font-semibold text-amber-600 uppercase tracking-wide mb-2">Hypotheses — unverified</p>
                <div className="space-y-1.5">
                  {c.hypotheses.map((h, i) => (
                    <div key={i} className="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 text-[12px] text-amber-800">
                      {h}
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div>
              <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-2">Evidence gaps</p>
              <div className="text-[12px] text-gray-500 space-y-1">
                {c.ward_join_confidence === 'none' && <div>• No ward enrichment — ward name unmatched in crosswalk</div>}
                {!c.centroid_lat && <div>• No GPS centroid — ward-temporal cluster</div>}
                {evidenceContextual.length === 0 && <div>• No KAUN contextual evidence</div>}
                {c.ward_join_confidence !== 'none' && c.centroid_lat && evidenceContextual.length > 0 && (
                  <div>• No major gaps identified</div>
                )}
              </div>
            </div>
          </Section>

          {/* All complaints */}
          <Section title={`Complaint Records (${c.complaint_count} total)`}>
            <AllComplaintsTable c={c} />
          </Section>
        </div>

        {/* Right sidebar */}
        <div>
          {/* Priority explanation */}
          <Section title="Priority Explanation">
            <div className="flex items-center gap-2.5 mb-2.5">
              <TierPill tier={c.priority_tier} />
              <span className="text-[22px] font-bold text-gray-900">{c.priority_score.toFixed(3)}</span>
            </div>
            <p className="text-[12px] text-gray-500 mb-3 leading-relaxed">{c.priority_rationale}</p>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={factorData} layout="vertical" margin={{ left: 10, right: 30 }}>
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} tickFormatter={v => `${v}%`} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={110} />
                <Tooltip formatter={((v: any) => [`${v}%`, 'Score']) as any} contentStyle={{ fontSize: 11, borderRadius: 6 }} />
                <Bar dataKey="value" radius={[0, 2, 2, 0]}>
                  {factorData.map((d, i) => (
                    <Cell key={i} fill={d.value >= 70 ? '#B91C1C' : d.value >= 40 ? '#B45309' : '#1D6FBF'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-[11px] text-gray-400 mt-1.5">
              Crash risk is ward-level only, not GPS-matched to this cluster.
            </p>
          </Section>

          {/* Ward context */}
          <Section title="Ward Context">
            <div className="space-y-2">
              <div className="flex justify-between items-center text-[12px] py-1.5 border-b border-gray-50">
                <span className="text-gray-500">Ward</span>
                <span className="font-semibold text-gray-800">{c.primary_ward_name ?? '—'}</span>
              </div>
              <div className="flex justify-between items-center text-[12px] py-1.5 border-b border-gray-50">
                <span className="text-gray-500">Enrichment</span>
                <JoinBadge conf={c.ward_join_confidence} note={c.ward_join_note} />
              </div>
              {evidenceContextual.map((e, i) => (
                <div key={i} className="text-[12px] py-1.5 border-b border-gray-50">
                  <span className="text-gray-400 block text-[10px] uppercase tracking-wide mb-0.5">{e.type.replace(/_/g, ' ')}</span>
                  <span className="text-gray-700">{e.description}</span>
                </div>
              ))}
              {evidenceContextual.length === 0 && (
                <p className="text-[12px] text-gray-400">No ward enrichment available.</p>
              )}
            </div>
            <p className="text-[11px] text-gray-400 mt-2.5 leading-relaxed">{c.ward_join_note}</p>
          </Section>

          {/* Work orders in ward */}
          {c.work_orders_detail && c.work_orders_detail.length > 0 && (
            <Section title={`Work Orders in Ward (${c.work_orders_detail.length})`}>
              <div className="space-y-2">
                {c.work_orders_detail.slice(0, 10).map((wo, i) => (
                  <div key={wo.work_order_id} className={`text-[12px] rounded-lg px-3 py-2 border ${i % 2 === 0 ? 'bg-white border-gray-100' : 'bg-gray-50/50 border-gray-100'}`}>
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-mono text-[10px] text-gray-400">{wo.work_order_id}</span>
                      {wo.fy && (
                        <span className="text-[10px] font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">{wo.fy}</span>
                      )}
                      {wo.sanctioned_crore != null && (
                        <span className="ml-auto text-[11px] font-semibold text-gray-700 tabular-nums">
                          ₹{wo.sanctioned_crore.toFixed(1)} Cr
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 leading-snug line-clamp-2">{wo.description}</p>
                    {wo.contractor_name && (
                      <p className="text-[11px] text-gray-400 mt-0.5">{wo.contractor_name}</p>
                    )}
                  </div>
                ))}
                {c.work_orders_detail.length > 10 && (
                  <p className="text-[11px] text-gray-400 text-center pt-1">
                    +{c.work_orders_detail.length - 10} more work orders in ward
                  </p>
                )}
              </div>
              <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-100 rounded px-2 py-1.5 mt-2 leading-relaxed">
                Ward-level only — these work orders cannot be directly linked to this complaint cluster.
              </p>
            </Section>
          )}

          {/* Recommended actions */}
          <Section title="Recommended Actions">
            <ol className="space-y-2.5">
              {c.recommended_next_steps.map((step, i) => (
                <li key={i} className="flex gap-2.5 text-[12px] text-gray-700 leading-relaxed">
                  <span className="shrink-0 font-bold text-blue-400 mt-px">{i + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>

            {/* Quick-action links */}
            <div className="mt-3 pt-3 border-t border-gray-100 space-y-1.5">
              <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-2">Useful links</p>
              {[
                {
                  label: 'File RTI online (Central RTI portal)',
                  url: 'https://rtionline.gov.in/',
                  note: 'Free, online. For BBMP matters use Karnataka state portal.',
                },
                {
                  label: 'Karnataka RTI portal',
                  url: 'https://rtimis.kar.nic.in/',
                  note: 'For state/BBMP departments.',
                },
                {
                  label: `KAUN BBMP — ward work orders for ${c.primary_ward_name ?? 'this ward'}`,
                  url: `https://bengaluru.kaun.city/ward/${encodeURIComponent(c.primary_ward_name ?? '')}`,
                  note: 'View sanctioned work orders and spending.',
                },
                {
                  label: 'I Change My City — file a new complaint',
                  url: 'https://www.ichangemycity.com/bengaluru',
                  note: 'Log a new pothole or road complaint.',
                },
                {
                  label: 'BBMP Citizen Portal (Sahaya)',
                  url: 'https://bbmpsahaya.karnataka.gov.in/',
                  note: 'Official BBMP grievance portal.',
                },
              ].map(({ label, url, note }) => (
                <a
                  key={url}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-2 group hover:bg-blue-50 rounded-lg px-2 py-1.5 transition-colors -mx-2"
                >
                  <span className="text-blue-500 shrink-0 mt-0.5 text-[10px] group-hover:text-blue-700">↗</span>
                  <span>
                    <span className="text-[12px] text-blue-700 group-hover:underline">{label}</span>
                    <span className="block text-[10px] text-gray-400 leading-tight">{note}</span>
                  </span>
                </a>
              ))}
            </div>

            <p className="text-[11px] text-gray-400 mt-3 leading-relaxed">
              These actions have not been performed. Pipeline-generated from evidence patterns.
            </p>
          </Section>

          {/* Meta */}
          <div className="text-[11px] text-gray-400 leading-relaxed bg-gray-50 rounded-lg p-3 border border-gray-100 space-y-0.5">
            <p>Cluster method: <span className="font-medium text-gray-500">{c.cluster_method.replace('_', '-')}</span></p>
            <p>Cluster confidence: <span className="font-medium text-gray-500">{c.cluster_confidence.toFixed(2)}</span></p>
            <p>Generated: <span className="font-medium text-gray-500">{c.generated_at?.slice(0, 10)}</span></p>
            <p className="pt-1 border-t border-gray-200 mt-1 text-gray-400">{c.agency_attribution_note}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
