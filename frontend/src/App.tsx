import { Fragment, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Check,
  ChevronDown,
  ChevronUp,
  CircleDollarSign,
  Clapperboard,
  Clipboard,
  Coffee,
  Crosshair,
  Crown,
  CupSoda,
  Database,
  Download,
  Droplets,
  Factory,
  Flame,
  Globe,
  LayoutGrid,
  Lightbulb,
  LoaderCircle,
  Mountain,
  PackageCheck,
  Palette,
  PawPrint,
  Quote,
  RefreshCcw,
  Rocket,
  Search,
  ShieldCheck,
  Shirt,
  ShoppingBag,
  ShoppingCart,
  Snowflake,
  Sparkles,
  Sprout,
  Store,
  Table2,
  Tag,
  Target,
  TrendingUp,
  Wallet,
  X,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  PolarAngleAxis,
  PolarGrid,
  Radar as RadarShape,
  RadarChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";
import { analyzeOpportunities, checkHealth, generateBrief } from "./api";
import type {
  AnalysisResult,
  Opportunity,
  ProductBrief,
  ScoringDetail,
  Strategy,
} from "./types";
import { useI18n } from "./i18n";
import { cn } from "./lib/utils";

type Screen = "discovery" | "goals" | "funnel" | "results";

const initialFilters = {
  dataSource: "ALL",
  country: "GLOBAL",
  seasonality: "Evergreen",
  categories: ["Drinkware", "Gifts"],
  keyword: "",
  targetBrand: "",
  selectedMarketplaces: ["amazon", "tiktok", "shopee", "lazada", "ebay", "etsy"],
  growth: 20,
  margin: 60,
  priceMin: 20,
  priceMax: 55,
  cogs: 15,
  warehouse: "US",
  techniques: ["LASER_ENGRAVING", "UV_PRINT"],
  productionDays: 3,
  strategy: "VIRAL_TREND" as Strategy,
};

const STRATEGY_WEIGHTS: Record<Strategy, Record<string, number>> = {
  VIRAL_TREND: { demand: 0.35, gap: 0.15, margin: 0.15, supply: 0.1, safety: 0.1, virality: 0.15 },
  HIGH_MARGIN: { demand: 0.2, gap: 0.15, margin: 0.4, supply: 0.1, safety: 0.1, virality: 0.05 },
  SAFE_EVERGREEN: { demand: 0.15, gap: 0.2, margin: 0.2, supply: 0.2, safety: 0.2, virality: 0.05 },
  LOW_COMPETITION: { demand: 0.2, gap: 0.4, margin: 0.15, supply: 0.1, safety: 0.1, virality: 0.05 },
};

const categoryOptions = [
  ["Drinkware", "Đồ uống"],
  ["Apparel", "Thời trang"],
  ["Home_Decor", "Trang trí nhà"],
  ["Pet_Accessories", "Phụ kiện thú cưng"],
  ["Gifts", "Quà tặng"],
  ["Outdoor_Sports", "Thể thao ngoài trời"],
] as const;

const techniqueOptions = [
  ["LASER_ENGRAVING", "Khắc laser"],
  ["UV_PRINT", "In UV"],
  ["DTG", "DTG"],
  ["EMBROIDERY", "Thêu"],
  ["SUBLIMATION", "In chuyển nhiệt"],
] as const;

const strategies: { id: Strategy; icon: LucideIcon; labelVi: string; labelEn: string; copyVi: string; copyEn: string }[] = [
  {
    id: "VIRAL_TREND",
    icon: Flame,
    labelVi: "Săn xu hướng viral",
    labelEn: "Viral trend hunting",
    copyVi: "Ưu tiên sản phẩm tăng trưởng nhanh, giàu khả năng lan truyền.",
    copyEn: "Prioritize fast-growing products with high viral potential.",
  },
  {
    id: "HIGH_MARGIN",
    icon: CircleDollarSign,
    labelVi: "Ưu tiên lợi nhuận",
    labelEn: "High margin",
    copyVi: "Tối ưu biên lợi nhuận gộp an toàn.",
    copyEn: "Optimize for thick, safe gross margins.",
  },
  {
    id: "SAFE_EVERGREEN",
    icon: ShieldCheck,
    labelVi: "Bền vững, an toàn",
    labelEn: "Safe & evergreen",
    copyVi: "Nhu cầu ổn định và an toàn bản quyền.",
    copyEn: "Stable demand and full IP safety.",
  },
  {
    id: "LOW_COMPETITION",
    icon: Crosshair,
    labelVi: "Ngách còn trống",
    labelEn: "Low competition",
    copyVi: "Tìm điểm đau khách hàng mà đối thủ bỏ lỡ.",
    copyEn: "Find customer pain points competitors missed.",
  },
];

const PLATFORM_TABS = [
  { id: "all", label: "Tất cả", en: "All" },
  { id: "amazon", label: "Amazon", en: "Amazon" },
  { id: "tiktok", label: "TikTok Shop", en: "TikTok Shop" },
  { id: "shopee", label: "Shopee", en: "Shopee" },
  { id: "lazada", label: "Lazada", en: "Lazada" },
  { id: "ebay", label: "eBay", en: "eBay" },
  { id: "etsy", label: "Etsy", en: "Etsy" },
] as const;

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}
function categoryName(category: string) {
  return (
    Object.fromEntries(categoryOptions)[category] ?? category.replace("_", " ")
  );
}

/* ═══════════════════════════════════════════════════════════════════
   APP ROOT
   ═══════════════════════════════════════════════════════════════════ */
