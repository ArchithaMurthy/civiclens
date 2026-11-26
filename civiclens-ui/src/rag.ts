/**
 * CivicLens RAG — Retrieval-Augmented Generation helpers
 *
 * Flow:
 *  1. loadEmbeddings()  — fetch pre-computed vectors once, cache in memory
 *  2. embedQuery(text)  — embed user query in-browser using same model as build script
 *  3. topKCaseIds(query, k) — cosine similarity search → case IDs
 *  4. fetchRetrievedContext(caseIds) — fetch CaseFull records, return formatted string
 */
import { pipeline, type FeatureExtractionPipeline } from '@huggingface/transformers'
import { fetchCaseFull, BASE } from './data'
import type { CaseFull } from './types'

const MODEL = 'Xenova/all-MiniLM-L6-v2'

// ── Singleton caches ──────────────────────────────────────────────────────────

let _embedder: FeatureExtractionPipeline | null = null
let _embedderLoading: Promise<FeatureExtractionPipeline> | null = null

async function getEmbedder(): Promise<FeatureExtractionPipeline> {
  if (_embedder) return _embedder
  if (_embedderLoading) return _embedderLoading
  _embedderLoading = pipeline('feature-extraction', MODEL, { dtype: 'fp32' }) as Promise<FeatureExtractionPipeline>
  _embedder = await _embedderLoading
  return _embedder
}

interface EmbeddingRecord {
  case_id: string
  vector: number[]
}

let _embeddingsCache: EmbeddingRecord[] | null = null
let _embeddingsLoading: Promise<EmbeddingRecord[]> | null = null

async function loadEmbeddings(): Promise<EmbeddingRecord[]> {
  if (_embeddingsCache) return _embeddingsCache
  if (_embeddingsLoading) return _embeddingsLoading
  _embeddingsLoading = fetch(`${BASE}data/embeddings.json`)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
    .then(data => { _embeddingsCache = data; return data })
  return _embeddingsLoading
}

// ── Maths ─────────────────────────────────────────────────────────────────────

function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0, normA = 0, normB = 0
  for (let i = 0; i < a.length; i++) {
    dot   += a[i] * b[i]
    normA += a[i] * a[i]
    normB += b[i] * b[i]
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-10)
}

// ── Public API ────────────────────────────────────────────────────────────────

/** Warm up the model and embeddings in the background — call on mount */
export function warmUp(): void {
  getEmbedder().catch(() => {})
  loadEmbeddings().catch(() => {})
}

/** Returns the top-k most relevant case IDs for a query string */
export async function topKCaseIds(query: string, k = 5): Promise<string[]> {
  const [embedder, embeddings] = await Promise.all([getEmbedder(), loadEmbeddings()])

  const output = await embedder(query, { pooling: 'mean', normalize: true })
  const queryVec = Array.from(output.data as Float32Array)

  const scored = embeddings.map(e => ({
    case_id: e.case_id,
    score: cosineSimilarity(queryVec, e.vector),
  }))
  scored.sort((a, b) => b.score - a.score)
  return scored.slice(0, k).map(e => e.case_id)
}

/** Fetch full case records for the given IDs and format them as a compact context block */
export async function fetchRetrievedContext(caseIds: string[]): Promise<string> {
  const cases: CaseFull[] = await Promise.all(
    caseIds.map(id => fetchCaseFull(id).catch(() => null as unknown as CaseFull))
  ).then(cs => cs.filter(Boolean))

  if (cases.length === 0) return ''

  const blocks = cases.map(c => {
    const factors = Object.entries(c.priority_factors)
      .map(([k, v]) => `${k}:${(v * 100).toFixed(0)}%`)
      .join(', ')
    return [
      `Case ${c.case_id}: ${c.problem_title}`,
      `  Ward: ${c.primary_ward_name} | Tier: ${c.priority_tier} | Score: ${c.priority_score.toFixed(3)}`,
      `  Complaints: ${c.complaint_count} total, ${c.unresolved_rate_pct}% unresolved, ${c.open_count} open`,
      `  Factors: ${factors}`,
      `  Rationale: ${c.priority_rationale}`,
    ].join('\n')
  })

  return `═══ RETRIEVED CASES (most relevant to your question) ═════════════════
${blocks.join('\n\n')}
═══════════════════════════════════════════════════════════════════`
}
