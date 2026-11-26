import { useState, useMemo, useEffect, useRef } from 'react'
import { useCasesIndex } from '../data'
import { useNavigate } from 'react-router-dom'
import { TIER_COLOR, TIER_BG } from '../design'
import type { CaseRow } from '../types'
import L from 'leaflet'
import { AIChatPanel } from '../AIChatPanel'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

/** Colour scale for choropleth — 5 buckets from 0 cases to 5+ cases */
function choroplethColor(caseCount: number): string {
  if (caseCount === 0) return '#F9FAFB'
  if (caseCount === 1) return '#DBEAFE'
  if (caseCount === 2) return '#93C5FD'
  if (caseCount <= 4) return '#3B82F6'
  return '#1D4ED8'
}

type MapMode = 'points' | 'choropleth'

interface WardMapProps {
  cases: CaseRow[]
  wardBoundaries: GeoJSON.FeatureCollection | null
  mode: MapMode
  onWardClick: (wardName: string) => void
}

function WardMap({ cases, wardBoundaries, mode, onWardClick }: WardMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstance = useRef<L.Map | null>(null)

  // Build ward → case count map for choropleth
  const wardCaseCount = useMemo(() => {
    const m: Record<string, number> = {}
    cases.forEach(c => {
      const w = c.primary_ward_name
      if (w) m[w] = (m[w] ?? 0) + 1
    })
    return m
  }, [cases])

  // Initialise map once
  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return
    const map = L.map(mapRef.current, { zoomControl: true }).setView([12.97, 77.59], 11)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map)
    mapInstance.current = map
    return () => { map.remove(); mapInstance.current = null }
  }, [])

  // Re-render layers when cases or mode changes
  useEffect(() => {
    const map = mapInstance.current
    if (!map) return
    // Clear all non-tile layers
    map.eachLayer(layer => { if (!(layer instanceof L.TileLayer)) map.removeLayer(layer) })

    if (mode === 'choropleth' && wardBoundaries) {
      // Choropleth fill layer
      L.geoJSON(wardBoundaries, {
        style: (feature) => {
          const name = feature?.properties?.ward_name ?? feature?.properties?.NAME ?? ''
          const count = wardCaseCount[name] ?? 0
          return {
            fillColor: choroplethColor(count),
            fillOpacity: count > 0 ? 0.75 : 0.25,
            color: '#6B7280',
            weight: 0.8,
          }
        },
        onEachFeature: (feature, layer) => {
          const name = feature?.properties?.ward_name ?? feature?.properties?.NAME ?? 'Unknown'
          const count = wardCaseCount[name] ?? 0
          layer.bindTooltip(
            `<div style="font:12px/1.5 Inter,sans-serif">
              <strong>${name}</strong><br/>
              ${count === 0 ? 'No cases' : `${count} case${count > 1 ? 's' : ''}`}
            </div>`,
            { sticky: true }
          )
          layer.on('click', () => { if (count > 0) onWardClick(name) })
        },
      }).addTo(map)
    } else {
      // Point markers (default / fallback)
      const gpsCases = cases.filter(c => c.centroid_lat && c.centroid_lon)
      gpsCases.forEach(c => {
        const color = TIER_COLOR[c.priority_tier] ?? '#6B7280'
        const marker = L.circleMarker([c.centroid_lat!, c.centroid_lon!], {
          radius: Math.min(4 + c.complaint_count / 10, 14),
          color,
          fillColor: color,
          fillOpacity: 0.72,
          weight: 1.5,
        }).addTo(map)
        marker.bindPopup(
          `<div style="font:12px/1.6 Inter,sans-serif;min-width:200px;padding:2px 0">
            <strong style="font-size:13px;display:block;margin-bottom:2px">${c.case_id}</strong>
            ${c.problem_title.substring(0, 60)}…<br/>
            <span style="color:${color};font-weight:600">${c.priority_tier}</span>
            &nbsp;·&nbsp;Score: ${c.priority_score.toFixed(3)}<br/>
            ${c.complaint_count} complaints · ${c.unresolved_rate_pct}% unresolved
          </div>`
        )
      })
    }
  }, [cases, mode, wardBoundaries, wardCaseCount, onWardClick])

  return <div ref={mapRef} className="map-container" />
}

