import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Check,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  ChevronsUpDown,
  CircleHelp,
  FileCheck2,
  LayoutDashboard,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  X,
} from "lucide-react";
import "./style.css";

type Ad = {
  ad_id: string;
  platform: string;
  ad_type: string;
  brand: string;
  category: string;
  target_audience: string;
  creative_theme: string;
  status: string;
  start_date: string;
  days_running: number;
  spend: string;
  revenue: string;
  roas: string;
  impressions: number;
  clicks: number;
  conversions: number;
  audit_status: string;
  contributes: boolean;
  contribution: string;
  checks: Record<string, boolean>;
  explanation: string;
  source_index: number;
  source_pointer: string;
};
type Group = {
  platform?: string;
  target_audience?: string;
  creative_theme?: string;
  count: number;
  spend: string;
  revenue: string;
  weighted_roas: string;
  wasted_spend: string;
  flagged_count: number;
};
type Category = {
  category: string;
  count: number;
  amount: string;
  record_ids: string[];
};
type Result = {
  answer: string;
  exact_answer: string;
  status: string;
  records_processed: number;
  flagged_records: number;
  total_spend: string;
  total_revenue: string;
  generated_at: string;
  categories: Category[];
  worst_audiences: Group[];
  best_themes: Group[];
  audience_groups: Group[];
  theme_groups: Group[];
  dataset: {
    filename: string;
    source_url: string;
    sha256: string;
    bytes: number;
    downloaded_at: string;
    row_count: number;
  };
  warnings: unknown[];
};
type View = "overview" | "explorer" | "insights" | "methodology" | "downloads";
const titles: Record<View, string> = {
  overview: "Performance overview",
  explorer: "Ad explorer",
  insights: "Creative intelligence",
  methodology: "Methodology & evidence",
  downloads: "Reports & downloads",
};
const palette: Record<string, string> = {
  Instagram: "#705cce",
  Google: "#579980",
  YouTube: "#e59866",
  Meta: "#628bc1",
};
function cents(value: string) {
  const [a, b = ""] = String(value).split(".");
  return BigInt(a) * 100n + BigInt(b.padEnd(2, "0").slice(0, 2));
}
function money(value: string) {
  const [a, b = ""] = String(value).split(".");
  return (
    "₹" + BigInt(a).toLocaleString("en-IN") + "." + b.padEnd(2, "0").slice(0, 2)
  );
}
const ratio = (value: string) => Number(value).toFixed(2) + "×";
const percent = (part: string, whole: string) =>
  Number((cents(part) * 10000n) / cents(whole)) / 100;
