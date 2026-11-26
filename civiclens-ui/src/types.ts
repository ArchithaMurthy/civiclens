/* CivicLens — shared type definitions */

export interface CaseRow {
  case_id: string
  cluster_id: string
  cluster_method: 'geo_dbscan' | 'ward_temporal' | 'manual'
  problem_title: string
  representative_subcategory: string
  primary_ward_name: string
  complaint_count: number
  unresolved_rate_pct: number
  open_count: number
  resolved_count: number
  reopened_count: number
  priority_tier: 'HIGH' | 'MEDIUM' | 'LOW'
  priority_score: number
  ward_join_confidence: 'exact_name' | 'fuzzy_name' | 'none'
  responsible_agency: string
  years_active: number[]
  date_first_complaint: string | null
  date_last_complaint: string | null
  centroid_lat: number | null
  centroid_lon: number | null
  geographic_extent_km: number | null
  has_gps: boolean
}

export interface EvidenceItem {
  type: string
  description: string
  source: string
  traceable_to: string
}

export interface RepComplaint {
  complaint_id: string
  created_at: string | null
  ward_name: string | null
  subcategory: string | null
  status: string | null
  description_excerpt: string
  latitude: number | null
  longitude: number | null
}

/** Compact work order record embedded in work_orders_detail (Sprint 5-5) */
export interface WorkOrderDetail {
  work_order_id: string
  fy: string | null
  description: string
  contractor_name: string | null
  sanctioned_crore: number | null
  work_category: string | null
}

/** Compact complaint record embedded in all_complaints (Sprint 5-2) */
export interface AllComplaint {
  complaint_id: string
  created_at: string        // date portion only: "YYYY-MM-DD"
  ward_name: string
  subcategory: string
  status: string
  description: string
  latitude?: number
  longitude?: number
}

export interface CaseFull extends CaseRow {
  problem_summary: string
  problem_category: string
  unique_ward_count: number
  all_ward_names: string[]
  complaint_chronology: { year: number; count: number }[]
  evidence_items: EvidenceItem[]
  hypotheses: string[]
  agency_confidence: string
  agency_attribution_note: string
  priority_factors: Record<string, number>
  priority_rationale: string
  cluster_confidence: number
  clustering_reasons: string[]
  ward_join_note: string
  recommended_next_steps: string[]
  complaint_ids: string[]
  work_order_ids: string[]                // Sprint 5-5
  work_orders_detail: WorkOrderDetail[]  // compact work order records
  representative_complaints: RepComplaint[]
  all_complaints: AllComplaint[]          // full set, embedded at build time
  generated_at: string
}

export interface WardMetric {
  ward_no: number
  ward_name: string
  pothole_complaints: number | null
  road_crashes_2024: number | null
  fatal_crashes_2024: number | null
  spend_roads_and_infrastructure: number | null
  spend_period: string | null
  total_work_orders: number | null
}
