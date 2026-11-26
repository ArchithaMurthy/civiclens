import { useCasesIndex } from '../data'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList,
  LineChart, Line, CartesianGrid, Legend,
} from 'recharts'
import { TIER_COLOR, TIER_BG, fmt } from '../design'

/** Map raw pipeline subcategory labels → plain English */
const SUBCAT_LABEL: Record<string, string> = {
  'Fixing/Reparing Potholes':                      'Pothole Repairs',
  'Tarring Or Asphalting Of Existing Road':         'Road Resurfacing',
  'Tarring Asphalting Mud/Kutcha/Unpaved Road':     'Unpaved Road Work',
  'Flooding/Waterlogging Roads And Footpaths':      'Flooding & Waterlogging',
  'Construction Of New Road':                       'New Road Construction',
  'Construction Roadside Drains':                   'Roadside Drain Work',
  'Construction of new footpaths':                  'Footpath Construction',
  'Footpath Repair/Maintenance':                    'Footpath Repairs',
  'Repair/Maintenance Of Existing Road':            'Road Maintenance',
  'Removal Of Encroachment On Footpath/Road':       'Footpath Encroachment',
}

function humanSubcat(raw: string): string {
  if (SUBCAT_LABEL[raw]) return SUBCAT_LABEL[raw]
  // Fallback: strip filler words, title-case
  return raw
    .replace(/\bOr\b/g, '&')
    .replace(/\bOf\b/g, 'of')
    .replace(/\bAnd\b/g, '&')
    .replace(/\/[A-Z][a-z]+/g, s => s.toLowerCase())
    .trim()
}