function Download({
  file,
  children,
  className = "button secondary",
}: {
  file: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <a className={className} href={"/reports/" + file} download>
      <ArrowDownToLine size={16} />
      {children}
    </a>
  );
}
function App() {
  const [result, setResult] = useState<Result | null>(null),
    [ads, setAds] = useState<Ad[]>([]),
    [error, setError] = useState("");
  const [view, setView] = useState<View>(
    (location.hash.slice(1) in titles
      ? location.hash.slice(1)
      : "overview") as View,
  );
  const [selected, setSelected] = useState<Ad | null>(null),
    [search, setSearch] = useState(""),
    [platform, setPlatform] = useState("All platforms"),
    [audience, setAudience] = useState("All audiences"),
    [theme, setTheme] = useState("All themes"),
    [status, setStatus] = useState("All results"),
    [minimum, setMinimum] = useState(""),
    [from, setFrom] = useState(""),
    [sort, setSort] = useState("impact"),
    [page, setPage] = useState(1);
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    Promise.all(
      ["final-result.json", "record-results.json"].map(async (f) => {
        const response = await fetch("/reports/" + f);
        if (!response.ok)
          throw Error("Report unavailable (" + response.status + ").");
        return response.json();
      }),
    )
      .then(([r, a]) => {
        if (r.status !== "PASS")
          throw Error(
            "Audit is blocked. Review source validation before publishing an answer.",
          );
        setResult(r);
        setAds(a);
      })
      .catch((e) => setError(String(e)));
  }, []);
  useEffect(() => {
    const onHash = () =>
      setView(
        (location.hash.slice(1) in titles
          ? location.hash.slice(1)
          : "overview") as View,
      );
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  useEffect(() => {
    if (selected) dialog.current?.showModal();
    else dialog.current?.close();
  }, [selected]);
  const navigate = (next: View) => {
    setView(next);
    location.hash = next;
    window.scrollTo({ top: 0 });
  };
  const filtered = useMemo(
    () =>
      ads
        .filter(
          (a) =>
            (!search ||
              [
                a.ad_id,
                a.brand,
                a.platform,
                a.creative_theme,
                a.target_audience,
              ]
                .join(" ")
                .toLowerCase()
                .includes(search.toLowerCase())) &&
            (platform === "All platforms" || a.platform === platform) &&
            (audience === "All audiences" || a.target_audience === audience) &&
            (theme === "All themes" || a.creative_theme === theme) &&
            (status === "All results" || a.audit_status === status) &&
            (!minimum ||
              !/^\d+(\.\d{0,2})?$/.test(minimum) ||
              cents(a.spend) >= cents(minimum)) &&
            (!from || a.start_date >= from),
        )
        .sort((a, b) => {
          if (sort === "id") return a.ad_id.localeCompare(b.ad_id);
          if (sort === "roas")
            return (
              Number(a.roas) - Number(b.roas) || a.ad_id.localeCompare(b.ad_id)
            );
          if (sort === "date")
            return (
              b.start_date.localeCompare(a.start_date) ||
              a.ad_id.localeCompare(b.ad_id)
            );
          const difference =
            cents(sort === "impact" ? b.contribution : b.spend) -
            cents(sort === "impact" ? a.contribution : a.spend);
          return difference > 0n
            ? 1
            : difference < 0n
              ? -1
              : a.ad_id.localeCompare(b.ad_id);
        }),
    [ads, search, platform, audience, theme, status, minimum, from, sort],
  );
  const update = (
    setter: React.Dispatch<React.SetStateAction<string>>,
    value: string,
  ) => {
    setter(value);
    setPage(1);
  };
  const explore = (p = "All platforms", waste = false) => {
    setPlatform(p);
    setStatus(waste ? "Wasted spend" : "All results");
    setSearch("");
    setAudience("All audiences");
    setTheme("All themes");
    setMinimum("");
    setFrom("");
    setPage(1);
    navigate("explorer");
  };
  const pages = Math.max(1, Math.ceil(filtered.length / 12));
  const reset = () => {
    setSearch("");
    setPlatform("All platforms");
    setAudience("All audiences");
    setTheme("All themes");
    setStatus("All results");
    setMinimum("");
    setFrom("");
    setPage(1);
  };
  const flagged = ads
    .filter((x) => x.contributes)
    .sort((a, b) => (cents(a.spend) > cents(b.spend) ? -1 : 1));
  const nav = [
    ["overview", LayoutDashboard, "Overview"],
    ["explorer", Search, "Ad explorer"],
    ["insights", Sparkles, "Creative intelligence"],
    ["methodology", ShieldCheck, "Methodology"],
    ["downloads", ArrowDownToLine, "Downloads"],
  ] as const;
  return (
    <>
      <a href="#main" className="skip">
        Skip to content
      </a>
      <aside className="sidebar">
        <a
          href="#overview"
          className="brand"
          onClick={() => navigate("overview")}
        >
          <span className="brand-mark">a</span>adlens
          <span className="brand-dot">.</span>
        </a>
        <div className="workspace-tag">MOSAIC / CONTENT & CREATIVE</div>
        <nav aria-label="Main navigation">
          {nav.map(([key, Icon, label]) => (
            <a
              aria-label={label}
              href={"#" + key}
              onClick={() => navigate(key)}
              aria-current={view === key ? "page" : undefined}
              className={view === key ? "active" : ""}
              key={key}
            >
              <Icon size={19} />
              <span>{label}</span>
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="source-tag">
            <FileCheck2 size={19} />
            <span>
              Official dataset
              <br />
              <strong>800 ads · 4 platforms</strong>
            </span>
          </div>
          <a
            href="https://mosaicfellowship.in/challenge"
            target="_blank"
            rel="noreferrer"
          >
            View the challenge <ArrowUpRight size={15} />
          </a>
          <p>
            Mosaic Fellowship
            <br />
            Builder Challenge
          </p>
        </div>
      </aside>
      <div className="shell">
        <header className="topbar">
          <span>
            WORKSPACE <ChevronRight size={14} />
            <strong>Ad Performance Intelligence</strong>
          </span>
          <span className="verified">
            <ShieldCheck size={15} />{" "}
            {result ? "Audit reconciled" : "Official dataset"}
          </span>
        </header>
        <main id="main">
          <div className="page-heading">
            <div>
              <p className="eyebrow">CONTENT & CREATIVE</p>
              <h1>{titles[view]}</h1>
              <p className="subtitle">
                {view === "overview"
                  ? "Find the spend that never found its return."
                  : view === "explorer"
                    ? "Every ad. Every threshold. A clear reason for every decision."
                    : view === "insights"
                      ? "Compare audiences and creative themes across the full dataset."
                      : view === "methodology"
                        ? "Trace the answer from the official source to each qualifying ad."
                        : "Take the complete audit with you."}
              </p>
            </div>
            {result && (
              <Download file="record-results.csv">Export audit</Download>
            )}
          </div>
          {error ? (
            <div role="alert" className="panel error">
              <h2>We couldn’t load the audit</h2>
              <p>{error}</p>
              <button className="button" onClick={() => location.reload()}>
                Try again
              </button>
            </div>
          ) : !result ? (
            <div className="panel loading" role="status">
              Loading the verified audit…
            </div>
          ) : (
            <>
              {view === "overview" && (
                <>
                  <section className="summary-grid">
                    <div className="answer-card">
                      <div className="answer-top">
                        <span>TOTAL WASTED SPEND</span>
                        <span className="answer-badge">
                          <CheckCheck size={15} /> Independently verified
                        </span>
                      </div>
                      <div className="answer">{money(result.answer)}</div>
                      <p>
                        Across{" "}
                        <strong>
                          {result.flagged_records} underperforming ads
                        </strong>{" "}
                        with enough budget and time to improve.
                      </p>
                      <div className="formula">
                        <span>
                          ROAS <b>&lt; 1.0</b>
                        </span>
                        <i>AND</i>
                        <span>
                          Spend <b>&gt; ₹5,000</b>
                        </span>
                        <i>AND</i>
                        <span>
                          Running <b>&gt; 14 days</b>
                        </span>
                      </div>
                      <button
                        onClick={() => explore("All platforms", true)}
                        className="answer-link"
                      >
                        Review the 13 flagged ads <ArrowRight size={18} />
                      </button>
                    </div>
                    <div className="mini-metrics">
                      <div className="metric">
                        <span>
                          Ads processed <BarChart3 size={18} />
                        </span>
                        <strong>
                          800 <small>/ 800</small>
                        </strong>
                        <p>Complete official dataset</p>
                      </div>
                      <div className="metric">
                        <span>
                          Share of total spend <CircleHelp size={17} />
                        </span>
                        <strong>
                          {percent(result.answer, result.total_spend).toFixed(
                            2,
                          )}
                          <small>%</small>
                        </strong>
                        <p>{money(result.total_spend)} total spend</p>
                      </div>
                    </div>
                  </section>
                  <section className="panel breakdown">
                    <div className="section-heading">
                      <div>
                        <h2>Where the waste is</h2>
                        <p>
                          One rule. Four mutually exclusive platform totals.
                        </p>
                      </div>
                      <span className="pill success">
                        <Check size={14} /> Reconciles exactly
                      </span>
                    </div>
                    <div
                      className="stack-bar"
                      aria-label="Wasted spend by platform"
                    >
                      {[...result.categories]
                        .sort((a, b) =>
                          cents(a.amount) > cents(b.amount) ? -1 : 1,
                        )
                        .map((c) => (
                          <button
                            key={c.category}
                            title={`${c.category}: ${money(c.amount)}`}
                            aria-label={`Explore ${c.category} wasted spend`}
                            style={{
                              width: percent(c.amount, result.answer) + "%",
                              background: palette[c.category],
                            }}
                            onClick={() => explore(c.category, true)}
                          />
                        ))}
                    </div>
                    <div className="category-grid">
                      {[...result.categories]
                        .sort((a, b) =>
                          cents(a.amount) > cents(b.amount) ? -1 : 1,
                        )
                        .map((c) => (
                          <button
                            className="category-card"
                            key={c.category}
                            onClick={() => explore(c.category, true)}
                          >
                            <div>
                              <span
                                className="legend-dot"
                                style={{ background: palette[c.category] }}
                              />
                              {c.category}
                              <ArrowUpRight size={15} />
                            </div>
                            <strong>{money(c.amount)}</strong>
                            <p>
                              {c.count} flagged ads{" "}
                              <span>
                                {percent(c.amount, result.answer).toFixed(1)}%
                              </span>
                            </p>
                          </button>
                        ))}
                    </div>
                    <div className="recon-line">
                      <span>Platform total</span>
                      <strong>{money(result.answer)}</strong>
                      <span className="muted">
                        Difference from answer <b>₹0.00</b>
                      </span>
                    </div>
                  </section>
                  <section className="panel">
                    <div className="section-heading">
                      <div>
                        <h2>Highest wasted spend</h2>
                        <p>
                          Start with the ads contributing most to the total.
                        </p>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => explore("All platforms", true)}
                      >
                        View all 13 <ArrowRight size={16} />
                      </button>
                    </div>
                    <AdTable rows={flagged.slice(0, 5)} open={setSelected} />
                  </section>
                  <div className="bottom-note">
                    <ShieldCheck size={17} />
                    <span>
                      Python Decimal + independent JavaScript BigInt
                      calculation. All 13 ad IDs and amounts agree.
                    </span>
                    <button onClick={() => navigate("methodology")}>
                      See methodology <ArrowRight size={14} />
                    </button>
                  </div>
                </>
              )}
              {view === "explorer" && (
                <>
                  <section className="panel filters">
                    <div className="filter-top">
                      <div className="searchbox">
                        <Search size={18} />
                        <input
                          aria-label="Search ads"
                          value={search}
                          onChange={(e) => update(setSearch, e.target.value)}
                          placeholder="Search ad ID, brand, audience or theme…"
                        />
                      </div>
                      <button className="text-button" onClick={reset}>
                        Reset filters
                      </button>
                    </div>
                    <div className="filter-grid">
                      <Select
                        label="Platform"
                        value={platform}
                        options={[
                          "All platforms",
                          ...Object.keys(palette).sort(),
                        ]}
                        onChange={(v) => update(setPlatform, v)}
                      />
                      <Select
                        label="Audience"
                        value={audience}
                        options={[
                          "All audiences",
                          ...new Set(ads.map((x) => x.target_audience)),
                        ].sort((a, b) =>
                          a === "All audiences"
                            ? -1
                            : b === "All audiences"
                              ? 1
                              : a.localeCompare(b),
                        )}
                        onChange={(v) => update(setAudience, v)}
                      />
                      <Select
                        label="Creative theme"
                        value={theme}
                        options={[
                          "All themes",
                          ...new Set(ads.map((x) => x.creative_theme)),
                        ]}
                        onChange={(v) => update(setTheme, v)}
                      />
                      <Select
                        label="Audit result"
                        value={status}
                        options={["All results", "Wasted spend", "Not flagged"]}
                        onChange={(v) => update(setStatus, v)}
                      />
                      <label>
                        Minimum spend (₹)
                        <input
                          inputMode="decimal"
                          value={minimum}
                          onChange={(e) => update(setMinimum, e.target.value)}
                          placeholder="Any amount"
                        />
                      </label>
                      <label>
                        Started on or after
                        <input
                          type="date"
                          value={from}
                          onChange={(e) => update(setFrom, e.target.value)}
                        />
                      </label>
                    </div>
                  </section>
                  <section className="panel">
                    <div className="section-heading">
                      <h2>
                        {filtered.length} ads{" "}
                        <span className="muted count-label">of 800</span>
                      </h2>
                      <label className="sort">
                        <ChevronsUpDown size={16} />
                        <span className="sr-only">Sort ads</span>
                        <select
                          aria-label="Sort ads"
                          value={sort}
                          onChange={(e) => update(setSort, e.target.value)}
                        >
                          <option value="impact">
                            Wasted spend: high to low
                          </option>
                          <option value="spend">Spend: high to low</option>
                          <option value="roas">ROAS: low to high</option>
                          <option value="id">Ad ID: ascending</option>
                          <option value="date">Start date: newest first</option>
                        </select>
                      </label>
                    </div>
                    {filtered.length ? (
                      <AdTable
                        rows={filtered.slice((page - 1) * 12, page * 12)}
                        open={setSelected}
                      />
                    ) : (
                      <div className="empty">
                        <SlidersHorizontal size={28} />
                        <h3>No ads match these filters</h3>
                        <p>
                          Try a different ID or broaden the selected filters.
                        </p>
                        <button className="button secondary" onClick={reset}>
                          Clear filters
                        </button>
                      </div>
                    )}
                    <div className="pagination">
                      <span>
                        {filtered.length
                          ? `${(page - 1) * 12 + 1}–${Math.min(page * 12, filtered.length)}`
                          : "0"}{" "}
                        of {filtered.length} ads
                      </span>
                      <div>
                        <button
                          aria-label="Previous page"
                          disabled={page === 1}
                          onClick={() => setPage(page - 1)}
                        >
                          <ChevronLeft size={17} />
                        </button>
                        <span>
                          Page {page} of {pages}
                        </span>
                        <button
                          aria-label="Next page"
                          disabled={page === pages}
                          onClick={() => setPage(page + 1)}
                        >
                          <ChevronRight size={17} />
                        </button>
                      </div>
                    </div>
                  </section>
                </>
              )}
              {view === "insights" && (
                <>
                  <div className="notice">
                    <CircleHelp size={20} />
                    <p>
                      Rankings use{" "}
                      <strong>
                        weighted ROAS: total revenue ÷ total spend
                      </strong>
                      . These official synthetic records have unusually high
                      returns. “Worst” means lowest relative return; it does not
                      mean the whole audience is loss-making.
                    </p>
                  </div>
                  <div className="insight-grid">
                    <section className="panel">
                      <div className="section-heading">
                        <div>
                          <p className="eyebrow">LOWEST WEIGHTED ROAS</p>
                          <h2>Platform × audience</h2>
                        </div>
                      </div>
                      {result.worst_audiences.map((g, i) => (
                        <div
                          className="rank-row"
                          key={g.platform! + g.target_audience}
                        >
                          <span className="rank">0{i + 1}</span>
                          <div>
                            <h3>
                              {g.platform}{" "}
                              <span className="muted">
                                / {g.target_audience}
                              </span>
                            </h3>
                            <p>
                              {g.count} ads · {money(g.spend)} spend
                            </p>
                            <small>
                              {money(g.wasted_spend)} qualifying waste
                            </small>
                          </div>
                          <strong>{ratio(g.weighted_roas)}</strong>
                        </div>
                      ))}
                    </section>
                    <section className="panel">
                      <div className="section-heading">
                        <div>
                          <p className="eyebrow">HIGHEST WEIGHTED ROAS</p>
                          <h2>Creative themes</h2>
                        </div>
                        <Sparkles size={23} />
                      </div>
                      {result.best_themes.map((g, i) => (
                        <div className="rank-row" key={g.creative_theme}>
                          <span className="rank green">0{i + 1}</span>
                          <div>
                            <h3>{g.creative_theme}</h3>
                            <p>
                              {g.count} ads · {money(g.spend)} spend
                            </p>
                            <small>
                              {g.flagged_count} individual ads still flagged
                            </small>
                          </div>
                          <strong>{ratio(g.weighted_roas)}</strong>
                        </div>
                      ))}
                    </section>
                  </div>
                  <section className="panel recommendation">
                    <div className="recommend-icon">
                      <Sparkles />
                    </div>
                    <div>
                      <p className="eyebrow">BUDGET RECOMMENDATION</p>
                      <h2>
                        Review the flagged ads before scaling the winners.
                      </h2>
                      <p>
                        The {money(result.answer)} is historical spend across
                        all ad statuses, not a forecast of recoverable cash.
                        Pause or revise qualifying ads that are still active.
                        Test additional budget in Doctor Trust, Lifestyle and
                        Product Demo, then validate incremental returns. Strong
                        theme averages can still hide losing ads.
                      </p>
                      <button
                        className="text-button"
                        onClick={() => explore("All platforms", true)}
                      >
                        Inspect the underlying ads <ArrowRight size={16} />
                      </button>
                    </div>
                  </section>
                  <section className="panel">
                    <div className="section-heading">
                      <h2>All creative themes</h2>
                      <span className="muted">Weighted ROAS</span>
                    </div>
                    <div className="theme-chart">
                      {result.theme_groups.map((g) => (
                        <div key={g.creative_theme}>
                          <span>{g.creative_theme}</span>
                          <div className="theme-track">
                            <i
                              style={{
                                width:
                                  (Number(g.weighted_roas) /
                                    Number(
                                      result.best_themes[0].weighted_roas,
                                    )) *
                                    100 +
                                  "%",
                              }}
                            />
                          </div>
                          <strong>{ratio(g.weighted_roas)}</strong>
                        </div>
                      ))}
                    </div>
                  </section>
                </>
              )}
              {view === "methodology" && (
                <>
                  <div className="method-grid">
                    <section className="panel method">
                      <p className="eyebrow">01 / OFFICIAL RULE</p>
                      <h2>Three checks, one decision.</h2>
                      <p>
                        Count an ad only when all three strict inequalities
                        pass. Sum its entire spend once. Revenue is used to
                        explain ROAS; it is not subtracted from the answer.
                      </p>
                      <code>
                        roas &lt; 1.0
                        <br />
                        AND spend &gt; 5000
                        <br />
                        AND days_running &gt; 14
                      </code>
                      <p>
                        Exactly 1.0 ROAS, exactly ₹5,000 spend, or exactly 14
                        days fails the corresponding check. Ad status does not
                        change eligibility.
                      </p>
                      <p className="muted">
                        The official problem defines one scored category: wasted
                        spend. Platforms are a presentation breakdown, not
                        additional error categories.
                      </p>
                    </section>
                    <section className="panel method">
                      <p className="eyebrow">02 / EXACT RECONCILIATION</p>
                      <h2>Every rupee, counted once.</h2>
                      {result.categories.map((c) => (
                        <div className="recon-row" key={c.category}>
                          <span>
                            {c.category} <small>({c.count} ads)</small>
                          </span>
                          <strong>{money(c.amount)}</strong>
                        </div>
                      ))}
                      <div className="recon-row total">
                        <span>Total</span>
                        <strong>{money(result.answer)}</strong>
                      </div>
                      <p>
                        Monetary values are parsed directly into Python Decimal.
                        An independent JavaScript implementation reads the raw
                        JSON into integer cents and verifies every qualifying
                        ID, count and platform amount.
                      </p>
                      <Download file="reconciliation.json">
                        Download reconciliation
                      </Download>
                    </section>
                    <section className="panel method">
                      <p className="eyebrow">03 / DATA QUALITY & ROUNDING</p>
                      <h2>Preserve uncertainty visibly.</h2>
                      <ul>
                        <li>
                          800 valid records, 800 unique IDs; no malformed rows,
                          missing required fields or duplicates found.
                        </li>
                        <li>
                          488 null video-completion values are allowed. They do
                          not affect the rule.
                        </li>
                        <li>
                          AD-0207 reports ROAS 1.00, while revenue/spend is
                          below 1. It ran for 8 days, so it is excluded under
                          both interpretations.
                        </li>
                        <li>
                          The supplied ROAS is used for the official filter.
                          Recomputing ROAS gives the same ₹14,75,731.79 answer.
                        </li>
                        <li>
                          The page specifies two decimal places but no
                          tie-breaking mode. Half-up is our reporting choice.
                          All monetary inputs are already in cents, so
                          half-even, half-up and per-record rounding agree here.
                        </li>
                      </ul>
                      <p>
                        No duplicate or malformed-record policy is published. If
                        encountered, the engine quarantines affected rows and
                        blocks a final answer for review.
                      </p>
                    </section>
                    <section className="panel method">
                      <p className="eyebrow">04 / SOURCE & PROVENANCE</p>
                      <h2>Official data. Reproducible result.</h2>
                      <dl>
                        <dt>Source</dt>
                        <dd>
                          <a href={result.dataset.source_url}>
                            {result.dataset.filename} <ArrowUpRight size={13} />
                          </a>
                        </dd>
                        <dt>Record count</dt>
                        <dd>800</dd>
                        <dt>File size</dt>
                        <dd>{result.dataset.bytes.toLocaleString()} bytes</dd>
                        <dt>Downloaded (UTC)</dt>
                        <dd>
                          {new Date(result.dataset.downloaded_at).toISOString()}
                        </dd>
                        <dt>Processed (UTC)</dt>
                        <dd>{new Date(result.generated_at).toISOString()}</dd>
                        <dt>SHA-256</dt>
                        <dd className="hash">{result.dataset.sha256}</dd>
                      </dl>
                      <a
                        href="https://mosaicfellowship.in/challenge"
                        target="_blank"
                        rel="noreferrer"
                        className="text-button"
                      >
                        Read official challenge <ArrowUpRight size={15} />
                      </a>
                      <p className="muted">
                        Official synthetic challenge data. No private answer key
                        has been accessed or verified.
                      </p>
                    </section>
                  </div>
                </>
              )}
              {view === "downloads" && (
                <section className="panel download-list">
                  {[
                    [
                      "final-result.json",
                      "Complete audit summary",
                      "Answer, platform totals, dataset metadata and creative rankings.",
                    ],
                    [
                      "record-results.csv",
                      "Ad-level CSV",
                      "All 800 ads, financial fields, classifications and inclusion reasons.",
                    ],
                    [
                      "record-results.json",
                      "Full record evidence",
                      "Machine-readable source fields and each threshold result.",
                    ],
                    [
                      "category-breakdown.json",
                      "Platform breakdown",
                      "Mutually exclusive contributions and qualifying ad references.",
                    ],
                    [
                      "reconciliation.json",
                      "Reconciliation ledger",
                      "Trace all 13 contributions back to the official source.",
                    ],
                    [
                      "independent-validation.json",
                      "Independent verification",
                      "Raw-source JavaScript BigInt calculation and Python comparisons.",
                    ],
                    [
                      "malformed-records.json",
                      "Malformed-record report",
                      "Validation findings; empty for this official dataset.",
                    ],
                    [
                      "duplicate-records.json",
                      "Duplicate-record report",
                      "Identical and conflicting duplicates; empty for this official dataset.",
                    ],
                  ].map(([file, title, description]) => (
                    <div key={file}>
                      <FileCheck2 size={25} />
                      <div>
                        <h2>{title}</h2>
                        <p>{description}</p>
                        <small>{file}</small>
                      </div>
                      <Download file={file}>Download</Download>
                    </div>
                  ))}
                </section>
              )}
              <footer>
                <span>Adlens / Mosaic Fellowship Builder Challenge</span>
                <span>Official synthetic data · No login required</span>
              </footer>
            </>
          )}
        </main>
      </div>
      <dialog
        ref={dialog}
        onCancel={() => setSelected(null)}
        onClick={(e) => {
          if (e.target === dialog.current) setSelected(null);
        }}
        aria-labelledby="detail-title"
      >
        {selected && (
          <>
            <div className="dialog-top">
              <span className="eyebrow">
                AD EVIDENCE / {selected.platform.toUpperCase()}
              </span>
              <button
                autoFocus
                aria-label="Close record"
                onClick={() => setSelected(null)}
              >
                <X size={22} />
              </button>
            </div>
            <h2 id="detail-title">{selected.ad_id}</h2>
            <p className="subtitle">
              {selected.brand} · {selected.creative_theme} ·{" "}
              {selected.target_audience}
            </p>
            <span
              className={
                "pill " + (selected.contributes ? "warning" : "neutral")
              }
            >
              {selected.audit_status}
            </span>
            <div className="detail-metrics">
              <div>
                <span>Spend</span>
                <strong>{money(String(selected.spend))}</strong>
              </div>
              <div>
                <span>Revenue</span>
                <strong>{money(String(selected.revenue))}</strong>
              </div>
              <div>
                <span>Contribution</span>
                <strong>{money(selected.contribution)}</strong>
              </div>
            </div>
            <h3>Threshold evidence</h3>
            <div className="check-list">
              {[
                [
                  `ROAS ${Number(selected.roas).toFixed(2)} < 1.00`,
                  selected.checks.roas_below_one,
                ],
                [
                  `Spend ${money(String(selected.spend))} > ₹5,000.00`,
                  selected.checks.spend_above_5000,
                ],
                [
                  `Running ${selected.days_running} days > 14 days`,
                  selected.checks.running_over_14_days,
                ],
              ].map(([label, pass]) => (
                <div key={String(label)}>
                  <span className={pass ? "check-pass" : "check-fail"}>
                    {pass ? <Check size={16} /> : <X size={16} />}
                  </span>
                  <span>{label}</span>
                  <b>{pass ? "Pass" : "Fail"}</b>
                </div>
              ))}
            </div>
            <div className="evidence-note">
              <h3>
                {selected.contributes
                  ? "Why this spend counts"
                  : "Why this ad is excluded"}
              </h3>
              <p>{selected.explanation}</p>
              <p>
                {selected.contributes
                  ? "The contribution is the full spend, counted once. The three checks are not three separate charges."
                  : "Failing any one threshold excludes the ad, even when other checks pass."}
              </p>
            </div>
            <dl className="detail-dl">
              <dt>Ad status</dt>
              <dd>{selected.status}</dd>
              <dt>Start date</dt>
              <dd>{selected.start_date}</dd>
              <dt>Creative format</dt>
              <dd>{selected.ad_type}</dd>
              <dt>Reconciliation category</dt>
              <dd>
                {selected.contributes ? selected.platform : "Excluded (₹0.00)"}
              </dd>
              <dt>Source record</dt>
              <dd>
                content_ads.json · index {selected.source_index} · pointer{" "}
                {selected.source_pointer}
              </dd>
            </dl>
            <p className="muted">
              Billed and expected invoice amounts do not apply to this ad
              dataset.
            </p>
          </>
        )}
      </dialog>
    </>
  );
}
function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <label>
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => (
          <option key={o}>{o}</option>
        ))}
      </select>
    </label>
  );
}
function AdTable({ rows, open }: { rows: Ad[]; open: (a: Ad) => void }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Ad / creative</th>
            <th>Platform</th>
            <th>Audience</th>
            <th className="number">Spend</th>
            <th className="number">ROAS</th>
            <th className="number">Days</th>
            <th>Audit result</th>
            <th>
              <span className="sr-only">Details</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((a) => (
            <tr key={a.ad_id}>
              <td>
                <button className="ad-link" onClick={() => open(a)}>
                  {a.ad_id}
                </button>
                <small>{a.creative_theme}</small>
              </td>
              <td>
                <span className="platform">
                  <i style={{ background: palette[a.platform] }} />
                  {a.platform}
                </span>
              </td>
              <td>{a.target_audience}</td>
              <td className="number">{money(String(a.spend))}</td>
              <td
                className={"number " + (Number(a.roas) < 1 ? "low-roas" : "")}
              >
                {ratio(String(a.roas))}
              </td>
              <td className="number">{a.days_running}</td>
              <td>
                <span
                  className={"pill " + (a.contributes ? "warning" : "neutral")}
                >
                  {a.audit_status}
                </span>
              </td>
              <td>
                <button
                  className="icon-button"
                  aria-label={"Open " + a.ad_id}
                  onClick={() => open(a)}
                >
                  <ArrowUpRight size={17} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
