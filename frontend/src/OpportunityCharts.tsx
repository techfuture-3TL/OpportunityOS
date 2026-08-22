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
import { BarChart3 } from "lucide-react";
import { useI18n } from "./i18n";
import type { Opportunity } from "./types";

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

export function PriceChartCard({ opportunity }: { opportunity: Opportunity }) {
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
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-bold">
          <span className="badge badge-red">{t("Đề xuất", "Suggested")}: {money(opportunity.suggested_price)}</span>
          <span className="badge badge-gray">{t("Giá vốn", "COGS")}: {money(opportunity.base_cost)}</span>
        </div>
      </div>
      <div className="h-48 w-full" aria-label={t("Biểu đồ giá trong 6 tháng", "Six-month price chart")}>
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
      <div className="mt-2.5 flex flex-col gap-1 border-t border-[#f0efed] pt-2.5 text-[10px] t-3 sm:flex-row sm:items-center sm:justify-between">
        <span>
          {t("Khoảng giá thị trường:", "Market price range:")} {" "}
          <strong className="text-[#1c1917]">
            ${opportunity.price_min?.toFixed(2) || "19.99"} – ${opportunity.price_max?.toFixed(2) || "39.99"}
          </strong>
        </span>
        <span className="font-bold text-emerald-700">
          {t("Lãi gộp dày:", "Thick gross profit:")} +{money(opportunity.profit_per_unit)}/{t("sp", "unit")} ({opportunity.profit_margin_pct}%)
        </span>
      </div>
    </div>
  );
}

export function OpportunityRadar({ opportunity }: { opportunity: Opportunity }) {
  const { t } = useI18n();
  const data = [
    { subject: t("Nhu Cầu", "Demand"), value: opportunity.score_breakdown.demand_growth },
    { subject: t("Khoảng Trống", "Gap"), value: opportunity.score_breakdown.market_gap },
    { subject: t("Biên Lãi", "Margin"), value: opportunity.score_breakdown.profit_margin },
    { subject: t("Chuỗi Cung", "Supply"), value: opportunity.score_breakdown.supply_feasibility },
    { subject: t("Bản Quyền", "IP"), value: opportunity.score_breakdown.ip_safety },
    { subject: t("Viral TikTok", "TikTok"), value: opportunity.score_breakdown.tiktok_virality },
  ];

  return (
    <div className="mt-2 h-56 sm:h-60" aria-label={t("Radar 6 trụ cột cơ hội", "Six-pillar opportunity radar")}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} outerRadius="74%">
          <PolarGrid stroke="#e7e5e4" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: "#57534e", fontSize: 10.5, fontWeight: 700 }} />
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
  );
}
