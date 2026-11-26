/* CivicLens — design tokens and helpers */

export const TIER_COLOR: Record<string, string> = {
  HIGH:   '#B91C1C',  // red-700
  MEDIUM: '#B45309',  // amber-700
  LOW:    '#15803D',  // green-700
}

export const TIER_BG: Record<string, string> = {
  HIGH:   '#FEF2F2',
  MEDIUM: '#FFFBEB',
  LOW:    '#F0FDF4',
}

export const JOIN_LABEL: Record<string, string> = {
  exact_name: 'Exact',
  fuzzy_name: 'Fuzzy',
  none:       'None',
}

export const JOIN_COLOR: Record<string, string> = {
  exact_name: '#15803D',
  fuzzy_name: '#B45309',
  none:       '#6B7280',
}

export const FACTOR_LABEL: Record<string, string> = {
  complaint_volume:    'Complaint Volume',
  recurrence_years:   'Recurrence (years)',
  unresolved_rate:    'Unresolved Rate',
  reopened_rate:      'Re-opened Rate',
  crash_risk:         'Crash Risk',
  description_severity: 'Severity Keywords',
}

export function fmt(n: number | null | undefined, decimals = 0): string {
  if (n == null) return '—'
  return n.toLocaleString('en-IN', { maximumFractionDigits: decimals })
}

export function fmtCrore(n: number | null | undefined): string {
  if (n == null) return '—'
  return `₹${(n / 1e7).toFixed(1)} Cr`
}
