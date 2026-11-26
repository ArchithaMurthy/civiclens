/**
 * build_embeddings.mjs
 * Pre-computes sentence embeddings for every case in cases_index.json
 * using the same model (@huggingface/transformers all-MiniLM-L6-v2)
 * that the browser will use at query time — guaranteeing identical vector space.
 *
 * Run from repo root:
 *   node scripts/build_embeddings.mjs
 *
 * Output: civiclens-ui/public/data/embeddings.json
 *   [{ case_id: string, vector: number[] }, ...]
 */

import { pipeline } from '@huggingface/transformers'
import { readFileSync, writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dir = dirname(fileURLToPath(import.meta.url))
const ROOT = join(__dir, '..')

const INDEX_PATH = join(ROOT, 'civiclens-ui', 'public', 'data', 'cases_index.json')
const OUT_PATH   = join(ROOT, 'civiclens-ui', 'public', 'data', 'embeddings.json')

/** Fields to embed per case — covers semantic + factual queries */
function caseToText(c) {
  return [
    c.problem_title,
    c.representative_subcategory,
    `Ward: ${c.primary_ward_name}`,
    `Priority: ${c.priority_tier} (score ${c.priority_score.toFixed(3)})`,
    `Complaints: ${c.complaint_count} total, ${c.unresolved_rate_pct}% unresolved`,
    `Agency: ${c.responsible_agency}`,
    `Years active: ${c.years_active.join(', ')}`,
  ].join('. ')
}

async function main() {
  console.log('Loading embedding model (downloads ~25 MB on first run)…')
  const embedder = await pipeline(
    'feature-extraction',
    'Xenova/all-MiniLM-L6-v2',
    { dtype: 'fp32' }
  )

  const cases = JSON.parse(readFileSync(INDEX_PATH, 'utf-8'))
  console.log(`Embedding ${cases.length} cases…`)

  const results = []
  for (let i = 0; i < cases.length; i++) {
    const c = cases[i]
    const text = caseToText(c)
    const output = await embedder(text, { pooling: 'mean', normalize: true })
    // output.data is a Float32Array — convert to plain Array for JSON
    results.push({ case_id: c.case_id, vector: Array.from(output.data) })
    if ((i + 1) % 25 === 0) console.log(`  ${i + 1}/${cases.length}`)
  }

  writeFileSync(OUT_PATH, JSON.stringify(results))
  console.log(`\nDone. Written to ${OUT_PATH}`)
  console.log(`Dimensions: ${results[0].vector.length}  Cases: ${results.length}`)
}

main().catch(err => { console.error(err); process.exit(1) })