export default function WardExplorer() {
  const { data: cases } = useCasesIndex()
  const navigate = useNavigate()

  const [selectedWard, setSelectedWard] = useState<string>('All')
  const [tierFilter, setTierFilter] = useState<string[]>([])
  const [mapMode, setMapMode] = useState<MapMode>('points')
  const [panelTab, setPanelTab] = useState<'cases' | 'ai'>('cases')
  const [chatCase, setChatCase] = useState<CaseRow | null>(null)
  const [wardBoundaries, setWardBoundaries] = useState<GeoJSON.FeatureCollection | null>(null)
  const [boundaryStatus, setBoundaryStatus] = useState<'loading' | 'loaded' | 'unavailable'>('loading')

  // Try to load ward boundary GeoJSON (optional — graceful fallback if absent)
  useEffect(() => {
    const base = import.meta.env.BASE_URL
    fetch(`${base}data/ward_boundaries.geojson`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((gj: GeoJSON.FeatureCollection) => {
        setWardBoundaries(gj)
        setBoundaryStatus('loaded')
        setMapMode('choropleth')  // auto-switch to choropleth when available
      })
      .catch(() => {
        setBoundaryStatus('unavailable')
      })
  }, [])

  const wards = useMemo(() => {
    if (!cases) return []
    return ['All', ...Array.from(new Set(cases.map(c => c.primary_ward_name).filter(Boolean))).sort()]
  }, [cases])

  const filteredCases = useMemo(() => {
    if (!cases) return []
    return cases.filter(c => {
      if (selectedWard !== 'All' && c.primary_ward_name !== selectedWard) return false
      if (tierFilter.length > 0 && !tierFilter.includes(c.priority_tier)) return false
      return true
    })
  }, [cases, selectedWard, tierFilter])

  const wardCases = useMemo(() => {
    if (selectedWard === 'All' || !cases) return []
    return cases.filter(c => c.primary_ward_name === selectedWard)
      .sort((a, b) => b.priority_score - a.priority_score)
  }, [cases, selectedWard])

  if (!cases) return (
    <div className="p-10 text-gray-400 text-sm flex items-center gap-2">
      <span className="animate-spin">⟳</span> Loading…
    </div>
  )

  const high   = filteredCases.filter(c => c.priority_tier === 'HIGH').length
  const medium = filteredCases.filter(c => c.priority_tier === 'MEDIUM').length
  const low    = filteredCases.filter(c => c.priority_tier === 'LOW').length
  const totalComplaints = filteredCases.reduce((s, c) => s + c.complaint_count, 0)

  const mapCaption = mapMode === 'choropleth' && wardBoundaries
    ? 'Choropleth: fill intensity = number of cases per ward. Click a ward to filter. © OpenStreetMap contributors.'
    : 'Circle size proportional to complaint count. Colour indicates priority tier. © OpenStreetMap contributors.'

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="px-8 py-5 border-b border-gray-100 bg-white">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-[22px] font-bold text-gray-900 tracking-tight">Ward Explorer</h1>
            <p className="text-[13px] text-gray-500 mt-0.5">
              {filteredCases.filter(c => c.has_gps).length} cluster locations shown · click a marker to preview
            </p>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            {/* Map mode toggle — only show when boundary data is loaded */}
            {boundaryStatus === 'loaded' && (
              <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
                {(['points', 'choropleth'] as MapMode[]).map(m => (
                  <button
                    key={m}
                    onClick={() => setMapMode(m)}
                    className={`px-3 py-1 rounded-md text-[11px] font-semibold transition-all capitalize ${
                      mapMode === m
                        ? 'bg-white text-gray-800 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            )}

            <select
              value={selectedWard}
              onChange={e => setSelectedWard(e.target.value)}
              className="text-[13px] border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-400/40 min-w-[180px] shadow-sm"
            >
              {wards.map(w => <option key={w} value={w}>{w}</option>)}
            </select>

            {/* Tier filters */}
            <div className="flex gap-1.5 items-center">
              {['HIGH', 'MEDIUM', 'LOW'].map(t => (
                <button
                  key={t}
                  onClick={() => setTierFilter(prev =>
                    prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]
                  )}
                  className="px-2.5 py-1 rounded-md text-[11px] font-semibold border transition-all"
                  style={tierFilter.includes(t)
                    ? { color: '#fff', background: TIER_COLOR[t], borderColor: TIER_COLOR[t] }
                    : { color: TIER_COLOR[t], background: TIER_BG[t], borderColor: 'transparent' }}
                >
                  {t}
                </button>
              ))}
              {tierFilter.length > 0 && (
                <button
                  onClick={() => setTierFilter([])}
                  className="text-[11px] text-gray-400 hover:text-gray-600 px-1.5 transition-colors"
                >
                  ×
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Summary stats strip */}
        <div className="flex items-center gap-6 text-[13px] text-gray-500">
          <span><strong className="text-gray-800 font-semibold">{filteredCases.length}</strong> cases</span>
          <span className="font-semibold" style={{ color: TIER_COLOR.HIGH }}>{high} HIGH</span>
          <span className="font-semibold" style={{ color: TIER_COLOR.MEDIUM }}>{medium} MED</span>
          <span className="font-semibold" style={{ color: TIER_COLOR.LOW }}>{low} LOW</span>
          <span><strong className="text-gray-800 font-semibold">{totalComplaints.toLocaleString()}</strong> complaints</span>
          {selectedWard !== 'All' && (
            <span className="ml-auto text-blue-700 font-semibold">{selectedWard}</span>
          )}
          {boundaryStatus === 'unavailable' && (
            <span className="ml-auto text-[11px] text-gray-400">
              Choropleth unavailable — place <code className="font-mono bg-gray-100 px-1 rounded">public/data/ward_boundaries.geojson</code> to enable
            </span>
          )}
        </div>

        {/* Choropleth legend */}
        {mapMode === 'choropleth' && wardBoundaries && (
          <div className="flex items-center gap-3 mt-3 text-[11px] text-gray-500">
            <span className="font-medium">Cases per ward:</span>
            {[
              { label: '0', color: '#F9FAFB' },
              { label: '1', color: '#DBEAFE' },
              { label: '2', color: '#93C5FD' },
              { label: '3–4', color: '#3B82F6' },
              { label: '5+', color: '#1D4ED8' },
            ].map(({ label, color }) => (
              <div key={label} className="flex items-center gap-1">
                <span className="inline-block w-3.5 h-3.5 rounded-sm border border-gray-200" style={{ background: color }} />
                <span>{label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Map + side panel */}
      <div className="flex flex-1 overflow-hidden">
        {/* Map */}
        <div className="flex-1 p-5 flex flex-col">
          <WardMap
            cases={filteredCases}
            wardBoundaries={wardBoundaries}
            mode={mapMode}
            onWardClick={setSelectedWard}
          />
          <p className="text-[11px] text-gray-400 mt-2 leading-relaxed">{mapCaption}</p>
        </div>

        {/* Side panel */}
        <div className="w-[320px] border-l border-gray-100 flex flex-col bg-white overflow-hidden">

          {/* Tab bar */}
          <div className="flex border-b border-gray-100 shrink-0">
            {(['cases', 'ai'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setPanelTab(tab)}
                className={[
                  'flex-1 py-2.5 text-[12px] font-semibold transition-colors',
                  panelTab === tab
                    ? 'text-blue-700 border-b-2 border-blue-500 -mb-px'
                    : 'text-gray-400 hover:text-gray-600',
                ].join(' ')}
              >
                {tab === 'cases' ? '📋 Cases' : '✦ AI Chat'}
              </button>
            ))}
          </div>

          {/* Cases tab */}
          {panelTab === 'cases' && (
            <div className="overflow-y-auto flex-1 px-4 py-4">
              {selectedWard === 'All' ? (
                <div className="mt-4 text-center">
                  <div className="text-3xl mb-3 text-gray-200">⊕</div>
                  <p className="text-[13px] font-medium text-gray-500 mb-1">Select a ward</p>
                  <p className="text-[12px] text-gray-400 leading-relaxed">
                    Use the dropdown above{mapMode === 'choropleth' ? ' or click a ward on the map' : ''} to filter by ward.
                  </p>
                </div>
              ) : (
                <>
                  <p className="text-[12px] font-semibold text-gray-700 mb-3 pb-2 border-b border-gray-100">
                    {wardCases.length} case{wardCases.length !== 1 ? 's' : ''} in <span className="text-blue-700">{selectedWard}</span>
                  </p>
                  <div className="flex flex-col gap-2">
                    {wardCases.map(c => (
                      <div key={c.case_id} className="rounded-lg border border-gray-100 hover:border-blue-200 hover:bg-blue-50/60 transition-all">
                        <button
                          onClick={() => navigate(`/cases/${c.case_id}`)}
                          className="text-left p-3 w-full"
                        >
                          <div className="flex items-center gap-2 mb-1.5">
                            <span className="px-1.5 py-0.5 rounded-md text-[10px] font-semibold"
                              style={{ color: TIER_COLOR[c.priority_tier], background: TIER_BG[c.priority_tier] }}>
                              {c.priority_tier}
                            </span>
                            <span className="text-[11px] text-gray-400 ml-auto tabular-nums">{c.priority_score.toFixed(3)}</span>
                          </div>
                          <p className="text-[12px] text-gray-700 leading-snug line-clamp-2">{c.problem_title}</p>
                          <p className="text-[11px] text-gray-400 mt-1">
                            {c.complaint_count} complaints · {c.unresolved_rate_pct}% unresolved
                          </p>
                        </button>
                        <div className="px-3 pb-2 flex gap-2">
                          <button
                            onClick={() => { setChatCase(c); setPanelTab('ai') }}
                            className="text-[10px] text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
                          >
                            ✦ Ask AI about this
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          {/* AI Chat tab */}
          {panelTab === 'ai' && (
            <div className="flex-1 min-h-0 flex flex-col">
              <AIChatPanel selectedCase={chatCase} allCases={cases} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
