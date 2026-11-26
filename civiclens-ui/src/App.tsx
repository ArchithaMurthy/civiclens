import { Routes, Route, NavLink } from 'react-router-dom'
import Overview from './pages/Overview'
import WardExplorer from './pages/WardExplorer'
import CaseRegistry from './pages/CaseRegistry'
import CaseDetail from './pages/CaseDetail'
import { LocalCaseProvider } from './localCaseStore'

const NAV = [
  { to: '/',      label: 'Overview',      icon: '◈' },
  { to: '/wards', label: 'Ward Explorer', icon: '⊕' },
  { to: '/cases', label: 'Case Registry', icon: '≡' },
]

export default function App() {
  return (
    <LocalCaseProvider>
    <div className="flex h-screen overflow-hidden bg-[#F8F9FB]">
      {/* ── Sidebar ── */}
      <aside className="w-[216px] shrink-0 flex flex-col bg-[#0D1117] overflow-y-auto">
        {/* Wordmark */}
        <div className="px-5 pt-6 pb-5 border-b border-[#21262D]">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[#3B82F6] text-[18px] leading-none">◈</span>
            <p className="text-[15px] font-bold tracking-tight text-[#F0F6FF]">CivicLens</p>
          </div>
          <p className="text-[11px] font-medium tracking-[0.12em] uppercase text-[#4D5562] pl-[26px]">
            Bengaluru
          </p>
        </div>

        {/* Nav */}
        <nav className="flex flex-col gap-0.5 px-3 pt-4">
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] transition-colors leading-snug ` +
                (isActive
                  ? 'bg-[#1C2333] text-[#E6EDF3] font-semibold'
                  : 'text-[#8B949E] hover:bg-[#161B22] hover:text-[#C9D1D9]')
              }
            >
              {({ isActive }) => (
                <>
                  <span className={`text-[14px] leading-none shrink-0 ${isActive ? 'text-[#3B82F6]' : 'text-[#4D5562]'}`}>
                    {icon}
                  </span>
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Spacer + footer */}
        <div className="mt-auto px-5 py-5 border-t border-[#21262D]">
          <div className="space-y-0.5 text-[11px] text-[#6E7681] leading-relaxed">
            <p><span className="text-[#4D5562]">Cases</span> · 298 (48 HIGH)</p>
            <p><span className="text-[#4D5562]">Source</span> · ICMC 2019–2022</p>
            <p><span className="text-[#4D5562]">Work orders</span> · KAUN 2023–2026</p>
          </div>
          <div className="mt-3 pt-3 border-t border-[#21262D]">
            <p className="text-[10px] text-[#3D444D] leading-relaxed">
              POC — verify before citing.
            </p>
          </div>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="flex-1 overflow-y-auto bg-white">
        <Routes>
          <Route path="/"          element={<Overview />} />
          <Route path="/wards"     element={<WardExplorer />} />
          <Route path="/cases"     element={<CaseRegistry />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
        </Routes>
      </main>
    </div>
    </LocalCaseProvider>
  )
}