function KPICard({
  label, value, sub, accent,
}: {
  label: string; value: string | number; sub?: string; accent?: string
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl px-5 py-4 flex flex-col gap-1 shadow-sm">
      <p className="text-[10px] font-semibold tracking-[0.12em] uppercase text-gray-400">{label}</p>
      <p className="text-[28px] font-bold leading-none" style={accent ? { color: accent } : { color: '#111827' }}>
        {value}
      </p>
      {sub && <p className="text-[11px] text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}

function TierPill({ tier }: { tier: string }) {
  return (
    <span
      className="inline-block px-2 py-0.5 rounded-md text-[11px] font-semibold tracking-wide"
      style={{ color: TIER_COLOR[tier], background: TIER_BG[tier] }}
    >
      {tier}
    </span>
  )
}

function SectionTitle({ children, sub }: { children: React.ReactNode; sub?: string }) {
  return (
    <div className="mb-3">
      <p className="text-[13px] font-semibold text-gray-700 flex items-center gap-2">
        <span className="inline-block w-1 h-4 rounded-full bg-blue-500 shrink-0" />
        {children}
      </p>
      {sub && <p className="text-[11px] text-gray-400 mt-0.5 pl-3">{sub}</p>}
    </div>
  )
}

export default function Overview() {
  const { data: cases, error } = useCasesIndex()
  const navigate = useNavigate()

  if (error) return (
    <div className="p-10 text-red-600 text-sm font-medium">
      Failed to load data: {error}
    </div>
  )
  if (!cases) return (
    <div className="p-10 text-gray-400 text-sm flex items-center gap-2">
      <span className="animate-spin">⟳</span> Loading…
    </div>
  )

  const high   = cases.filter(c => c.priority_tier === 'HIGH')
  const medium = cases.filter(c => c.priority_tier === 'MEDIUM')
  const low    = cases.filter(c => c.priority_tier === 'LOW')
  const totalComplaints = cases.reduce((s, c) => s + c.complaint_count, 0)
  const wards = [...new Set(cases.map(c => c.primary_ward_name).filter(Boolean))].length

  // ── Year-on-year complaint trend ──
  // Each case has years_active[]; count how many cases were active each year
  const YEARS = [2019, 2020, 2021, 2022]
  const yearTrend = YEARS.map(yr => {
    const active = cases.filter(c => c.years_active.includes(yr))
    return {
      year: String(yr),
      Total:    active.length,
      Urgent:   active.filter(c => c.priority_tier === 'HIGH').length,
      Moderate: active.filter(c => c.priority_tier === 'MEDIUM').length,
      Low:      active.filter(c => c.priority_tier === 'LOW').length,
    }
  })

  // ── Subcategory: horizontal bar, % of total cases, plain English ──
  const subcatMap: Record<string, number> = {}
  cases.forEach(c => {
    const key = humanSubcat(c.representative_subcategory)
    subcatMap[key] = (subcatMap[key] || 0) + 1
  })
  const total = cases.length
  const subcats = Object.entries(subcatMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7)
    .map(([name, count]) => ({
      name,
      count,
      pct: Math.round(count / total * 100),
    }))
    .reverse() // bottom-to-top for horizontal bar

  // ── Top wards ──
  const wardMap: Record<string, { total: number; high: number; complaints: number }> = {}
  cases.forEach(c => {
    const w = c.primary_ward_name || 'Unknown'
    if (!wardMap[w]) wardMap[w] = { total: 0, high: 0, complaints: 0 }
    wardMap[w].total++
    wardMap[w].complaints += c.complaint_count
    if (c.priority_tier === 'HIGH') wardMap[w].high++
  })
  const topWards = Object.entries(wardMap)
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 15)
    .map(([name, v]) => ({ name, ...v }))
    .reverse()

  const topCases = [...cases].sort((a, b) => b.priority_score - a.priority_score).slice(0, 10)

  return (
    <div className="px-8 py-7 max-w-[1360px] mx-auto">
      {/* Page header */}
      <div className="mb-7">
        <h1 className="text-[22px] font-bold text-gray-900 tracking-tight">City Overview</h1>
        <p className="text-[13px] text-gray-500 mt-1 leading-relaxed">
          Recurring civic infrastructure problems in Bengaluru — 298 cases derived from 5,072 road complaints
        </p>
      </div>

      {/* KPI bar */}
      <div className="grid grid-cols-6 gap-3 mb-7">
        <KPICard label="Civic Cases"    value={cases.length} />
        <KPICard label="Needs Urgent Action" value={high.length}   sub="score ≥ 0.55 (HIGH)"   accent="#B91C1C" />
        <KPICard label="Needs Attention"     value={medium.length} sub="score 0.35–0.55 (MED)"  accent="#B45309" />
        <KPICard label="Monitor"             value={low.length}    sub="score < 0.35 (LOW)"     accent="#15803D" />
        <KPICard label="Complaints Logged"   value={fmt(totalComplaints)} sub="in clusters" />
        <KPICard label="Wards Affected"      value={wards} />
      </div>

      {/* Data provenance */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl px-5 py-3 mb-7 text-[12px] text-blue-800 leading-relaxed">
        <span className="font-semibold">Data sources:</span> ICMC 2019–2022 (I Change My City) · KAUN BBMP 2023–2026 work orders · 243-ward metrics
        &ensp;·&ensp;<span className="font-semibold">Ward enrichment:</span> 206 exact · 66 fuzzy · 26 unmatched
        &ensp;·&ensp;<span className="font-semibold">Scoring:</span> thresholds HIGH≥0.55 / MED≥0.35
        &ensp;·&ensp;<span className="font-semibold">Note:</span> Complaint data 2019–2022; work orders 2023–2026 (temporal gap)
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-5 mb-7">

        {/* Year-on-year complaint trend */}
        <div className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm">
          <SectionTitle sub="Number of active cases per year — a case counts in every year it received complaints.">
            Complaint Activity by Year
          </SectionTitle>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={yearTrend} margin={{ left: 0, right: 16, top: 8, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} tickLine={false} />
              <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} width={28} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6 }} />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
              <Line type="monotone" dataKey="Total"    stroke="#6B7280" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Urgent"   stroke={TIER_COLOR.HIGH}   strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Moderate" stroke={TIER_COLOR.MEDIUM} strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Low"      stroke={TIER_COLOR.LOW}    strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Subcategory horizontal bar — % of cases */}
        <div className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm">
          <SectionTitle sub="What types of civic problems appear most? Each bar = % of all cases.">
            What Problems Come Up Most?
          </SectionTitle>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={subcats} layout="vertical" margin={{ left: 0, right: 44, top: 4, bottom: 4 }}>
              <XAxis
                type="number"
                domain={[0, Math.ceil(Math.max(...subcats.map(s => s.pct)) / 10) * 10 + 5]}
                tickFormatter={v => `${v}%`}
                tick={{ fontSize: 10 }}
              />
              <YAxis
                type="category" dataKey="name"
                tick={{ fontSize: 10 }} width={160}
                tickFormatter={(v: string) => v.length > 22 ? v.slice(0, 21) + '…' : v}
              />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6 }}
                formatter={(v: any, _: any, props: any) => [`${v}% of cases (${props.payload.count} clusters)`, 'Share']}
              />
              <Bar dataKey="pct" fill="#3B82F6" radius={[0, 3, 3, 0]}>
                <LabelList dataKey="pct" position="right" formatter={(v: any) => `${v}%`} style={{ fontSize: 10, fill: '#374151' }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

      </div>

      {/* Top wards */}
      <div className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm mb-7">
        <SectionTitle sub="Wards with the most recurring civic cases logged — not necessarily the worst roads overall.">
          Which Wards Have the Most Cases?
        </SectionTitle>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={topWards} layout="vertical" barSize={14} margin={{ left: 0, right: 44, top: 4, bottom: 24 }}>
            <XAxis
              type="number" tick={{ fontSize: 10 }}
              label={{ value: 'Number of cases', position: 'insideBottom', offset: -14, fontSize: 10, fill: '#9CA3AF' }}
            />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={110} />
            <Tooltip
              contentStyle={{ fontSize: 12, borderRadius: 6 }}
              formatter={(v: any) => [v, 'Cases']}
            />
            <Bar dataKey="total" fill="#1D6FBF" radius={[0, 3, 3, 0]}>
              <LabelList dataKey="total" position="right" style={{ fontSize: 10, fill: '#374151' }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top 10 priority cases — compact card grid */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-[13px] font-semibold text-gray-700 flex items-center gap-2">
              <span className="inline-block w-1 h-4 rounded-full bg-blue-500 shrink-0" />
              Top 10 Cases Needing Attention
            </p>
            <p className="text-[11px] text-gray-400 pl-3">Ranked by urgency score — click any card to open the full investigation</p>
          </div>
          <button
            onClick={() => navigate('/cases')}
            className="text-[12px] text-blue-600 hover:underline shrink-0"
          >
            View all 298 →
          </button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {topCases.map((c) => (
            <button
              key={c.case_id}
              onClick={() => navigate(`/cases/${c.case_id}`)}
              className="text-left bg-white border border-gray-200 rounded-xl px-4 py-3.5 hover:border-blue-300 hover:bg-blue-50/40 transition-all shadow-sm group"
            >
              <div className="flex items-center justify-between mb-2">
                <TierPill tier={c.priority_tier} />
                <span className="text-[11px] tabular-nums font-bold text-gray-500">
                  {c.priority_score.toFixed(3)}
                </span>
              </div>
              <p className="text-[12px] font-semibold text-gray-800 leading-snug mb-1 group-hover:text-blue-800 line-clamp-2">
                {c.problem_title}
              </p>
              <div className="flex items-center gap-3 text-[11px] text-gray-400 mt-1">
                <span>{c.primary_ward_name}</span>
                <span className="ml-auto">{c.complaint_count} complaints</span>
                <span className="text-orange-500 font-medium">{c.unresolved_rate_pct}% open</span>
              </div>
            </button>
          ))}
        </div>
        <p className="text-[11px] text-gray-400 mt-3">
          Urgency reflects complaint volume, recurrence, and unresolved rate. Does not establish legal liability.
        </p>
      </div>
    </div>
  )
}
