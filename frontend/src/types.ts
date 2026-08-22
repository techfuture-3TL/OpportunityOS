export type Strategy = 'VIRAL_TREND' | 'HIGH_MARGIN' | 'SAFE_EVERGREEN' | 'LOW_COMPETITION'

export interface ScoreRationale {
  demand: string
  gap: string
  margin: string
  supply: string
  safety: string
  virality: string
}

export interface PricePoint {
  month: string
  market_avg: number
  cogs: number
  suggested_price: number
}

export interface PillarSubScore {
  label_vi: string
  label_en: string
  score: number
  evidence: string
}

export interface PillarDetail {
  key: string
  label_vi: string
  label_en: string
  score: number
  weight: number
  contribution: number
  formula_vi: string
  formula_en: string
  sub_scores: PillarSubScore[]
}

export interface IpCheckDetail {
  tier: number
  tier_label_vi: string
  tier_label_en: string
  score: number
  status: string
  verdict_vi: string
  verdict_en: string
  notes: string
}

export interface VerdictDetail {
  result: 'GO' | 'CAUTION' | 'STOP' | string
  label_vi: string
  label_en: string
  reasons_vi: string[]
  reasons_en: string[]
}

export interface ScoringDetail {
  weights: Record<string, number>
  strategy_preset: string
  formula_total: string
  pillars: PillarDetail[]
  ip_check?: IpCheckDetail | null
  verdict?: VerdictDetail | null
}

export interface Opportunity {
  id: string
  name: string
  category: string
  target_niche: string
  image_url?: string
  opportunity_score: number
  score_breakdown: Record<'demand_growth' | 'market_gap' | 'profit_margin' | 'supply_feasibility' | 'ip_safety' | 'tiktok_virality', number>
  score_rationales?: ScoreRationale
  scoring_detail?: ScoringDetail | null
  price_chart_data?: PricePoint[]
  price_min?: number
  price_max?: number
  matched_sku: string
  matched_product_name: string
  base_cost: number
  suggested_price: number
  profit_margin_pct: number
  profit_per_unit: number
  trend_velocity: string
  key_pain_point_solved: string
  negative_reviews_summary: string[]
  ip_safety_status: string
  virality_hook_rating: string
  ai_design_prompt: string
  tiktok_hooks: string[]
  target_audience: string
  brand_reference?: string
  marketplace_sources?: string[]
}

export interface AnalysisResult {
  total_opportunities: number
  execution_time_ms: number
  applied_strategy: string
  data_source_used: string
  crawl_summary?: {
    auto_crawl_full?: boolean
    marketplaces?: string[]
  }
  opportunities: Opportunity[]
}

export interface ProductBrief {
  opportunity_id: string
  title: string
  executive_summary: string
  target_buyer_persona: string
  product_specifications: Record<string, string>
  financial_model: Record<string, number>
  ai_design_prompts: string[]
  tiktok_marketing_plan: string[]
  tiktok_hooks?: string[]
  launch_checklist: string[]
}

export interface DatabaseRecord {
  [key: string]: string | number | undefined
}

export interface CatalogItem {
  sku: string
  name: string
  category: string
  base_cost: number
  suggested_min_price: number
  suggested_max_price: number
  warehouses: string[]
  techniques: string[]
  production_days: number
  description: string
}