export default function App() {
  const { t } = useI18n();
  const [screen, setScreen] = useState<Screen>("discovery");
  const [filters, setFilters] = useState(initialFilters);
  const [health, setHealth] = useState<"checking" | "online" | "offline">(
    "checking",
  );
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Opportunity | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    checkHealth()
      .then(() => setHealth("online"))
      .catch(() => setHealth("offline"));
  }, []);

  const submitAnalysis = async (overrideKeyword?: string) => {
    setLoading(true);
    setError("");
    try {
      const result = await analyzeOpportunities({
        search_mode:
          overrideKeyword || filters.keyword ? "GUIDED" : "DISCOVERY",
        data_source: filters.dataSource,
        limit: 20,
        market_and_niche: {
          target_country: filters.country,
          categories: filters.categories,
          seasonality: filters.seasonality,
          seed_keywords: (overrideKeyword ?? filters.keyword)
            .split(",")
            .map((word) => word.trim())
            .filter(Boolean),
          target_brand: filters.targetBrand ? filters.targetBrand.trim() : undefined,
          selected_marketplaces: ["amazon", "tiktok", "shopee", "lazada", "ebay", "etsy"],
          min_sales_growth_pct: filters.growth,
        },
        financials: {
          min_profit_margin_pct: filters.margin,
          target_retail_price_min: filters.priceMin,
          target_retail_price_max: filters.priceMax,
          max_base_cogs_cap: filters.cogs,
          target_ad_budget: 1000,
        },
        supply_chain: {
          preferred_warehouse: filters.warehouse,
          allowed_techniques: filters.techniques,
          max_production_days: filters.productionDays,
        },
        strategy: { preset: filters.strategy },
      });
      setAnalysis(result);
      setScreen("results");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? t(
              "Không thể kết nối OpportunityOS API (vps.nexora-flow.cloud). Hãy kiểm tra backend rồi thử lại.",
              "Cannot reach the OpportunityOS API (vps.nexora-flow.cloud). Check the backend and retry.",
            )
          : t("Chưa thể phân tích cơ hội vào lúc này.", "Could not analyze opportunities right now."),
      );
    } finally {
      setLoading(false);
    }
  };

  const enterCopilot = () => {
    setScreen("discovery");
    setError("");
    setFilters(initialFilters);
  };

  return (
    <main className="flex h-screen overflow-hidden bg-[#fafaf9] text-[#1c1917]">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
        filters={filters}
        setFilters={setFilters}
        screen={screen}
        setScreen={setScreen}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar health={health} screen={screen} onReset={enterCopilot} />

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[1240px] p-5 sm:p-7 lg:p-9">
            {screen === "discovery" && (
              <Discovery
                loading={loading}
                error={error}
                filters={filters}
                setFilters={setFilters}
                onSelectKeyword={(keyword, brand) => {
                  setFilters((current) => ({ ...current, keyword, targetBrand: brand || "" }));
                  setScreen("goals");
                }}
                onAnalyze={(keyword, brand) => {
                  setFilters((current) => ({ ...current, keyword, targetBrand: brand || "" }));
                  setScreen("goals");
                }}
              />
            )}
            {screen === "goals" && (
              <GoalsSetup
                filters={filters}
                setFilters={setFilters}
                onBack={() => setScreen("discovery")}
                onNext={() => setScreen("funnel")}
              />
            )}
            {screen === "funnel" && (
              <Funnel
                filters={filters}
                setFilters={setFilters}
                loading={loading}
                error={error}
                onBack={() => setScreen("goals")}
                onAnalyze={() => submitAnalysis()}
              />
            )}
            {screen === "results" && (
              <Results
                analysis={analysis}
                filters={filters}
                setFilters={setFilters}
                loading={loading}
                error={error}
                onAnalyze={() => submitAnalysis()}
                onOpen={setSelected}
                onRestart={enterCopilot}
              />
            )}
          </div>
        </div>
      </div>

      {selected && (
        <BriefModal opportunity={selected} onClose={() => setSelected(null)} />
      )}
    </main>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   LOGO MARK
   ═══════════════════════════════════════════════════════════════════ */
function LogoMark({ size = 36 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 4.5l9.5 5.5v12L16 27.5l-9.5-5.5v-12z" stroke="#b72727" strokeWidth="2" fill="#fdf3f3" />
      <path d="M16 10l2.2 3.8L22 16l-3.8 2.2L16 22l-2.2-3.8L10 16l3.8-2.2z" fill="#b72727" />
      <circle cx="16" cy="16" r="1.6" fill="#9a1f1f" />
    </svg>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   TOP BAR — stepper + ngôn ngữ + trạng thái
   ═══════════════════════════════════════════════════════════════════ */
function TopBar({
  health,
  screen,
  onReset,
}: {
  health: "checking" | "online" | "offline";
  screen: Screen;
  onReset: () => void;
}) {
  const { t, lang, setLang } = useI18n();
  const steps: { id: Screen; labelVi: string; labelEn: string }[] = [
    { id: "discovery", labelVi: "Khám phá", labelEn: "Discover" },
    { id: "goals", labelVi: "Mục tiêu", labelEn: "Goals" },
    { id: "funnel", labelVi: "Phễu lọc", labelEn: "Funnel" },
    { id: "results", labelVi: "Kết quả", labelEn: "Results" },
  ];
  const activeIdx = steps.findIndex((step) => step.id === screen);

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-4 border-b border-[#e7e5e4] bg-white px-5">
      <div className="flex items-center gap-2.5">
        {steps.map((step, idx) => {
          const state = idx < activeIdx ? "done" : idx === activeIdx ? "active" : "todo";
          return (
            <div key={step.id} className="flex items-center gap-2.5">
              <div
                className={cn(
                  "step-dot",
                  state === "active" && "step-dot-active",
                  state === "done" && "step-dot-done",
                )}
              >
                {state === "done" ? <Check className="h-3 w-3" /> : idx + 1}
              </div>
              <span
                className={cn(
                  "text-[11px] font-bold",
                  state === "active" ? "text-[#1c1917]" : state === "done" ? "text-[#b72727]" : "t-3",
                )}
              >
                {t(step.labelVi, step.labelEn)}
              </span>
              {idx < steps.length - 1 && (
                <div className={cn("step-line", state === "done" && "step-line-done")} />
              )}
            </div>
          );
        })}
      </div>

      <div className="flex items-center gap-2.5">
        <span className="hidden items-center gap-2 rounded-full border border-[#e7e5e4] bg-[#fafaf9] px-3 py-1.5 text-[11px] font-semibold t-2 xl:inline-flex">
          <Database className="h-3.5 w-3.5 text-[#b72727]" />
          {t("2,091 tín hiệu · auto crawl 6 sàn", "2,091 signals · auto-crawl 6 marketplaces")}
        </span>
        <span
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1.5 text-[11px] font-bold",
            health === "online"
              ? "border-emerald-200 bg-emerald-50 text-emerald-700"
              : "border-amber-200 bg-amber-50 text-amber-700",
          )}
        >
          <i
            className={cn(
              "h-1.5 w-1.5 rounded-full",
              health === "online" ? "pulse-dot bg-emerald-500" : "animate-pulse bg-amber-500",
            )}
          />
          {health === "online" ? t("Online", "Online") : health === "checking" ? t("Đang kết nối", "Connecting") : t("Offline", "Offline")}
        </span>

        {/* Language toggle */}
        <div className="seg !p-0.5">
          <button
            onClick={() => setLang("vi")}
            className={cn("seg-btn !px-2.5 !py-1 !text-[11px]", lang === "vi" && "seg-btn-active")}
          >
            VI
          </button>
          <button
            onClick={() => setLang("en")}
            className={cn("seg-btn !px-2.5 !py-1 !text-[11px]", lang === "en" && "seg-btn-active")}
          >
            EN
          </button>
        </div>

        <button onClick={onReset} className="btn-ghost !px-3.5 !py-1.5 !text-[11px]">
          <RefreshCcw className="h-3 w-3" />
          {t("Bắt đầu lại", "Restart")}
        </button>
      </div>
    </header>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SIDEBAR — full height, không chọn thị trường (auto crawl full)
   ═══════════════════════════════════════════════════════════════════ */
function Sidebar({
  collapsed,
  onToggleCollapse,
  filters,
  setFilters,
  screen,
  setScreen,
}: {
  collapsed: boolean;
  onToggleCollapse: () => void;
  filters: typeof initialFilters;
  setFilters: React.Dispatch<React.SetStateAction<typeof initialFilters>>;
  screen: Screen;
  setScreen: (screen: Screen) => void;
}) {
  const { t } = useI18n();
  const update = <K extends keyof typeof filters>(
    key: K,
    value: (typeof filters)[K],
  ) => setFilters((current) => ({ ...current, [key]: value }));

  const steps: { id: Screen; labelVi: string; labelEn: string; icon: LucideIcon }[] = [
    { id: "discovery", labelVi: "Khám phá ngách", labelEn: "Discover niches", icon: Search },
    { id: "goals", labelVi: "Thiết lập mục tiêu", labelEn: "Set goals", icon: Target },
    { id: "funnel", labelVi: "Phễu lọc 3 cấp", labelEn: "3-stage funnel", icon: Crosshair },
    { id: "results", labelVi: "Bảng xếp hạng", labelEn: "Leaderboard", icon: Crown },
  ];

  const marketList = [
    { id: "amazon", label: "Amazon", icon: ShoppingCart },
    { id: "tiktok", label: "TikTok Shop", icon: Clapperboard },
    { id: "shopee", label: "Shopee", icon: ShoppingBag },
    { id: "lazada", label: "Lazada", icon: Store },
    { id: "ebay", label: "eBay", icon: Tag },
    { id: "etsy", label: "Etsy", icon: Palette },
  ];

  if (collapsed) {
    return (
      <aside className="flex w-[60px] shrink-0 select-none flex-col items-center justify-between border-r border-[#e7e5e4] bg-white py-4">
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={onToggleCollapse}
            className="grid h-8 w-8 place-items-center rounded-lg border border-[#e7e5e4] text-[#b72727] transition hover:border-[#b72727]/40"
            title="Expand sidebar"
          >
            <ArrowRight className="h-4 w-4" />
          </button>
          <LogoMark size={30} />
          <div className="h-px w-7 bg-[#e7e5e4]" />
          {steps.map((step) => (
            <button
              key={step.id}
              onClick={() => setScreen(step.id)}
              className={cn(
                "grid h-9 w-9 place-items-center rounded-xl transition",
                screen === step.id
                  ? "bg-[#b72727] text-white"
                  : "text-[#a8a29e] hover:bg-[#f5f5f4] hover:text-[#1c1917]",
              )}
              title={t(step.labelVi, step.labelEn)}
            >
              <step.icon className="h-4 w-4" />
            </button>
          ))}
        </div>
      </aside>
    );
  }

  return (
    <aside className="flex w-[280px] shrink-0 select-none flex-col border-r border-[#e7e5e4] bg-white">
      <div className="flex items-center gap-3 border-b border-[#e7e5e4] px-4 py-4">
        <LogoMark size={36} />
        <div className="min-w-0 flex-1">
          <strong className="block text-[15px] font-extrabold tracking-tight text-[#1c1917]">
            Opportunity<span className="text-[#b72727]">OS</span>
          </strong>
          <small className="block text-[10px] font-semibold uppercase tracking-[0.12em] t-3">
            {t("Nghiên cứu · Quyết định · Sản xuất", "Research · Decide · Produce")}
          </small>
        </div>
        <button
          onClick={onToggleCollapse}
          className="grid h-7 w-7 place-items-center rounded-lg border border-[#e7e5e4] text-[10px] text-[#a8a29e] transition hover:border-[#b72727]/40 hover:text-[#b72727]"
          title="Collapse"
        >
          <ArrowRight className="h-3.5 w-3.5 rotate-180" />
        </button>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto p-4">
        <SideSection title={t("Hành trình", "Journey")}>
          <div className="space-y-1">
            {steps.map((step, idx) => (
              <button
                key={step.id}
                onClick={() => setScreen(step.id)}
                className={cn(
                  "flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left transition",
                  screen === step.id ? "bg-[#fdf3f3]" : "hover:bg-[#f5f5f4]",
                )}
              >
                <span
                  className={cn(
                    "grid h-7 w-7 shrink-0 place-items-center rounded-lg font-mono text-[10.5px] font-bold transition",
                    screen === step.id
                      ? "bg-[#b72727] text-white"
                      : "border border-[#e7e5e4] bg-white text-[#a8a29e]",
                  )}
                >
                  {idx + 1}
                </span>
                <span className={cn("text-[12.5px] font-bold", screen === step.id ? "text-[#b72727]" : "t-2")}>
                  {t(step.labelVi, step.labelEn)}
                </span>
              </button>
            ))}
          </div>
        </SideSection>

        {/* Auto crawl full — thông tin, không chọn */}
        <SideSection title={t("Nguồn dữ liệu", "Data sources")}>
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3">
            <div className="flex items-center gap-1.5 text-[11.5px] font-bold text-emerald-700">
              <Zap className="h-3.5 w-3.5" />
              {t("Auto crawl full 6 sàn", "Auto-crawl all 6 platforms")}
            </div>
            <p className="mt-1 text-[10.5px] leading-relaxed text-emerald-800/80">
              {t(
                "Hệ thống tự động quét toàn bộ 6 sàn TMĐT cho từ khóa của bạn — không cần chọn thủ công.",
                "The system automatically crawls all 6 marketplaces for your keyword — no manual selection needed.",
              )}
            </p>
            <div className="mt-2 flex flex-wrap gap-1">
              {marketList.map((mkt) => (
                <span key={mkt.id} className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-white px-2 py-0.5 text-[10px] font-bold text-emerald-700">
                  <mkt.icon className="h-3 w-3" />
                  {mkt.label}
                </span>
              ))}
            </div>
          </div>
        </SideSection>

        {/* Kho phôi */}
        <SideSection title={t("Kho phôi (Fulfillment)", "Blank warehouse")}>
          <select
            value={filters.warehouse}
            onChange={(e) => update("warehouse", e.target.value)}
            className="select !py-2 !text-[12px]"
          >
            <option value="US">{t("Kho US — giao 2–5 ngày", "US warehouse — 2–5 day delivery")}</option>
            <option value="VN">{t("Kho Việt Nam — xưởng gốc", "Vietnam — factory")}</option>
            <option value="EU">{t("Kho Châu Âu — EU Hub", "EU hub")}</option>
          </select>
        </SideSection>

        {/* Unit economics */}
        <SideSection title={t("Kinh tế đơn vị", "Unit economics")}>
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[11px] font-semibold t-2">{t("Biên lợi nhuận gộp", "Gross margin")}</span>
            <span className="font-mono text-[13px] font-bold text-[#b72727]">{filters.margin}%</span>
          </div>
          <input
            type="range"
            min="20"
            max="80"
            value={filters.margin}
            onChange={(e) => update("margin", Number(e.target.value))}
            className="range"
            style={{
              background: `linear-gradient(90deg, #b72727 0%, #b72727 ${((filters.margin - 20) / 60) * 100}%, #e7e5e4 ${((filters.margin - 20) / 60) * 100}%)`,
            }}
          />
          <div className="mt-3 grid grid-cols-2 gap-2">
            <div>
              <label className="field-label !text-[9.5px]">{t("Trần COGS ($)", "COGS cap ($)")}</label>
              <input
                type="number"
                value={filters.cogs}
                onChange={(e) => update("cogs", Number(e.target.value) || 15)}
                className="input mt-1 !px-2.5 !py-1.5 !text-[12px] font-bold"
              />
            </div>
            <div>
              <label className="field-label !text-[9.5px]">{t("Giá min ($)", "Min price ($)")}</label>
              <input
                type="number"
                value={filters.priceMin}
                onChange={(e) => update("priceMin", Number(e.target.value) || 20)}
                className="input mt-1 !px-2.5 !py-1.5 !text-[12px] font-bold"
              />
            </div>
          </div>
        </SideSection>

        {/* Strategy */}
        <SideSection title={t("Chiến lược ưu tiên", "Priority strategy")}>
          <div className="grid grid-cols-2 gap-1.5">
            {strategies.map((st) => (
              <button
                key={st.id}
                type="button"
                onClick={() => update("strategy", st.id)}
                className={cn(
                  "flex flex-col items-center gap-1.5 rounded-xl border p-2.5 text-center transition",
                  filters.strategy === st.id
                    ? "border-[#b72727] bg-[#fdf3f3]"
                    : "border-[#e7e5e4] bg-white hover:border-[#d6d3d1]",
                )}
              >
                <st.icon
                  className={cn("h-4 w-4", filters.strategy === st.id ? "text-[#b72727]" : "text-[#a8a29e]")}
                />
                <span className={cn("text-[10.5px] font-bold leading-tight", filters.strategy === st.id ? "text-[#b72727]" : "t-2")}>
                  {t(st.labelVi, st.labelEn)}
                </span>
              </button>
            ))}
          </div>
        </SideSection>
      </div>

      <div className="border-t border-[#e7e5e4] px-4 py-3">
        <button
          type="button"
          onClick={() => setFilters(initialFilters)}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-[#e7e5e4] bg-white px-3 py-2 text-xs font-semibold text-[#78716c] transition hover:border-[#b72727] hover:bg-[#fafaf9] hover:text-[#b72727]"
        >
          <RefreshCcw className="h-3.5 w-3.5" />
          {t("Đặt lại bộ lọc", "Reset filters")}
        </button>
      </div>
    </aside>
  );
}

function SideSection({
  title,
  extra,
  children,
}: {
  title: string;
  extra?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="mb-2.5 flex items-center justify-between">
        <span className="text-[10px] font-extrabold uppercase tracking-[0.14em] t-3">{title}</span>
        {extra}
      </div>
      {children}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SCREEN 01 — DISCOVERY
   ═══════════════════════════════════════════════════════════════════ */
function Discovery({
  loading,
  error,
  filters,
  setFilters,
  onSelectKeyword,
  onAnalyze,
}: {
  loading: boolean;
  error: string;
  filters: typeof initialFilters;
  setFilters: React.Dispatch<React.SetStateAction<typeof initialFilters>>;
  onSelectKeyword: (keyword: string, brand?: string) => void;
  onAnalyze: (keyword: string, brand?: string) => void;
}) {
  const { t, lang } = useI18n();
  const [keyword, setKeyword] = useState(filters.keyword);
  const [brand, setBrand] = useState(filters.targetBrand || "");
  const [searchMode, setSearchMode] = useState<"KEYWORD" | "BRAND">(
    filters.targetBrand ? "BRAND" : "KEYWORD"
  );
  const [validationMsg, setValidationMsg] = useState("");

  const popularBrands = [
    { name: "Stanley", categoryVi: "Bình giữ nhiệt & Tumbler cách nhiệt", categoryEn: "Insulated bottles & tumblers", icon: CupSoda, kw: "Stanley 40oz tumbler with handle" },
    { name: "Hydro Flask", categoryVi: "Bình nước thể thao dã ngoại", categoryEn: "Sports & outdoor bottles", icon: Mountain, kw: "Hydro Flask stainless steel water bottle" },
    { name: "Yeti", categoryVi: "Cốc giữ nhiệt & Phụ kiện dã ngoại", categoryEn: "Insulated cups & outdoor gear", icon: Snowflake, kw: "Yeti rambler 20oz stainless tumbler" },
    { name: "Owala", categoryVi: "Bình nước nắp bật FreeSip", categoryEn: "FreeSip water bottles", icon: Droplets, kw: "Owala FreeSip insulated water bottle" },
    { name: "Starbucks", categoryVi: "Ly sứ, cốc tái sử dụng theo mùa", categoryEn: "Seasonal ceramic tumblers & mugs", icon: Coffee, kw: "Starbucks seasonal ceramic tumbler mug" },
    { name: "Nike", categoryVi: "Thời trang thể thao & Streetwear", categoryEn: "Sportswear & streetwear", icon: Shirt, kw: "Nike streetwear vintage tee" },
    { name: "Lululemon", categoryVi: "Activewear & Túi gym yoga", categoryEn: "Activewear & yoga gym bags", icon: Activity, kw: "Lululemon activewear graphic hoodie" },
    { name: "PetSmart", categoryVi: "Quà tặng & Phụ kiện thú cưng", categoryEn: "Pet gifts & accessories", icon: PawPrint, kw: "PetSmart custom dog leather collar" },
    { name: "Printway Original", categoryVi: "Phôi xưởng POD độc quyền", categoryEn: "Exclusive POD blanks", icon: Factory, kw: "Custom laser engraved wooden plaque" },
  ];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchMode === "BRAND") {
      if (!brand.trim() && !keyword.trim()) {
        setValidationMsg(
          t(
            "Vui lòng nhập tên Hãng/Thương hiệu hoặc bấm chọn 1 Hãng gợi ý bên dưới.",
            "Please enter a brand name or pick a suggested brand below.",
          ),
        );
        return;
      }
      setValidationMsg("");
      const activeBrand = brand.trim() || keyword.trim();
      setFilters((c) => ({ ...c, targetBrand: activeBrand }));
      onSelectKeyword(keyword.trim() || activeBrand, activeBrand);
    } else {
      if (!keyword.trim()) {
        setValidationMsg(
          t(
            "Vui lòng nhập từ khóa hoặc bấm chọn 1 ngách gợi ý bên dưới để tiếp tục.",
            "Please enter a keyword or pick a suggested niche below to continue.",
          ),
        );
        return;
      }
      setValidationMsg("");
      onSelectKeyword(keyword.trim(), brand.trim() || undefined);
    }
  };

  const trendingNiches = [
    {
      topic: "Bình Giữ Nhiệt 40oz (Insulated Tumbler)",
      tag: "Drinkware",
      sku: "PW-DRINK-TUMB-20OZ",
      growth: "+210%",
      profit: "$22.19 (74%)",
      slaVi: "Kho US 2 ngày",
      slaEn: "US warehouse 2 days",
      badge: t("Hot Winner", "Hot Winner"),
      spark: [34, 52, 46, 68, 82, 96],
    },
    {
      topic: "Halloween Ghost Mirror",
      tag: "Home Decor",
      sku: "PW-GIFT-ACRYLIC-LIGHT",
      growth: "+185%",
      profit: "$21.49 (77%)",
      slaVi: "Kho US Đúc 5mm",
      slaEn: "US 5mm acrylic",
      badge: t("Mùa vụ Q4", "Q4 seasonal"),
      spark: [28, 40, 58, 62, 78, 88],
    },
    {
      topic: "Personalized Pet Collar",
      tag: "Pet Accessories",
      sku: "PW-PET-LEATHER-COLLAR",
      growth: "+140%",
      profit: "$18.50 (68%)",
      slaVi: "Da Bò + Khắc Laser",
      slaEn: "Leather + laser",
      badge: t("Quà tặng VIP", "VIP gifting"),
      spark: [40, 38, 52, 64, 70, 84],
    },
    {
      topic: "Teacher Appreciation Mug",
      tag: "Drinkware",
      sku: "PW-DRINK-MUG-15OZ",
      growth: "+125%",
      profit: "$14.49 (76%)",
      slaVi: "Gốm Sứ Cao Cấp",
      slaEn: "Premium ceramic",
      badge: t("Evergreen", "Evergreen"),
      spark: [30, 44, 48, 56, 66, 76],
    },
  ];

  return (
    <section className="animate-fade-up">
      <p className="eyebrow">
        {t("01 · Khám phá ý tưởng & xu hướng thị trường", "01 · Discover ideas & market trends")}
      </p>
      <h1 className="mt-4 max-w-3xl text-4xl font-extrabold leading-[1.08] tracking-tight text-[#1c1917] sm:text-5xl">
        {lang === "vi" ? (
          <>Tìm thấy sản phẩm tiếp theo <span className="text-[#b72727]">đáng để làm.</span></>
        ) : (
          <>Find the next product <span className="text-[#b72727]">worth making.</span></>
        )}
      </h1>
      <p className="mt-4 max-w-2xl text-[15px] leading-relaxed t-2">
        {t(
          "Tự động quét full 6 sàn TMĐT cùng 2,091 tín hiệu nhu cầu, ghép với kho phôi Printway bằng mô hình MCDA 6 trụ cột — biến ý tưởng thành sản phẩm thắng trong vài giây.",
          "Auto-crawl all 6 marketplaces and 2,091 demand signals, match them with Printway blanks using the 6-pillar MCDA model — turn ideas into winning products in seconds.",
        )}
      </p>

      <div className="mt-6 flex flex-wrap gap-2.5">
        {[
          [Zap, t("Auto crawl full 6 sàn TMĐT", "Auto-crawl all 5 marketplaces")],
          [Database, t("2,091 tín hiệu nhu cầu CSV", "2,091 CSV demand signals")],
          [Factory, t("Kho phôi Printway tích hợp", "Printway blank catalog")],
          [Flame, t("Chấm điểm MCDA 6 trụ cột", "6-pillar MCDA scoring")],
        ].map(([Icon, label]) => {
          const IconCmp = Icon as LucideIcon;
          return (
            <span key={label as string} className="chip !cursor-default">
              <IconCmp className="h-3.5 w-3.5 text-[#b72727]" />
              {label as string}
            </span>
          );
        })}
      </div>

      <div className="seg mt-7 w-full sm:w-fit">
        <button
          type="button"
          onClick={() => { setSearchMode("KEYWORD"); setValidationMsg(""); }}
          className={cn("seg-btn", searchMode === "KEYWORD" && "seg-btn-active")}
        >
          <Search className="h-3.5 w-3.5" />
          {t("Theo từ khóa & ngách", "By keyword & niche")}
        </button>
        <button
          type="button"
          onClick={() => { setSearchMode("BRAND"); setValidationMsg(""); }}
          className={cn("seg-btn", searchMode === "BRAND" && "seg-btn-active")}
        >
          <Target className="h-3.5 w-3.5" />
          {t("Theo hãng / thương hiệu", "By brand")}
        </button>
      </div>

      <form
        className="card mt-4 flex flex-col gap-2 p-2.5 transition focus-within:border-[#b72727] focus-within:shadow-[0_0_0_3px_rgba(183,39,39,0.08)] sm:flex-row sm:items-center"
        onSubmit={handleSearchSubmit}
      >
        <label className="flex flex-1 items-center gap-3 px-3">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[#b72727]">
            {searchMode === "BRAND" ? (
              <Target className="h-4 w-4 text-white" />
            ) : (
              <Search className="h-4 w-4 text-white" />
            )}
          </span>
          <input
            value={searchMode === "BRAND" ? brand : keyword}
            onChange={(event) => {
              if (searchMode === "BRAND") setBrand(event.target.value);
              else setKeyword(event.target.value);
              if (validationMsg) setValidationMsg("");
            }}
            className="min-w-0 flex-1 bg-transparent py-2.5 text-[15px] text-[#1c1917] outline-none placeholder:text-[#a8a29e]"
            placeholder={
              searchMode === "BRAND"
                ? t(
                    "Nhập tên hãng/thương hiệu — VD: Stanley, Hydro Flask, Yeti, Owala, Nike, Lululemon…",
                    "Enter a brand — e.g. Stanley, Hydro Flask, Yeti, Owala, Nike, Lululemon…",
                  )
                : t(
                    "VD: bình giữ nhiệt, quà thú cưng, halloween mug, pickleball…",
                    "e.g. insulated bottle, pet gifts, halloween mug, pickleball…",
                  )
            }
            autoFocus
          />
        </label>
        <button className="btn-primary !px-6 !py-3 text-sm" disabled={loading}>
          {loading ? (
            <>
              <LoaderCircle className="h-4 w-4 animate-spin" />
              {t("Đang phân tích…", "Analyzing…")}
            </>
          ) : (
            <>
              {searchMode === "BRAND"
                ? t("Tìm theo hãng này", "Search this brand")
                : t("Tiếp tục thiết lập mục tiêu", "Continue to goals")}
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </form>

      {validationMsg && (
        <p className="mt-3 flex items-center gap-2 text-xs font-semibold text-[#b45309]">
          <ShieldCheck className="h-3.5 w-3.5" />
          {validationMsg}
        </p>
      )}

      {error && (
        <div className="mt-3 flex items-center justify-between rounded-xl border border-[#f3d6d6] bg-[#fdf3f3] px-4 py-2.5 text-xs text-[#b72727]">
          <span>{error}</span>
          <button
            onClick={() => onAnalyze(keyword || brand || "Bình giữ nhiệt", brand || undefined)}
            className="ml-3 font-bold underline underline-offset-2 hover:text-[#9a1f1f]"
          >
            {t("Thử lại", "Retry")}
          </button>
        </div>
      )}

      {searchMode === "BRAND" ? (
        <div className="mt-8">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[0.14em] t-3">
              <Target className="h-3.5 w-3.5 text-[#b72727]" />
              {t("Chọn nhanh hãng / thương hiệu thịnh hành", "Quick pick trending brands")}
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {popularBrands.map((b, idx) => (
              <button
                key={b.name}
                type="button"
                onClick={() => {
                  setBrand(b.name);
                  setKeyword(b.kw);
                  setValidationMsg("");
                  setFilters((c) => ({ ...c, targetBrand: b.name, keyword: b.kw }));
                  onSelectKeyword(b.kw, b.name);
                }}
                className={cn("card card-hover group flex items-center gap-3.5 p-4 text-left animate-fade-up", `d-${(idx % 6) + 1}`)}
              >
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-[#f5f5f4] text-[#b72727] transition group-hover:bg-[#fdf3f3]">
                  <b.icon className="h-5 w-5" />
                </span>
                <span className="min-w-0 flex-1">
                  <strong className="block truncate text-[13.5px] font-bold text-[#1c1917]">{b.name}</strong>
                  <span className="block truncate text-[11.5px] t-3">{t(b.categoryVi, b.categoryEn)}</span>
                </span>
                <ArrowRight className="h-4 w-4 shrink-0 text-[#a8a29e] transition group-hover:translate-x-0.5 group-hover:text-[#b72727]" />
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-7 flex flex-wrap items-center gap-2">
          <span className="mr-1 text-[11px] font-extrabold uppercase tracking-[0.14em] t-3">
            {t("Gợi ý nhanh:", "Quick picks:")}
          </span>
          {[
            "Bình giữ nhiệt",
            "Insulated Tumbler 40oz",
            "Halloween Ghost",
            "Quà Tặng Thú Cưng",
            "Teacher Appreciation",
            "Christmas Ornaments",
            "Vintage Streetwear",
            "Decor Mica Đèn LED",
          ].map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => {
                setKeyword(item);
                setBrand("");
                setValidationMsg("");
                onSelectKeyword(item);
              }}
              className="chip hover:border-[#b72727]/40 hover:text-[#b72727]"
            >
              {item}
            </button>
          ))}
        </div>
      )}

      <div className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <p className="flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[0.14em] t-3">
            <TrendingUp className="h-3.5 w-3.5 text-[#b72727]" />
            {t("Top 4 ngách nổi bật từ 2,091 tín hiệu thị trường", "Top 4 niches from 2,091 market signals")}
          </p>
          <span className="chip !cursor-default !py-1 !text-[10px]">
            <i className="pulse-dot h-1.5 w-1.5 rounded-full bg-emerald-500" />
            {t("Cập nhật theo thời gian thực", "Live updated")}
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {trendingNiches.map((niche, idx) => (
            <button
              key={niche.topic}
              onClick={() => {
                setKeyword(niche.topic);
                setValidationMsg("");
                onSelectKeyword(niche.topic);
              }}
              className={cn("card card-hover group flex flex-col p-5 text-left animate-fade-up", `d-${idx + 2}`)}
            >
              <div className="flex items-center justify-between">
                <span className="badge badge-red">{niche.badge}</span>
                <span className="text-[10px] font-bold uppercase tracking-wider t-3">{niche.tag}</span>
              </div>
              <h3 className="mt-3 text-[15px] font-bold text-[#1c1917] transition-colors group-hover:text-[#b72727]">
                {niche.topic}
              </h3>

              <div className="mt-3 flex items-end justify-between gap-3">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider t-3">
                    {t("Tăng trưởng", "Growth")}
                  </span>
                  <div className="font-mono text-lg font-bold text-emerald-700">{niche.growth}</div>
                </div>
                <div className="flex h-10 items-end gap-1">
                  {niche.spark.map((height, i) => (
                    <i key={i} className="spark-bar" style={{ height: `${height}%` }} />
                  ))}
                </div>
              </div>

              <div className="mt-3 grid grid-cols-2 gap-2 border-t border-[#f0efed] pt-3 text-[11px]">
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider t-3">
                    {t("Lãi gộp", "Gross profit")}
                  </span>
                  <strong className="mt-0.5 block font-mono text-[12px] text-[#1c1917]">{niche.profit}</strong>
                </div>
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider t-3">
                    {t("Chuỗi cung", "Supply chain")}
                  </span>
                  <span className="mt-0.5 block text-[11px] t-2">{t(niche.slaVi, niche.slaEn)}</span>
                </div>
              </div>

              <span className="mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl border border-[#f3d6d6] bg-[#fdf3f3] py-2.5 text-xs font-bold text-[#b72727] transition-all group-hover:border-[#b72727] group-hover:bg-[#b72727] group-hover:text-white">
                {t("Khám phá ngách này", "Explore this niche")}
                <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SCREEN 02 — GOALS (bỏ chọn thị trường, chỉ còn 2 câu hỏi)
   ═══════════════════════════════════════════════════════════════════ */
function GoalsSetup({
  filters,
  setFilters,
  onBack,
  onNext,
}: {
  filters: typeof initialFilters;
  setFilters: React.Dispatch<React.SetStateAction<typeof initialFilters>>;
  onBack: () => void;
  onNext: () => void;
}) {
  const { t, lang } = useI18n();
  const [stage, setStage] = useState("growth");
  const [budget, setBudget] = useState(1000);

  const chooseStage = (next: string) => {
    setStage(next);
    setFilters((current) => ({
      ...current,
      strategy:
        next === "new"
          ? "SAFE_EVERGREEN"
          : next === "growth"
            ? "HIGH_MARGIN"
            : "VIRAL_TREND",
    }));
  };

  return (
    <section className="animate-fade-up">
      <p className="eyebrow">
        {t("02 · Thiết lập mục tiêu & quy mô dự án", "02 · Set goals & project scale")}
      </p>
      <h1 className="mt-4 max-w-3xl text-4xl font-extrabold leading-[1.08] tracking-tight text-[#1c1917] sm:text-5xl">
        {lang === "vi" ? (
          <>Tùy chỉnh chiến lược theo <span className="text-[#b72727]">nguồn lực của bạn.</span></>
        ) : (
          <>Tailor the strategy to <span className="text-[#b72727]">your resources.</span></>
        )}
      </h1>
      <p className="mt-4 max-w-2xl text-[15px] leading-relaxed t-2">
        {t(
          "Hai câu hỏi giúp hệ thống tinh chỉnh trọng số 6 trụ cột MCDA phù hợp với đội ngũ bạn.",
          "Two questions to tune the 6-pillar MCDA weights to your team.",
        )}
      </p>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        {/* Card 1: Team stage */}
        <div className="card card-hover p-5 animate-fade-up d-1">
          <div className="flex items-center gap-3">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-[#b72727] font-mono text-xs font-bold text-white">
              01
            </span>
            <strong className="text-[14.5px] font-bold text-[#1c1917]">
              {t("Giai đoạn đội ngũ", "Team stage")}
            </strong>
          </div>
          <p className="mt-2.5 text-[12px] leading-relaxed t-3">
            {t(
              "Hệ thống tự tinh chỉnh trọng số 6 trụ cột phù hợp với giai đoạn này.",
              "The system auto-tunes the 6-pillar weights to this stage.",
            )}
          </p>
          <div className="mt-4 space-y-2">
            {[
              { id: "new", icon: Sprout, titleVi: "Mới bắt đầu", titleEn: "Just starting", copyVi: "Sản phẩm đầu tiên — ít rủi ro, an toàn IP tuyệt đối", copyEn: "First product — low risk, absolute IP safety" },
              { id: "growth", icon: TrendingUp, titleVi: "Đang tăng trưởng", titleEn: "Growing", copyVi: "Biên lãi gộp dày > 70%, đệm tiền > $12", copyEn: "Thick margins > 70%, cushion > $12" },
              { id: "scale", icon: Rocket, titleVi: "Mở rộng quy mô", titleEn: "Scaling", copyVi: "Bắt hot trend TikTok Shop bùng nổ đơn hàng", copyEn: "Ride TikTok Shop hot trends for order bursts" },
            ].map((opt) => (
              <button
                key={opt.id}
                onClick={() => chooseStage(opt.id)}
                className={cn(
                  "flex w-full items-start gap-3 rounded-xl border p-3 text-left transition",
                  stage === opt.id
                    ? "border-[#b72727] bg-[#fdf3f3]"
                    : "border-[#e7e5e4] bg-white hover:border-[#d6d3d1]",
                )}
              >
                <opt.icon className={cn("mt-0.5 h-4 w-4 shrink-0", stage === opt.id ? "text-[#b72727]" : "text-[#a8a29e]")} />
                <span>
                  <strong className={cn("block text-xs font-bold", stage === opt.id ? "text-[#b72727]" : "text-[#1c1917]")}>
                    {t(opt.titleVi, opt.titleEn)}
                  </strong>
                  <span className="mt-0.5 block text-[11px] leading-tight t-3">{t(opt.copyVi, opt.copyEn)}</span>
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Card 2: Budget & COGS */}
        <div className="card card-hover p-5 animate-fade-up d-2">
          <div className="flex items-center gap-3">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-[#b72727] font-mono text-xs font-bold text-white">
              02
            </span>
            <strong className="text-[14.5px] font-bold text-[#1c1917]">
              {t("Ngân sách & giá vốn", "Budget & COGS")}
            </strong>
          </div>
          <p className="mt-2.5 text-[12px] leading-relaxed t-3">
            {t(
              "Chỉ đề xuất cơ hội có chi phí phôi xưởng phù hợp ngân sách.",
              "Only surface opportunities whose blank cost fits your budget.",
            )}
          </p>
          <div className="mt-4 space-y-3.5">
            <div>
              <label className="field-label flex items-center gap-1.5">
                <Wallet className="h-3 w-3 text-[#b72727]" />
                {t("Ngân sách quảng cáo dự kiến ($)", "Planned ad budget ($)")}
              </label>
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value) || 0)}
                className="input mt-1.5"
                placeholder="500, 1000, 5000…"
              />
            </div>
            <div>
              <label className="field-label">{t("Giá vốn phôi tối đa ($)", "Max blank cost ($)")}</label>
              <input
                type="number"
                value={filters.cogs}
                onChange={(e) => setFilters((c) => ({ ...c, cogs: Number(e.target.value) || 15 }))}
                className="input mt-1.5"
                placeholder="15"
              />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <label className="field-label">{t("Biên lãi gộp tối thiểu", "Min gross margin")}</label>
                <span className="font-mono text-sm font-bold text-[#b72727]">{filters.margin}%</span>
              </div>
              <input
                type="range"
                min="20"
                max="80"
                value={filters.margin}
                onChange={(e) => setFilters((c) => ({ ...c, margin: Number(e.target.value) }))}
                className="range mt-2.5"
                style={{
                  background: `linear-gradient(90deg, #b72727 0%, #b72727 ${((filters.margin - 20) / 60) * 100}%, #e7e5e4 ${((filters.margin - 20) / 60) * 100}%)`,
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="mt-9 flex flex-wrap items-center gap-3">
        <button onClick={onNext} className="btn-primary !px-8 !py-3 text-sm">
          {t("Tiếp tục: Phễu lọc chi tiết", "Continue: detailed funnel")}
          <ArrowRight className="h-4 w-4" />
        </button>
        <button onClick={onBack} className="btn-ghost !py-3">
          {t("Quay lại khám phá", "Back to discovery")}
        </button>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SCREEN 03 — FUNNEL (không chọn thị trường)
   ═══════════════════════════════════════════════════════════════════ */
function Funnel({
  filters,
  setFilters,
  loading,
  error,
  onBack,
  onAnalyze,
}: {
  filters: typeof initialFilters;
  setFilters: React.Dispatch<React.SetStateAction<typeof initialFilters>>;
  loading: boolean;
  error: string;
  onBack: () => void;
  onAnalyze: () => void;
}) {
  const { t, lang } = useI18n();
  const update = <K extends keyof typeof filters>(
    key: K,
    value: (typeof filters)[K],
  ) => setFilters((current) => ({ ...current, [key]: value }));
  const toggle = (key: "categories" | "techniques", value: string) =>
    setFilters((current) => ({
      ...current,
      [key]: current[key].includes(value)
        ? current[key].filter((item) => item !== value)
        : [...current[key], value],
    }));
  return (
    <section className="animate-fade-up">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-2xl">
          <p className="eyebrow">
            {t("03 · Phễu lọc cây thông 3 cấp — Deterministic Funnel", "03 · 3-stage deterministic funnel")}
          </p>
          <h1 className="mt-4 text-4xl font-extrabold leading-[1.08] tracking-tight text-[#1c1917] sm:text-5xl">
            {lang === "vi" ? (
              <>Thiết lập tiêu chuẩn <span className="text-[#b72727]">loại trừ rủi ro.</span></>
            ) : (
              <>Set the standard to <span className="text-[#b72727]">eliminate risk.</span></>
            )}
          </h1>
          <p className="mt-4 text-[15px] leading-relaxed t-2">
            {t(
              "Bộ lọc 3 cấp loại trừ dần cơ hội không phù hợp. Sàn TMĐT tự động quét full 6 sàn — chiến lược chọn ở Sidebar.",
              "The 3-stage filter eliminates unfit opportunities. All 6 marketplaces are auto-crawled — strategy is set in the Sidebar.",
            )}
          </p>
        </div>
        <button className="btn-ghost" onClick={() => setFilters(initialFilters)}>
          <RefreshCcw className="h-3.5 w-3.5" />
          {t("Đặt lại mặc định", "Reset defaults")}
        </button>
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-3">
        <FilterGroup number="01" title={t("Ngách & mùa vụ", "Niche & seasonality")} subtitle={t("Chỉ giữ lại những cơ hội bạn thực sự muốn xem xét.", "Keep only the opportunities you really want.")}>
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
            <div className="flex items-center gap-1.5 font-bold text-emerald-700">
              <Zap className="h-3.5 w-3.5" />
              {t("Auto crawl full 6 sàn TMĐT", "Auto-crawl all 5 marketplaces")}
            </div>
            <p className="mt-1 text-[11px] leading-tight text-emerald-800/80">
              {t(
                "Tự động quét Amazon, TikTok Shop, Shopee, eBay, Etsy + 2,091 từ khóa CSV + kho phôi Printway.",
                "Auto-scans Amazon, TikTok Shop, Shopee, eBay, Etsy + 2,091 CSV keywords + Printway blanks.",
              )}
            </p>
          </div>
          <Select
            label={t("Mùa vụ", "Seasonality")}
            value={filters.seasonality}
            onChange={(value) => update("seasonality", value)}
            options={[
              ["Evergreen", t("Quanh năm", "Year-round")],
              ["Halloween", t("Halloween", "Halloween")],
              ["Q4_Holiday_Xmas", t("Mùa lễ Q4", "Q4 holidays")],
              ["Valentine", t("Valentine", "Valentine")],
              ["Summer_Vacation", t("Mùa hè", "Summer")],
            ]}
          />
          <div>
            <span className="field-label">{t("Ngành hàng", "Categories")}</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {categoryOptions.map(([value, label]) => (
                <TogglePill
                  key={value}
                  active={filters.categories.includes(value)}
                  onClick={() => toggle("categories", value)}
                >
                  {label}
                </TogglePill>
              ))}
            </div>
          </div>
          <div>
            <label className="field-label flex items-center justify-between">
              <span>{t("Lọc theo hãng / thương hiệu", "Filter by brand")}</span>
              {filters.targetBrand && (
                <button
                  type="button"
                  onClick={() => update("targetBrand", "")}
                  className="text-[10px] font-bold text-[#b72727] hover:underline"
                >
                  {t("Xóa lọc hãng", "Clear brand")}
                </button>
              )}
            </label>
            <input
              type="text"
              value={filters.targetBrand || ""}
              onChange={(e) => update("targetBrand", e.target.value)}
              placeholder={t("VD: Stanley, Hydro Flask, Yeti, Nike…", "e.g. Stanley, Hydro Flask, Yeti, Nike…")}
              className="input mt-1.5"
            />
          </div>
          <Range
            label={t("Tăng trưởng nhu cầu tối thiểu", "Min demand growth")}
            value={filters.growth}
            min={0}
            max={100}
            suffix="%"
            onChange={(value) => update("growth", value)}
          />
        </FilterGroup>

        <FilterGroup number="02" title={t("Hiệu quả đơn vị", "Unit economics")} subtitle={t("Đảm bảo biên lợi nhuận hợp lý trước khi ra mắt.", "Ensure healthy margins before launch.")}>
          <Range
            label={t("Biên lợi nhuận gộp tối thiểu", "Min gross margin")}
            value={filters.margin}
            min={20}
            max={80}
            suffix="%"
            onChange={(value) => update("margin", value)}
          />
          <div className="grid grid-cols-2 gap-3">
            <NumberInput label={t("Giá bán tối thiểu", "Min price")} value={filters.priceMin} onChange={(value) => update("priceMin", value)} />
            <NumberInput label={t("Giá bán tối đa", "Max price")} value={filters.priceMax} onChange={(value) => update("priceMax", value)} />
          </div>
          <NumberInput label={t("Giá vốn phôi tối đa", "Max blank cost")} value={filters.cogs} onChange={(value) => update("cogs", value)} />
          <div className="rounded-xl border border-[#e7e5e4] bg-[#fafaf9] p-4 text-xs leading-5 t-2">
            <CircleDollarSign className="mr-2 inline h-4 w-4 text-[#b72727]" />
            {t(
              "Hệ thống sẽ tính giá bán đề xuất, lợi nhuận mỗi đơn vị và điểm cơ hội từ các ràng buộc này.",
              "The system computes suggested price, profit per unit and opportunity score from these constraints.",
            )}
          </div>
        </FilterGroup>

        <FilterGroup number="03" title={t("Khả năng sản xuất", "Production capability")} subtitle={t("Ghép nhu cầu với sản phẩm bạn có thể hoàn tất đơn hàng.", "Match demand with blanks you can fulfill.")}>
          <Select
            label={t("Kho ưu tiên", "Preferred warehouse")}
            value={filters.warehouse}
            onChange={(value) => update("warehouse", value)}
            options={[
              ["US", t("Kho Mỹ — giao 2–5 ngày", "US — 2–5 day delivery")],
              ["EU", t("Kho Trung tâm EU", "EU hub")],
              ["VN", t("Xưởng Việt Nam", "Vietnam factory")],
              ["ANY", t("Mọi kho", "Any warehouse")],
            ]}
          />
          <Select
            label={t("Thời gian sản xuất tối đa", "Max production time")}
            value={String(filters.productionDays)}
            onChange={(value) => update("productionDays", Number(value))}
            options={[
              ["2", "≤ 2 " + t("ngày làm việc", "business days")],
              ["3", "≤ 3 " + t("ngày làm việc", "business days")],
              ["5", "≤ 5 " + t("ngày làm việc", "business days")],
            ]}
          />
          <div>
            <span className="field-label">{t("Kỹ thuật sản xuất", "Craft techniques")}</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {techniqueOptions.map(([value, label]) => (
                <TogglePill
                  key={value}
                  active={filters.techniques.includes(value)}
                  onClick={() => toggle("techniques", value)}
                >
                  {label}
                </TogglePill>
              ))}
            </div>
          </div>
          <div className="rounded-xl border border-[#e7e5e4] bg-[#fafaf9] px-3 py-2.5 text-xs t-2">
            <span className="font-bold text-[#57534e]">{t("Chiến lược:", "Strategy:")}</span>{" "}
            <strong className="text-[#b72727]">
              {t(
                strategies.find((s) => s.id === filters.strategy)?.labelVi ?? "",
                strategies.find((s) => s.id === filters.strategy)?.labelEn ?? "",
              )}
            </strong>
          </div>
        </FilterGroup>
      </div>

      <div className="card mt-8 flex flex-col items-start justify-between gap-5 border-l-4 !border-l-[#b72727] p-6 sm:flex-row sm:items-center animate-fade-up d-4">
        <div>
          <p className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-[#b72727]">
            {t("Sẵn sàng khi bạn sẵn sàng", "Ready when you are")}
          </p>
          <p className="mt-1.5 text-xl font-extrabold tracking-tight text-[#1c1917]">
            {t(
              "Quét tín hiệu thị trường với danh mục phôi xưởng.",
              "Scan market signals against the blank catalog.",
            )}
          </p>
        </div>
        <button onClick={onAnalyze} disabled={loading} className="btn-primary !px-9 !py-3.5 text-sm">
          {loading ? (
            <>
              <LoaderCircle className="h-4 w-4 animate-spin" />
              {t("Đang auto crawl 6 sàn + chấm điểm…", "Auto-crawling 6 platforms + scoring…")}
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              {t("Phân tích cơ hội", "Analyze opportunities")}
            </>
          )}
        </button>
      </div>
      {error && (
        <p className="mt-4 flex items-center gap-2 text-sm font-semibold text-[#b72727]">
          <ShieldCheck className="h-4 w-4" />
          {error}
        </p>
      )}
    </section>
  );
}

function FilterGroup({
  number,
  title,
  subtitle,
  children,
}: {
  number: string;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <article className="card card-hover p-5 animate-fade-up">
      <div className="flex items-center gap-3">
        <span className="font-mono text-2xl font-bold text-[#b72727]">{number}</span>
        <div>
          <h2 className="text-[15px] font-bold text-[#1c1917]">{title}</h2>
          <p className="text-[11.5px] t-3">{subtitle}</p>
        </div>
      </div>
      <div className="divider my-4" />
      <div className="space-y-4">{children}</div>
    </article>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[][];
}) {
  return (
    <div>
      <label className="field-label">{label}</label>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="select mt-1.5"
      >
        {options.map(([id, name]) => (
          <option key={id} value={id}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}

function Range({
  label,
  value,
  min,
  max,
  suffix,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  suffix: string;
  onChange: (value: number) => void;
}) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div>
      <div className="flex items-center justify-between">
        <label className="field-label">{label}</label>
        <strong className="font-mono text-[13px] text-[#b72727]">
          {value}
          {suffix}
        </strong>
      </div>
      <input
        className="range mt-3"
        type="range"
        min={min}
        max={max}
        step="5"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        style={{
          background: `linear-gradient(90deg, #b72727 0%, #b72727 ${pct}%, #e7e5e4 ${pct}%)`,
        }}
      />
    </div>
  );
}

function NumberInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <label className="field-label">{label}</label>
      <div className="relative mt-1.5">
        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-sm text-[#a8a29e]">$</span>
        <input
          className="input !pl-7"
          type="number"
          value={value}
          min="0"
          onChange={(event) => onChange(Number(event.target.value))}
        />
      </div>
    </div>
  );
}

function TogglePill({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button onClick={onClick} className={cn("chip", active && "chip-active")}>
      {active && <Check className="h-3 w-3" />}
      {children}
    </button>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SCREEN 04 — RESULTS (tabs nền tảng + Card/Table view)
   ═══════════════════════════════════════════════════════════════════ */
function Results({
  analysis,
  filters,
  setFilters,
  loading,
  error,
  onAnalyze,
  onOpen,
  onRestart,
}: {
  analysis: AnalysisResult | null;
  filters: typeof initialFilters;
  setFilters: React.Dispatch<React.SetStateAction<typeof initialFilters>>;
  loading: boolean;
  error: string;
  onAnalyze: () => void;
  onOpen: (opportunity: Opportunity) => void;
  onRestart: () => void;
}) {
  const { t, lang } = useI18n();
  const [sort, setSort] = useState<"score" | "margin" | "growth">("score");
  const [ipOnly, setIpOnly] = useState(false);
  const [marginOnly, setMarginOnly] = useState(false);
  const [platform, setPlatform] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"card" | "table">("card");

  const displayed = useMemo(
    () =>
      [...(analysis?.opportunities ?? [])]
        .filter(
          (opportunity) =>
            (!ipOnly || opportunity.ip_safety_status.includes("CLEAN")) &&
            (!marginOnly || opportunity.profit_margin_pct > 70),
        )
        .filter((opportunity) => {
          if (platform === "all") return true;
          const sources = (opportunity.marketplace_sources ?? []).join(" ").toLowerCase();
          return sources.includes(platform.toLowerCase());
        })
        .sort((a, b) =>
          sort === "score"
            ? b.opportunity_score - a.opportunity_score
            : sort === "margin"
              ? b.profit_margin_pct - a.profit_margin_pct
              : b.score_breakdown.demand_growth -
                a.score_breakdown.demand_growth,
        ),
    [analysis, sort, ipOnly, marginOnly, platform],
  );
  const averageMargin = analysis?.opportunities.length
    ? analysis.opportunities.reduce(
        (sum, item) => sum + item.profit_margin_pct,
        0,
      ) / analysis.opportunities.length
    : 0;

  return (
    <section className="animate-fade-up">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-2xl">
          <p className="eyebrow">{t("04 · Bảng xếp hạng cơ hội vàng", "04 · Golden opportunity leaderboard")}</p>
          <h1 className="mt-4 text-4xl font-extrabold leading-[1.08] tracking-tight text-[#1c1917] sm:text-5xl">
            {lang === "vi" ? (
              <>Danh sách cơ hội <span className="text-[#b72727]">chiến thắng</span> đã sẵn sàng.</>
            ) : (
              <>The list of <span className="text-[#b72727]">winning</span> opportunities is ready.</>
            )}
          </h1>
          <p className="mt-4 text-[15px] leading-relaxed t-2">
            {t(
              "Xếp hạng tự động bởi MCDA 6 trụ cột — auto crawl full 6 sàn + 2,091 tín hiệu thị trường.",
              "Ranked automatically by the 6-pillar MCDA — full auto-crawl of 6 marketplaces + 2,091 signals.",
            )}
          </p>
        </div>
        <div className="flex gap-2.5">
          <button className="btn-ghost" onClick={onRestart}>
            <Search className="h-3.5 w-3.5" />
            {t("Tìm kiếm mới", "New search")}
          </button>
          <button className="btn-primary !px-5 !py-2.5 !text-xs" onClick={onAnalyze} disabled={loading}>
            {loading ? <LoaderCircle className="h-3.5 w-3.5 animate-spin" /> : <RefreshCcw className="h-3.5 w-3.5" />}
            {t("Làm mới kết quả", "Refresh results")}
          </button>
        </div>
      </div>

      {loading && !analysis && (
        <div className="mt-8 space-y-4">
          {[0, 1, 2].map((i) => (
            <div key={i} className="card p-5">
              <div className="flex justify-between">
                <div className="space-y-3">
                  <div className="skeleton h-3 w-40" />
                  <div className="skeleton h-5 w-64" />
                </div>
                <div className="skeleton h-16 w-16 rounded-full" />
              </div>
              <div className="mt-4 grid grid-cols-6 gap-2">
                {[0, 1, 2, 3, 4, 5].map((j) => (
                  <div key={j} className="skeleton h-12" />
                ))}
              </div>
            </div>
          ))}
          <p className="flex items-center justify-center gap-2.5 py-4 text-sm font-semibold t-2">
            <LoaderCircle className="h-4 w-4 animate-spin text-[#b72727]" />
            {t(
              "AI đang auto crawl 6 sàn + quét 2,091 tín hiệu + chấm điểm 6 trụ cột…",
              "AI is auto-crawling 6 platforms + scanning 2,091 signals + scoring 6 pillars…",
            )}
          </p>
        </div>
      )}

      {analysis && (
        <>
          <div className="mt-7 grid gap-3.5 sm:grid-cols-2 xl:grid-cols-4">
            <Kpi
              icon={Target}
              label={t("Cơ hội đủ điều kiện", "Qualified opportunities")}
              value={String(analysis.total_opportunities)}
              note={t("sau khi qua bộ lọc ràng buộc", "after constraint filters")}
              delay={1}
            />
            <Kpi
              icon={TrendingUp}
              label={t("Điểm cơ hội cao nhất", "Top opportunity score")}
              value={Math.max(...analysis.opportunities.map((item) => item.opportunity_score), 0).toFixed(1)}
              note={t("trên thang điểm 100", "out of 100")}
              delay={2}
            />
            <Kpi
              icon={CircleDollarSign}
              label={t("Biên lãi gộp trung bình", "Average gross margin")}
              value={`${averageMargin.toFixed(1)}%`}
              note={t("trên toàn bộ danh sách", "across the list")}
              delay={3}
            />
            <Kpi
              icon={Zap}
              label={t("Thời gian tính toán", "Computation time")}
              value={`${analysis.execution_time_ms}ms`}
              note={t("auto crawl full + 6 trụ cột", "full auto-crawl + 6 pillars")}
              delay={4}
            />
          </div>

          {/* Platform tabs + view mode + sort */}
          <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {PLATFORM_TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setPlatform(tab.id)}
                  className={cn("chip", platform === tab.id && "chip-active")}
                >
                  {t(tab.label, tab.en)}
                  <span className="font-mono text-[10px] opacity-70">
                    {tab.id === "all"
                      ? analysis.opportunities.length
                      : analysis.opportunities.filter((o) =>
                          (o.marketplace_sources ?? []).join(" ").toLowerCase().includes(tab.id),
                        ).length}
                  </span>
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              {/* Sort */}
              <div className="seg !p-0.5">
                {(
                  [
                    ["score", t("Điểm cao nhất", "Top score")],
                    ["margin", t("Lãi dày nhất", "Top margin")],
                    ["growth", t("Tăng nhanh nhất", "Top growth")],
                  ] as const
                ).map(([id, label]) => (
                  <button
                    key={id}
                    onClick={() => setSort(id)}
                    className={cn("seg-btn !px-3 !py-1.5 !text-[11px]", sort === id && "seg-btn-active")}
                  >
                    {label}
                  </button>
                ))}
              </div>
              {/* Quick filters */}
              <button onClick={() => setIpOnly(!ipOnly)} className={cn("chip", ipOnly && "chip-active")}>
                <ShieldCheck className="h-3.5 w-3.5" />
                {t("Clean IP", "Clean IP")}
              </button>
              <button onClick={() => setMarginOnly(!marginOnly)} className={cn("chip", marginOnly && "chip-active")}>
                <CircleDollarSign className="h-3.5 w-3.5" />
                {t("Lãi > 70%", "Margin > 70%")}
              </button>
              {/* View mode */}
              <div className="seg !p-0.5">
                <button
                  onClick={() => setViewMode("card")}
                  className={cn("seg-btn !px-3 !py-1.5", viewMode === "card" && "seg-btn-active")}
                  title={t("Xem dạng thẻ", "Card view")}
                >
                  <LayoutGrid className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => setViewMode("table")}
                  className={cn("seg-btn !px-3 !py-1.5", viewMode === "table" && "seg-btn-active")}
                  title={t("Xem dạng bảng chi tiết", "Detailed table view")}
                >
                  <Table2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>

          <div className="mt-5">
            {viewMode === "card" ? (
              <div className="space-y-4">
                {displayed.map((opportunity, index) => (
                  <OpportunityCard
                    key={opportunity.id}
                    opportunity={opportunity}
                    rank={index + 1}
                    onOpen={() => onOpen(opportunity)}
                  />
                ))}
                {!displayed.length && (
                  <div className="card p-14 text-center text-sm t-2">
                    {t(
                      "Không có cơ hội nào khớp với bộ lọc hiện tại. Hãy thử tắt bớt điều kiện lọc.",
                      "No opportunities match the current filters. Try relaxing them.",
                    )}
                  </div>
                )}
              </div>
            ) : (
              <ResultsTable
                rows={displayed}
                onOpen={onOpen}
                emptyText={t(
                  "Không có cơ hội nào khớp với bộ lọc hiện tại. Hãy thử tắt bớt điều kiện lọc.",
                  "No opportunities match the current filters. Try relaxing them.",
                )}
              />
            )}
          </div>
        </>
      )}

      {error && !analysis && (
        <div className="card mt-8 p-8 text-center">
          <p className="text-sm font-semibold text-[#b72727]">{error}</p>
          <button onClick={onAnalyze} className="btn-primary mt-5">
            <RefreshCcw className="h-4 w-4" />
            {t("Thử lại", "Retry")}
          </button>
        </div>
      )}
    </section>
  );
}

function Kpi({
  icon: Icon,
  label,
  value,
  note,
  delay,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  note: string;
  delay: number;
}) {
  return (
    <article className={cn("card card-hover p-5 animate-fade-up", `d-${delay}`)}>
      <div className="flex items-center justify-between">
        <span className="text-[11.5px] font-bold uppercase tracking-wider t-3">{label}</span>
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#fdf3f3] text-[#b72727]">
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <strong className="mt-3 block font-mono text-[26px] font-bold tracking-tight text-[#1c1917]">
        {value}
      </strong>
      <small className="mt-0.5 block text-[11px] t-3">{note}</small>
    </article>
  );
}

/* ── SHARED: PW1 scoring detail (fallback client-side if API thiếu) ── */
function buildScoringDetail(opportunity: Opportunity, preset: Strategy): ScoringDetail {
  if (opportunity.scoring_detail) return opportunity.scoring_detail;

  const weights = STRATEGY_WEIGHTS[preset] ?? STRATEGY_WEIGHTS.VIRAL_TREND;
  const keys = [
    ["demand", "Nhu Cầu", "Demand", "demand_growth"],
    ["gap", "Khoảng Trống", "Market Gap", "market_gap"],
    ["margin", "Biên Lãi", "Profit Margin", "profit_margin"],
    ["supply", "Chuỗi Cung", "Supply Chain", "supply_feasibility"],
    ["safety", "Bản Quyền", "IP Safety", "ip_safety"],
    ["virality", "Viral TikTok", "TikTok Virality", "tiktok_virality"],
  ] as const;

  const pillars = keys.map(([key, lvi, len, field]) => {
    const score = opportunity.score_breakdown[field];
    const weight = weights[key];
    const sub = (opportunity.score_rationales?.[key as keyof typeof opportunity.score_rationales] ?? "")
      .split("·")
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s) => {
        const m = s.match(/^(.*?)\s*\(([\d.]+)\)$/);
        return {
          label_vi: m?.[1] ?? s,
          label_en: "",
          score: m ? Number(m[2]) : 0,
          evidence: "",
        };
      });
    return {
      key,
      label_vi: lvi,
      label_en: len,
      score,
      weight,
      contribution: Number((score * weight).toFixed(1)),
      formula_vi: "",
      formula_en: "",
      sub_scores: sub,
    };
  });

  const cleanIp =
    opportunity.ip_safety_status.includes("CLEAN") ||
    opportunity.ip_safety_status.toLowerCase().includes("sạch");
  const tier = cleanIp ? 3 : 1;
  const ipCheck = {
    tier,
    tier_label_vi: cleanIp ? "An toàn sạch 100%" : "Cảnh báo nhãn hiệu",
    tier_label_en: cleanIp ? "100% clean" : "Trademark alert",
    score: opportunity.score_breakdown.ip_safety,
    status: cleanIp ? "CLEAN_IP" : "TRADEMARK_ALERT",
    verdict_vi: cleanIp ? "GO — không vi phạm bản quyền" : "STOP — rủi ro nhãn hiệu",
    verdict_en: cleanIp ? "GO — no IP infringement" : "STOP — trademark risk",
    notes: opportunity.ip_safety_status,
  };

  const total = opportunity.opportunity_score;
  const verdict =
    total >= 75 && tier === 3
      ? { result: "GO", label_vi: "GO — Triển khai ngay", label_en: "GO — Launch now", reasons_vi: ["Điểm tổng ≥ 75", "Bản quyền sạch 100%"], reasons_en: ["Total ≥ 75", "100% clean IP"] }
      : total >= 55
        ? { result: "CAUTION", label_vi: "CAUTION — Thận trọng", label_en: "CAUTION — Proceed carefully", reasons_vi: ["Điểm ở mức trung bình"], reasons_en: ["Mid-range score"] }
        : { result: "STOP", label_vi: "STOP — Loại khỏi danh mục", label_en: "STOP — Exclude", reasons_vi: ["Điểm dưới ngưỡng"], reasons_en: ["Below threshold"] };

  return {
    weights,
    strategy_preset: preset,
    formula_total: "S = Σ w_k · S_k,  Σ w_k = 1.0",
    pillars,
    ip_check: ipCheck,
    verdict,
  };
}

function ScoringDetailPanel({
  opportunity,
  preset,
}: {
  opportunity: Opportunity;
  preset: Strategy;
}) {
  const { t, lang } = useI18n();
  const detail = buildScoringDetail(opportunity, preset);
  const verdict = detail.verdict;
  const ip = detail.ip_check;

  return (
    <div className="space-y-4">
      {/* Verdict banner — PW1 4.3 */}
      {verdict && (
        <div
          className={cn(
            "flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3",
            verdict.result === "GO"
              ? "border-emerald-200 bg-emerald-50"
              : verdict.result === "CAUTION"
                ? "border-amber-200 bg-amber-50"
                : "border-[#f3d6d6] bg-[#fdf3f3]",
          )}
        >
          <div className="flex items-center gap-2.5">
            <span
              className={cn(
                "grid h-8 w-8 place-items-center rounded-lg font-mono text-[11px] font-extrabold text-white",
                verdict.result === "GO" ? "bg-emerald-600" : verdict.result === "CAUTION" ? "bg-amber-600" : "bg-[#b72727]",
              )}
            >
              {verdict.result}
            </span>
            <div>
              <strong className={cn(
                "block text-sm font-extrabold",
                verdict.result === "GO" ? "text-emerald-800" : verdict.result === "CAUTION" ? "text-amber-800" : "text-[#9a1f1f]",
              )}>
                {lang === "vi" ? verdict.label_vi : verdict.label_en}
              </strong>
              <span className="text-[11px] t-2">
                {t("Kết luận cuối cùng (PW1 4.3)", "Final verdict (PW1 4.3)")}
              </span>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {(lang === "vi" ? verdict.reasons_vi : verdict.reasons_en).map((r) => (
              <span key={r} className="badge badge-gray !text-[10px]">{r}</span>
            ))}
          </div>
        </div>
      )}

      {/* Weights */}
      <div className="flex flex-wrap gap-1.5">
        {detail.pillars.map((p) => (
          <span key={p.key} className="badge badge-gray !text-[10px] font-mono">
            {lang === "vi" ? p.label_vi : p.label_en} · w={p.weight}
          </span>
        ))}
      </div>

      {/* Pillars detail */}
      <div className="grid gap-3 lg:grid-cols-2">
        {detail.pillars.map((p) => (
          <div key={p.key} className="rounded-xl border border-[#e7e5e4] bg-white p-3.5">
            <div className="flex items-center justify-between gap-2">
              <strong className="text-[12.5px] font-extrabold text-[#1c1917]">
                {lang === "vi" ? p.label_vi : p.label_en}
              </strong>
              <span className="font-mono text-[11px] font-bold t-3">
                {p.score}
                <span className="text-[#b72727]"> × {p.weight}</span>
                <span className="text-[#b72727]"> = {p.contribution}</span>
              </span>
            </div>
            <div className="pillar-bar mt-2">
              <div className="pillar-bar-fill" style={{ width: `${Math.min(p.score, 100)}%` }} />
            </div>
            {p.formula_vi && (
              <p className="mt-2 rounded-lg bg-[#fafaf9] px-2 py-1 font-mono text-[9.5px] leading-relaxed t-3">
                {lang === "vi" ? p.formula_vi : p.formula_en}
              </p>
            )}
            {(() => {
              const rationale =
                opportunity.score_rationales?.[p.key as keyof typeof opportunity.score_rationales] ||
                (opportunity.score_rationales as any)?.[p.key] ||
                (opportunity as any).score_breakdown_details?.[p.key]?.reason;
              if (rationale) {
                return (
                  <div className="mt-2.5 rounded-lg border border-[#f3d6d6] bg-[#fdf3f3]/70 p-2.5 text-[11px]">
                    <span className="flex items-center gap-1 text-[11px] font-bold text-[#b72727]">
                      <Lightbulb className="h-3 w-3" /> {t("Chi tiết phân tích & Benchmark:", "Analysis & Benchmark:")}
                    </span>
                    <div className="mt-1 whitespace-pre-line text-[11px] leading-relaxed text-[#44403c]">
                      {rationale}
                    </div>
                  </div>
                );
              }
              return null;
            })()}
            {p.sub_scores.length > 0 && (
              <div className="mt-2.5 space-y-1.5">
                {p.sub_scores.map((sub, idx) => (
                  <div key={idx} className="flex items-start justify-between gap-3 text-[11px]">
                    <div className="min-w-0">
                      <span className="block font-semibold t-2">
                        {lang === "vi" ? sub.label_vi : sub.label_en || sub.label_vi}
                      </span>
                      {sub.evidence && <span className="block text-[10px] t-3">{sub.evidence}</span>}
                    </div>
                    <span className="shrink-0 font-mono text-[11px] font-bold text-[#b72727]">
                      {sub.score}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* IP check — PW1 4.2 */}
      {ip && (
        <div className="rounded-xl border border-[#e7e5e4] bg-white p-3.5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <strong className="flex items-center gap-1.5 text-[12.5px] font-extrabold text-[#1c1917]">
              <ShieldCheck className="h-4 w-4 text-[#b72727]" />
              {t("Kiểm tra bản quyền & thương hiệu", "Copyright & trademark check")}
              <span className="text-[10px] font-bold uppercase tracking-wider t-3">(PW1 4.2)</span>
            </strong>
            <span
              className={cn(
                "badge",
                ip.tier === 3 ? "badge-emerald" : ip.tier === 2 ? "badge-amber" : "badge-red",
              )}
            >
              {t("Tầng", "Tier")} {ip.tier} · {ip.score}/100
            </span>
          </div>
          <p className="mt-2 text-[11.5px] leading-relaxed t-2">
            <strong className="text-[#1c1917]">
              {lang === "vi" ? ip.tier_label_vi : ip.tier_label_en}:
            </strong>{" "}
            {lang === "vi" ? ip.verdict_vi : ip.verdict_en}
          </p>
          {ip.notes && <p className="mt-1 text-[11px] leading-relaxed t-3">{ip.notes}</p>}
        </div>
      )}

      <p className="text-center font-mono text-[10px] t-3">{detail.formula_total}</p>
    </div>
  );
}

function PriceChartCard({ opportunity }: { opportunity: Opportunity }) {
  const { t } = useI18n();
  return (
    <div className="card p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h4 className="flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-[#b72727]">
            <BarChart3 className="h-3.5 w-3.5" />
            {t("Biểu đồ giá thị trường & đệm lãi gộp (6 tháng)", "Market price & margin cushion (6 months)")}
          </h4>
          <p className="text-[10px] t-3">
            {t("Giá bán lẻ đề xuất vs giá trung bình sàn & giá vốn phôi Printway", "Suggested retail vs marketplace avg & Printway blank cost")}
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-bold">
          <span className="badge badge-red">{t("Đề xuất", "Suggested")}: {money(opportunity.suggested_price)}</span>
          <span className="badge badge-gray">{t("Giá vốn", "COGS")}: {money(opportunity.base_cost)}</span>
        </div>
      </div>
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={opportunity.price_chart_data || []}>
            <defs>
              <linearGradient id={`colorPrice-${opportunity.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#b72727" stopOpacity={0.18} />
                <stop offset="95%" stopColor="#b72727" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0efed" />
            <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#78716c" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: "#78716c" }} unit="$" axisLine={false} tickLine={false} width={46} />
            <RechartsTooltip
              formatter={(value) => [`$${Number(value).toFixed(2)}`, ""]}
              labelStyle={{ color: "#57534e", fontWeight: 700, fontSize: 11 }}
              contentStyle={{
                background: "#ffffff",
                border: "1px solid #e7e5e4",
                borderRadius: 12,
                fontSize: 11,
              }}
              itemStyle={{ color: "#1c1917" }}
            />
            <Area
              type="monotone"
              dataKey="suggested_price"
              name={t("Giá bán đề xuất", "Suggested price")}
              stroke="#b72727"
              strokeWidth={2.5}
              fillOpacity={1}
              fill={`url(#colorPrice-${opportunity.id})`}
              dot={{ r: 2.5, fill: "#b72727", strokeWidth: 0 }}
            />
            <Line
              type="monotone"
              dataKey="market_avg"
              name={t("Giá TB sàn đối thủ", "Competitor avg price")}
              stroke="#d97706"
              strokeWidth={1.6}
              strokeDasharray="5 4"
              dot={{ r: 2, fill: "#d97706", strokeWidth: 0 }}
            />
            <Line
              type="monotone"
              dataKey="cogs"
              name={t("Giá vốn phôi xưởng", "Blank cost")}
              stroke="#7c3aed"
              strokeWidth={1.6}
              dot={{ r: 2, fill: "#7c3aed", strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2.5 flex items-center justify-between border-t border-[#f0efed] pt-2.5 text-[10px] t-3">
        <span>
          {t("Khoảng giá thị trường:", "Market price range:")}{" "}
          <strong className="text-[#1c1917]">
            ${opportunity.price_min?.toFixed(2) || "19.99"} – ${opportunity.price_max?.toFixed(2) || "39.99"}
          </strong>
        </span>
        <span className="font-bold text-emerald-700">
          {t("Lãi gộp dày:", "Thick gross profit:")} +{money(opportunity.profit_per_unit)}/sp ({opportunity.profit_margin_pct}%)
        </span>
      </div>
    </div>
  );
}

function UnitEconomicsBox({ opportunity }: { opportunity: Opportunity }) {
  const { t } = useI18n();
  return (
    <div className="card-2 flex flex-col justify-between p-4">
      <div>
        <p className="text-[10.5px] font-extrabold uppercase tracking-[0.14em] t-3">
          {t("Kinh tế đơn vị", "Unit economics")}
        </p>
        <div className="mt-3 grid grid-cols-3 gap-2 text-center">
          <Metric value={money(opportunity.base_cost)} label={t("Giá phôi", "Blank cost")} />
          <Metric value={money(opportunity.suggested_price)} label={t("Giá bán", "Retail price")} />
          <Metric value={`${opportunity.profit_margin_pct}%`} label={t("Biên lãi", "Margin")} accent />
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-[#e7e5e4] pt-3 text-[11px]">
        <span className="truncate t-2">{opportunity.matched_product_name}</span>
        <strong className="ml-2 shrink-0 font-mono font-bold text-emerald-700">
          +{money(opportunity.profit_per_unit)}/sp
        </strong>
      </div>
    </div>
  );
}

/* ── SHARED: 6 pillar chips interactive ── */
function PillarsInteractive({ opportunity }: { opportunity: Opportunity }) {
  const { t, lang } = useI18n();
  const [activePillar, setActivePillar] = useState<string>("demand");
  const detail = buildScoringDetail(opportunity, "VIRAL_TREND");
  const pillarMap = new Map(detail.pillars.map((p) => [p.key, p]));

  const pillars = [
    { key: "demand", field: "demand_growth", labelVi: "Nhu cầu", labelEn: "Demand", icon: "📊" },
    { key: "gap", field: "market_gap", labelVi: "Khoảng trống", labelEn: "Market Gap", icon: "🎯" },
    { key: "margin", field: "profit_margin", labelVi: "Biên lãi", labelEn: "Margin", icon: "💰" },
    { key: "supply", field: "supply_feasibility", labelVi: "Chuỗi cung", labelEn: "Supply", icon: "⚡" },
    { key: "safety", field: "ip_safety", labelVi: "Bản quyền", labelEn: "IP Safety", icon: "🛡️" },
    { key: "virality", field: "tiktok_virality", labelVi: "Viral TikTok", labelEn: "Virality", icon: "📱" },
  ] as const;

  const activePillarObj = pillars.find((p) => p.key === activePillar) || pillars[0];
  const scoreVal = Number(opportunity.score_breakdown[activePillarObj.field] || 0).toFixed(0);

  const rationale =
    opportunity.score_rationales?.[activePillarObj.key as keyof typeof opportunity.score_rationales] ||
    opportunity.score_rationales?.[activePillarObj.field as keyof typeof opportunity.score_rationales] ||
    (opportunity as any).score_breakdown_details?.[activePillarObj.key]?.reason ||
    (opportunity as any).score_breakdown_details?.[activePillarObj.field]?.reason ||
    (opportunity as any).rationales?.[activePillarObj.key] ||
    (opportunity as any).rationales?.[activePillarObj.field] ||
    t("Số liệu được tính toán dựa trên thuật toán định lượng đa biến 6 trụ cột của Printway.", "Calculated via Printway 6-pillar quantitative model.");

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-extrabold uppercase tracking-[0.14em] text-[#78716c]">
          {t("Bóc tách định lượng 6 trụ cột", "6-Pillar Quantitative Breakdown")}
        </p>
        <span className="text-[10.5px] font-semibold text-[#a8a29e]">
          {t("Bấm chọn trụ cột để xem giải trình số liệu", "Select a pillar to view metrics")}
        </span>
      </div>

      {/* Pillar selector buttons */}
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        {pillars.map((p) => {
          const isSelected = activePillar === p.key;
          const score = Number(opportunity.score_breakdown[p.field] || 0).toFixed(0);
          return (
            <button
              type="button"
              key={p.key}
              onClick={() => setActivePillar(p.key)}
              className={cn(
                "group relative flex flex-col rounded-xl border p-2.5 text-left transition-all",
                isSelected
                  ? "border-[#b72727] bg-[#fff5f5] shadow-sm ring-1 ring-[#b72727]"
                  : "border-[#e7e5e4] bg-white hover:border-[#d6d3d1] hover:bg-[#fafaf9]"
              )}
            >
              <div className="flex items-center justify-between gap-1">
                <span className="text-[11px]">{p.icon}</span>
                <span className={cn("font-mono text-xs font-black", isSelected ? "text-[#b72727]" : "text-[#1c1917]")}>
                  {score}
                </span>
              </div>
              <span className={cn("mt-1.5 block truncate text-[10px] font-bold", isSelected ? "text-[#b72727]" : "text-[#78716c]")}>
                {lang === "vi" ? p.labelVi : p.labelEn}
              </span>
              <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-[#f0efed]">
                <div
                  className={cn("h-full transition-all duration-300", isSelected ? "bg-[#b72727]" : "bg-[#a8a29e]")}
                  style={{ width: `${Math.min(Number(score), 100)}%` }}
                />
              </div>
            </button>
          );
        })}
      </div>

      {/* Rationale & Benchmark Explanation Box */}
      <div className="rounded-xl border border-[#e7e5e4] bg-white p-4 shadow-sm">
        <div className="mb-2.5 flex items-center justify-between border-b border-[#f0efed] pb-2.5">
          <div className="flex items-center gap-2">
            <span className="text-base">{activePillarObj.icon}</span>
            <strong className="text-xs font-extrabold text-[#1c1917]">
              {lang === "vi" ? activePillarObj.labelVi : activePillarObj.labelEn}:
            </strong>
            <span className="rounded-lg bg-[#b72727] px-2 py-0.5 font-mono text-[11px] font-bold text-white">
              {scoreVal}/100
            </span>
          </div>
          <span className="rounded-md border border-[#e7e5e4] bg-[#fafaf9] px-2 py-0.5 text-[10.5px] font-semibold text-[#78716c]">
            {t("Đối chuẩn Benchmark Ngành", "Industry Benchmark")}
          </span>
        </div>
        <div className="whitespace-pre-line text-xs font-medium leading-relaxed text-[#374151]">
          {rationale}
        </div>
      </div>
    </div>
  );
}

/* ── RESULTS TABLE — kiểu shadcn DataTable ── */
function ResultsTable({
  rows,
  onOpen,
  emptyText,
}: {
  rows: Opportunity[];
  onOpen: (opportunity: Opportunity) => void;
  emptyText: string;
}) {
  const { t, lang } = useI18n();
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="card overflow-hidden animate-fade-up">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[860px] text-sm">
          <thead>
            <tr className="border-b border-[#e7e5e4] bg-[#fafaf9] text-left text-[10.5px] font-extrabold uppercase tracking-wider t-3">
              <th className="w-12 px-4 py-3">#</th>
              <th className="px-4 py-3">{t("Sản phẩm & ngách", "Product & niche")}</th>
              <th className="hidden px-4 py-3 md:table-cell">{t("Nguồn dữ liệu", "Data sources")}</th>
              <th className="px-4 py-3">{t("Điểm", "Score")}</th>
              <th className="hidden px-4 py-3 sm:table-cell">{t("Biên lãi", "Margin")}</th>
              <th className="hidden px-4 py-3 sm:table-cell">{t("Lãi/sp", "Profit/unit")}</th>
              <th className="hidden px-4 py-3 lg:table-cell">{t("Giá bán", "Price")}</th>
              <th className="hidden px-4 py-3 md:table-cell">{t("Bản quyền", "IP")}</th>
              <th className="w-12 px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {rows.map((opp, index) => {
              const isCleanIp =
                opp.ip_safety_status.includes("CLEAN") ||
                opp.ip_safety_status.toLowerCase().includes("sạch");
              const isOpen = expanded === opp.id;
              return (
                <Fragment key={opp.id}>
                  <tr
                    className={cn(
                      "cursor-pointer border-t border-[#f0efed] transition hover:bg-[#fafaf9]",
                      isOpen && "bg-[#fafaf9]",
                    )}
                    onClick={() => setExpanded(isOpen ? null : opp.id)}
                  >
                    <td className="px-4 py-3.5">
                      <span
                        className={cn(
                          "grid h-7 w-7 place-items-center rounded-lg font-mono text-xs font-bold",
                          index === 0 ? "rank-1" : index === 1 ? "rank-2" : index === 2 ? "rank-3" : "rank-n",
                        )}
                      >
                        {index === 0 ? <Crown className="h-3.5 w-3.5" /> : index + 1}
                      </span>
                    </td>
                    <td className="max-w-[320px] px-4 py-3.5">
                      <div className="flex items-center gap-3">
                        {((opp as any).image_url || (opp as any).img_url || (opp as any).thumbnail) && (
                          <img
                            src={(opp as any).image_url || (opp as any).img_url || (opp as any).thumbnail}
                            alt={opp.name}
                            className="h-10 w-10 shrink-0 rounded-lg border border-[#e7e5e4] object-cover"
                            loading="lazy"
                          />
                        )}
                        <div className="min-w-0 flex-1">
                          <strong className="block truncate text-[13.5px] font-bold text-[#1c1917]">{opp.name}</strong>
                          <span className="block truncate text-[11px] t-3">{opp.target_niche}</span>
                          <span className="badge badge-red mt-1 !text-[9.5px]">{categoryName(opp.category)}</span>
                        </div>
                      </div>
                    </td>
                    <td className="hidden px-4 py-3.5 md:table-cell">
                      <div className="flex flex-wrap gap-1">
                        {(opp.marketplace_sources ?? []).slice(0, 3).map((source) => (
                          <span key={source} className="badge badge-sky !text-[9.5px]">{source}</span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[15px] font-bold text-[#1c1917]">
                          {opp.opportunity_score}
                        </span>
                        <div className="h-1.5 w-14 rounded-full bg-[#e7e5e4]">
                          <div
                            className="h-1.5 rounded-full bg-[#b72727]"
                            style={{ width: `${Math.min(opp.opportunity_score, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="hidden px-4 py-3.5 font-mono text-[12.5px] font-bold text-[#1c1917] sm:table-cell">
                      {opp.profit_margin_pct}%
                    </td>
                    <td className="hidden px-4 py-3.5 font-mono text-[12.5px] font-bold text-emerald-700 sm:table-cell">
                      +{money(opp.profit_per_unit)}
                    </td>
                    <td className="hidden px-4 py-3.5 font-mono text-[12.5px] t-2 lg:table-cell">
                      {money(opp.suggested_price)}
                    </td>
                    <td className="hidden px-4 py-3.5 md:table-cell">
                      <span className={cn("badge", isCleanIp ? "badge-emerald" : "badge-amber")}>
                        {isCleanIp ? t("Clean IP", "Clean IP") : t("Cần duyệt", "Review")}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <ChevronDown
                        className={cn("h-4 w-4 text-[#a8a29e] transition-transform", isOpen && "rotate-180")}
                      />
                    </td>
                  </tr>

                  {isOpen && (
                    <tr className="border-t border-[#f0efed]">
                      <td colSpan={9} className="bg-[#fafaf9] px-5 py-5">
                        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.9fr]">
                          <PillarsInteractive opportunity={opp} />
                          <UnitEconomicsBox opportunity={opp} />
                        </div>

                        <div className="mt-4">
                          <PriceChartCard opportunity={opp} />
                        </div>

                        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-[#e7e5e4] pt-4">
                          <span className="flex items-center gap-1.5 text-xs t-2">
                            <Flame className="h-3.5 w-3.5 text-[#b72727]" />
                            {opp.trend_velocity}
                          </span>
                          <div className="flex gap-2">
                            <span className="btn-soft !cursor-default">
                              <Factory className="h-3.5 w-3.5" />
                              {opp.matched_sku}
                            </span>
                            <button onClick={() => onOpen(opp)} className="btn-primary !px-5 !py-2 !text-xs">
                              {t("Xem Brief & chiến lược marketing", "View brief & marketing strategy")}
                              <ArrowRight className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
            {!rows.length && (
              <tr>
                <td colSpan={9} className="px-5 py-14 text-center text-sm t-2">
                  {emptyText}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   OPPORTUNITY CARD (mode Card)
   ═══════════════════════════════════════════════════════════════════ */
function ScoreRing({ score, size = 74 }: { score: number; size?: number }) {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const timer = window.setTimeout(() => setProgress(score), 60);
    return () => window.clearTimeout(timer);
  }, [score]);
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#efeeec"
          strokeWidth="6"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#b72727"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - (progress / 100) * circumference}
          style={{ transition: "stroke-dashoffset 1.1s cubic-bezier(0.22, 1, 0.36, 1)" }}
        />
      </svg>
      <div className="absolute inset-0 grid place-items-center">
        <span className="font-mono font-bold text-[#1c1917]" style={{ fontSize: size * 0.26 }}>
          {score}
        </span>
      </div>
    </div>
  );
}

function OpportunityCard({
  opportunity,
  rank,
  onOpen,
}: {
  opportunity: Opportunity;
  rank: number;
  onOpen: () => void;
}) {
  const { t, lang } = useI18n();
  const [showAnalysis, setShowAnalysis] = useState(false);

  const isCleanIp =
    opportunity.ip_safety_status.includes("CLEAN") ||
    opportunity.ip_safety_status.toLowerCase().includes("sạch");

  return (
    <article className="card card-hover overflow-hidden">
      {/* Header */}
      <div className="flex flex-col gap-4 p-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-start gap-4">
          <span
            className={cn(
              "grid h-11 w-11 shrink-0 place-items-center rounded-xl font-mono text-sm font-bold",
              rank === 1 ? "rank-1" : rank === 2 ? "rank-2" : rank === 3 ? "rank-3" : "rank-n",
            )}
          >
            {rank === 1 ? <Crown className="h-4 w-4" /> : `#${rank}`}
          </span>
          {((opportunity as any).image_url || (opportunity as any).img_url || (opportunity as any).thumbnail) && (
            <img
              src={(opportunity as any).image_url || (opportunity as any).img_url || (opportunity as any).thumbnail}
              alt={opportunity.name}
              className="h-14 w-14 shrink-0 rounded-xl border border-[#e7e5e4] object-cover shadow-sm transition hover:scale-105"
              loading="lazy"
            />
          )}
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="badge badge-red">{categoryName(opportunity.category)}</span>
              {opportunity.brand_reference && (
                <span className="badge badge-violet">🏷 {opportunity.brand_reference}</span>
              )}
              {(opportunity.marketplace_sources ?? []).slice(0, 3).map((source) => (
                <span key={source} className="badge badge-sky">{source}</span>
              ))}
              <span className={cn("badge", isCleanIp ? "badge-emerald" : "badge-amber")}>
                {isCleanIp ? t("Sạch bản quyền", "Clean IP") : t("Cần duyệt bản quyền", "IP review needed")}
              </span>
            </div>
            <h2 className="mt-1.5 text-lg font-extrabold tracking-tight text-[#1c1917] sm:text-xl">
              {opportunity.name}
            </h2>
            <p className="text-xs t-3">{opportunity.target_niche}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center">
          <ScoreRing score={opportunity.opportunity_score} />
          <div>
            <span className="block text-[10px] font-extrabold uppercase tracking-[0.14em] t-3">
              Opportunity<br />Score
            </span>
            <span className="mt-0.5 inline-block rounded-lg border border-[#f3d6d6] bg-[#fdf3f3] px-2.5 py-1 font-mono text-[11px] font-bold text-[#b72727]">
              /100
            </span>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="grid gap-5 border-t border-[#f0efed] p-5 lg:grid-cols-[1.35fr_0.9fr]">
        <div>
          <PillarsInteractive opportunity={opportunity} />
        </div>
        <UnitEconomicsBox opportunity={opportunity} />
      </div>

      {/* Expandable: chart + scoring detail PW1 */}
      {showAnalysis && (
        <div className="border-t border-[#f0efed] bg-[#fafaf9] p-5 animate-fade-up">
          <div className="grid gap-4 lg:grid-cols-[1.15fr_1fr]">
            <PriceChartCard opportunity={opportunity} />
            <ScoringDetailPanel opportunity={opportunity} preset="VIRAL_TREND" />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[#f0efed] bg-[#fafaf9] px-5 py-3">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs t-2">
            <Flame className="h-3.5 w-3.5 text-[#b72727]" />
            {opportunity.trend_velocity}
          </span>
          <button onClick={() => setShowAnalysis(!showAnalysis)} className="btn-soft">
            {showAnalysis ? <ChevronUp className="h-3.5 w-3.5" /> : <BarChart3 className="h-3.5 w-3.5" />}
            {showAnalysis
              ? t("Ẩn chấm điểm chi tiết", "Hide detailed scoring")
              : t("Xem chấm điểm chi tiết PW1", "View detailed PW1 scoring")}
          </button>
        </div>
        <button onClick={onOpen} className="btn-primary !rounded-full !px-5 !py-2 !text-xs">
          {t("Xem chi tiết & chiến lược marketing", "View details & marketing strategy")}
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </article>
  );
}

function Metric({ value, label, accent }: { value: string; label: string; accent?: boolean }) {
  return (
    <div className="rounded-xl border border-[#e7e5e4] bg-white p-2">
      <strong className={cn("block font-mono text-[13.5px] font-bold", accent ? "text-[#b72727]" : "text-[#1c1917]")}>
        {value}
      </strong>
      <small className="text-[9px] font-bold uppercase tracking-wider t-3">{label}</small>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   BRIEF MODAL
   ═══════════════════════════════════════════════════════════════════ */
function BriefModal({
  opportunity,
  onClose,
}: {
  opportunity: Opportunity;
  onClose: () => void;
}) {
  const { t } = useI18n();
  const radarData = [
    { subject: t("Nhu Cầu", "Demand"), value: opportunity.score_breakdown.demand_growth },
    { subject: t("Khoảng Trống", "Gap"), value: opportunity.score_breakdown.market_gap },
    { subject: t("Biên Lãi", "Margin"), value: opportunity.score_breakdown.profit_margin },
    { subject: t("Chuỗi Cung", "Supply"), value: opportunity.score_breakdown.supply_feasibility },
    { subject: t("Bản Quyền", "IP"), value: opportunity.score_breakdown.ip_safety },
    { subject: t("Viral TikTok", "TikTok"), value: opportunity.score_breakdown.tiktok_virality },
  ];

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Product details">
      <div className="modal-panel">
        <div className="flex items-start justify-between gap-4 border-b border-[#e7e5e4] bg-white px-6 py-5 sm:px-8">
          <div>
            <p className="eyebrow">{t("05 · Chi tiết sản phẩm & số liệu thị trường", "05 · Product details & market metrics")}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <h2 className="text-2xl font-extrabold tracking-tight text-[#1c1917] sm:text-3xl">
                {opportunity.name}
              </h2>
              {opportunity.brand_reference && (
                <span className="badge badge-violet">🏷 {opportunity.brand_reference}</span>
              )}
              {(opportunity.marketplace_sources ?? []).map((source) => (
                <span key={source} className="badge badge-sky">{source}</span>
              ))}
            </div>
          </div>
          <button
            className="grid h-9 w-9 shrink-0 place-items-center rounded-xl border border-[#e7e5e4] text-[#a8a29e] transition hover:border-[#b72727]/40 hover:text-[#b72727]"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="bg-[#fafaf9] p-5 sm:p-7">
          <div className="space-y-5">
            {/* Scoring detail PW1 */}
            <ScoringDetailPanel opportunity={opportunity} preset="VIRAL_TREND" />

            <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="space-y-5">
                <div className="card flex items-center gap-4 p-4">
                  {((opportunity as any).image_url || (opportunity as any).img_url || (opportunity as any).thumbnail) ? (
                    <img
                      src={(opportunity as any).image_url || (opportunity as any).img_url || (opportunity as any).thumbnail}
                      alt={opportunity.name}
                      className="h-20 w-20 shrink-0 rounded-2xl border border-[#e7e5e4] object-cover shadow-sm"
                    />
                  ) : (
                    <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-[#b72727] font-mono text-2xl font-bold text-white">
                      {opportunity.opportunity_score}
                    </span>
                  )}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="badge badge-red">{categoryName(opportunity.category)}</span>
                      <span className="rounded-lg bg-[#b72727] px-2 py-0.5 font-mono text-xs font-bold text-white">
                        {opportunity.opportunity_score}/100
                      </span>
                    </div>
                    <p className="mt-2 text-xs t-2">
                      {t("Tệp khách hàng:", "Target audience:")}{" "}
                      <strong className="text-[#1c1917]">{opportunity.target_audience}</strong>
                    </p>
                  </div>
                </div>

                <div className="card p-5">
                  <h3 className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-[#b72727]">
                    <Quote className="h-3.5 w-3.5" />
                    {t("Đặc điểm sản phẩm & Điểm giải quyết", "Product features & solution")}
                  </h3>
                  <p className="mt-2.5 text-sm font-medium leading-relaxed t-2">
                    {opportunity.key_pain_point_solved}
                  </p>
                  {opportunity.negative_reviews_summary && opportunity.negative_reviews_summary.length > 0 && (
                    <>
                      <h4 className="mt-4 text-[11px] font-extrabold uppercase tracking-wider t-3">
                        {t("Phản hồi thị trường & Điểm cần tối ưu", "Market feedback & optimization")}
                      </h4>
                      <div className="mt-2.5 space-y-2">
                        {opportunity.negative_reviews_summary.map((review) => (
                          <blockquote key={review} className="quote-block text-xs leading-relaxed t-2">
                            {review}
                          </blockquote>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="space-y-5">
                <div className="card p-5">
                  <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#1c1917]">
                    {t("Kinh tế đơn vị & điểm hòa vốn", "Unit economics & break-even")}
                  </h3>
                  <dl className="mt-3 divide-y divide-[#f0efed] text-xs">
                    {[
                      [t("Giá vốn phôi Printway (COGS)", "Printway blank cost (COGS)"), money(opportunity.base_cost)],
                      [t("Giá bán lẻ đề xuất thị trường", "Suggested retail price"), money(opportunity.suggested_price)],
                      [t("Lãi gộp trên mỗi đơn vị", "Gross profit per unit"), `+${money(opportunity.profit_per_unit)}`],
                      [t("Tỷ suất lợi nhuận gộp", "Gross margin %"), `${opportunity.profit_margin_pct}%`],
                      [t("Mã phôi Printway khuyến nghị", "Recommended Printway SKU"), opportunity.matched_sku],
                      [t("Điểm hòa vốn ($1,000 Ads)", "Break-even ($1,000 ads)"), `~${Math.ceil(1000 / (opportunity.profit_per_unit || 1))} ${t("sản phẩm", "units")}`],
                    ].map(([term, value]) => (
                      <div className="flex justify-between gap-3 py-2.5" key={term as string}>
                        <dt className="t-3">{term}</dt>
                        <dd className="text-right font-mono font-bold text-[#1c1917]">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>

                <div className="card p-4">
                  <p className="text-[11px] font-extrabold uppercase tracking-wider t-3">
                    {t("Radar 6 trụ cột cơ hội", "6-pillar opportunity radar")}
                  </p>
                  <div className="mt-2 h-60">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData} outerRadius="74%">
                        <PolarGrid stroke="#e7e5e4" />
                        <PolarAngleAxis
                          dataKey="subject"
                          tick={{ fill: "#57534e", fontSize: 10.5, fontWeight: 700 }}
                        />
                        <RadarShape
                          dataKey="value"
                          stroke="#b72727"
                          fill="#b72727"
                          fillOpacity={0.22}
                          strokeWidth={2}
                          dot={{ r: 3, fill: "#b72727", strokeWidth: 0 }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>

            <PriceChartCard opportunity={opportunity} />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[#e7e5e4] bg-white px-6 py-4 sm:px-8">
          <button onClick={() => window.print()} className="btn-ghost">
            <Download className="h-3.5 w-3.5" />
            {t("Xuất file / In báo cáo PDF", "Export / Print PDF report")}
          </button>
          <button onClick={onClose} className="text-xs font-bold t-3 transition hover:text-[#1c1917]">
            {t("Đóng", "Close")}
          </button>
        </div>
      </div>
    </div>
  );
}

