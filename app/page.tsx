"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: "SOLUNA Clash of Clans Dashboard",
  applicationCategory: "GameApplication",
  operatingSystem: "Any (Web)",
  description:
    "Clash-of-Clans Analyse-Tool für Clan-Aktivität, Spenden, Angriffe, Kriegs-Sterne und Rathaus-Verteilung mit automatischer Interpretation.",
  offers: { "@type": "Offer", price: "0", priceCurrency: "EUR" },
  inLanguage: "de",
};

const faq = [
  {
    q: "Kann ich jeden Clan analysieren?",
    a: "Ja. Du gibst einfach den Clan-Tag ein (z. B. #2LUVL2QGL) und bekommst sofort das volle Dashboard. Kein Login, keine Registrierung, keine versteckten Grenzen.",
  },
  {
    q: "Welche Daten werden abgerufen?",
    a: "Nur öffentliche Daten aus der offiziellen Clash-of-Clans-API: Mitgliederliste, Spenden, gewonnene Angriffe, Trophäen, Rathaus-Level, Rollen und Kriegs-Sterne. Nichts Persönliches, keine Passwörter, keine E-Mails.",
  },
  {
    q: "Ist das kostenlos?",
    a: "Ja, komplett kostenlos. SOLUNA ist ein persönliches Projekt und nicht von Supercell gesponsert oder genehmigt.",
  },
  {
    q: "Wie wird der Aktivitäts-Score berechnet?",
    a: "Linear und ungedeckelt: 1 Punkt pro gegebener Spende, 3 Punkte × Trophäen-Bonus (0.8–1.3) pro Angriffssieg, 0.5 Punkte pro Kriegs-Stern. Details, Formel und Beispiele findest du im Dashboard selbst.",
  },
  {
    q: "Wie oft werden die Daten aktualisiert?",
    a: "Bei jedem Aufruf wird live die CoC-API abgefragt. Du siehst also immer den aktuellen Stand — ohne Caching. Die CoC-API selbst aktualisiert sich etwa alle paar Minuten.",
  },
  {
    q: "Warum dauert der erste Aufruf so lange?",
    a: "Für bis zu 50 Mitglieder werden einzelne Spielerdaten parallel abgefragt. Je nach Clan-Größe und API-Latenz braucht das 5–15 Sekunden beim ersten Laden.",
  },
];

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [clanTag, setClanTag] = useState("");
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    const trimmed = clanTag.trim();
    const target = trimmed
      ? `/clan-activity?clan_tag=${encodeURIComponent(trimmed)}`
      : "/clan-activity";
    setTimeout(() => router.push(target), 50);
  };

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 antialiased selection:bg-amber-200">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Skip-to-content for keyboard users */}
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-amber-600 focus:px-4 focus:py-2 focus:font-semibold focus:text-white focus:outline-none focus:ring-4 focus:ring-amber-200"
      >
        Zum Hauptinhalt springen
      </a>

      {/* Ambient background — parchment + subtle grid */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(1200px_600px_at_20%_-10%,rgba(251,191,36,0.12),transparent),radial-gradient(900px_500px_at_110%_10%,rgba(220,38,38,0.08),transparent),linear-gradient(180deg,#fafaf9,#f5f5f4)]"
      />

      {/* Navbar */}
      <header className="sticky top-0 z-20 border-b border-stone-200/80 bg-stone-50/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6 sm:py-4">
          <a
            href="/"
            aria-label="SOLUNA Startseite"
            className="flex items-center gap-2 font-bold tracking-tight focus:outline-none focus-visible:rounded-md focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2 sm:gap-2.5"
          >
            <ShieldIcon />
            <span className="text-base sm:text-lg">
              <span className="text-amber-700">SO</span>
              <span>LUNA</span>
            </span>
            <span className="ml-1 hidden rounded-md bg-stone-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-stone-600 ring-1 ring-stone-200 sm:ml-2 sm:inline">
              CoC Dashboard
            </span>
          </a>
          <nav aria-label="Hauptnavigation" className="hidden gap-7 text-sm font-medium text-stone-600 md:flex">
            <a href="#features" className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2">
              Features
            </a>
            <a href="#how" className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2">
              So funktionierts
            </a>
            <a href="#faq" className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2">
              FAQ
            </a>
            <a href="/ueber_uns" className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2">
              Über uns
            </a>
          </nav>
        </div>
      </header>

      <main id="main">
      {/* Hero */}
      <section aria-labelledby="hero-heading" className="relative mx-auto max-w-6xl px-4 pt-12 pb-16 sm:px-6 sm:pt-16 sm:pb-20 md:pt-24 md:pb-28">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-amber-800 sm:text-xs">
            <SparkleIcon />
            Live-Daten aus der offiziellen CoC-API
          </span>
          <h1
            id="hero-heading"
            className="mt-5 text-balance text-3xl font-extrabold leading-[1.15] tracking-tight text-stone-900 sm:mt-6 sm:text-4xl md:text-6xl"
          >
            Durchleuchte deinen{" "}
            <span className="bg-gradient-to-r from-amber-600 via-amber-700 to-red-700 bg-clip-text text-transparent">
              Clash-of-Clans-Clan
            </span>{" "}
            in unter 30 Sekunden
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-pretty text-base leading-relaxed text-stone-600 sm:mt-6 sm:text-lg">
            Aktivitäts-Score, Spenden-Bilanz, Top-Angreifer, Kriegs-Sterne,
            Rathaus-Verteilung — mit <b>automatischer Interpretation</b>, die
            Fachbegriffe in einfacher Sprache erklärt. Gib einfach deinen
            Clan-Tag ein.
          </p>

          {/* Clan-Tag input */}
          <form
            onSubmit={handleSubmit}
            aria-label="Clan-Analyse starten"
            className="mx-auto mt-8 flex max-w-xl flex-col gap-3 sm:mt-10 sm:flex-row"
          >
            <div className="relative flex-1">
              <label htmlFor="clan-tag-input" className="sr-only">
                Clan-Tag (leer lassen für Demo-Clan SOLUNA)
              </label>
              <span
                aria-hidden="true"
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 select-none font-mono text-lg font-semibold text-stone-400"
              >
                #
              </span>
              <input
                id="clan-tag-input"
                name="clan_tag"
                type="text"
                value={clanTag}
                onChange={(e) => setClanTag(e.target.value.toUpperCase())}
                placeholder="2LUVL2QGL"
                aria-describedby="clan-tag-hint"
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="characters"
                spellCheck={false}
                inputMode="text"
                maxLength={20}
                className="w-full rounded-xl border border-stone-300 bg-white py-3.5 pl-10 pr-4 font-mono text-lg font-semibold tracking-[0.15em] text-stone-900 placeholder:font-normal placeholder:tracking-normal placeholder:text-stone-400 shadow-sm transition focus:border-amber-500 focus:outline-none focus:ring-4 focus:ring-amber-200 disabled:bg-stone-100 sm:py-4 sm:text-xl"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              aria-label={isLoading ? "Clan-Daten werden geladen" : "Analyse starten"}
              className="group inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-br from-amber-600 to-red-700 px-6 py-4 text-base font-semibold text-white shadow-lg shadow-amber-900/20 transition hover:shadow-amber-900/40 focus:outline-none focus-visible:ring-4 focus-visible:ring-amber-300 disabled:cursor-wait disabled:opacity-80 sm:px-7"
            >
              {isLoading ? (
                <>
                  <Spinner />
                  <span>Lade Clan-Daten …</span>
                </>
              ) : (
                <>
                  <span>Analyse starten</span>
                  <ArrowIcon />
                </>
              )}
            </button>
          </form>
          <p id="clan-tag-hint" className="mt-3 text-xs leading-relaxed text-stone-500">
            Leer lassen für Demo-Clan SOLUNA. Keine Anmeldung, keine Cookies — nur öffentliche CoC-API-Daten.
          </p>

          {/* Trust / stats band */}
          <div className="mx-auto mt-14 grid max-w-3xl grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { k: "10", v: "Metrik-Karten" },
              { k: "7", v: "Charts" },
              { k: "9", v: "Auto-Insights" },
              { k: "0 €", v: "Kosten" },
            ].map((s) => (
              <div
                key={s.v}
                className="rounded-xl border border-stone-200 bg-white/80 px-4 py-4 shadow-sm"
              >
                <div className="text-2xl font-extrabold text-amber-700">
                  {s.k}
                </div>
                <div className="text-xs font-medium uppercase tracking-wider text-stone-500">
                  {s.v}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section
        id="features"
        aria-labelledby="features-heading"
        className="mx-auto max-w-6xl scroll-mt-24 px-4 py-14 sm:px-6 sm:py-16 md:py-24"
      >
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-bold uppercase tracking-widest text-amber-700">
            Was du bekommst
          </span>
          <h2 id="features-heading" className="mt-3 text-balance text-2xl font-extrabold tracking-tight sm:text-3xl md:text-4xl">
            Jede Kennzahl, die ein Anführer wirklich braucht
          </h2>
          <p className="mt-4 text-pretty text-stone-600">
            Kein Ratespiel, kein Excel-Export, keine halben Antworten. Das
            Dashboard rechnet alles aus und erklärt, was die Zahlen bedeuten.
          </p>
        </div>

        <ul role="list" className="mt-10 grid gap-4 sm:mt-12 sm:gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <li key={f.title}>
              <article className="group relative h-full overflow-hidden rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md sm:p-6">
                <div aria-hidden="true" className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-amber-100/60 blur-2xl transition group-hover:bg-amber-200/60" />
                <div aria-hidden="true" className="relative flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-100 to-amber-200 text-amber-800 ring-1 ring-amber-300/60">
                  {f.icon}
                </div>
                <h3 className="relative mt-4 text-base font-bold text-stone-900 sm:mt-5 sm:text-lg">
                  {f.title}
                </h3>
                <p className="relative mt-2 text-sm leading-relaxed text-stone-600">
                  {f.body}
                </p>
              </article>
            </li>
          ))}
        </ul>
      </section>

      {/* How it works */}
      <section
        id="how"
        aria-labelledby="how-heading"
        className="border-y border-stone-200 bg-gradient-to-b from-white to-stone-50 py-14 sm:py-16 md:py-24"
      >
        <div className="mx-auto max-w-6xl scroll-mt-24 px-4 sm:px-6">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-xs font-bold uppercase tracking-widest text-amber-700">
              So funktionierts
            </span>
            <h2 id="how-heading" className="mt-3 text-balance text-2xl font-extrabold tracking-tight sm:text-3xl md:text-4xl">
              Von Clan-Tag bis Rangliste in drei Schritten
            </h2>
          </div>
          <ol className="mt-12 grid gap-6 sm:gap-5 md:grid-cols-3">
            {steps.map((s, i) => (
              <li
                key={s.t}
                className="relative rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-6"
              >
                <div aria-hidden="true" className="absolute -top-4 left-5 flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-600 to-red-700 text-sm font-bold text-white shadow-md shadow-amber-900/20 sm:left-6">
                  <span className="sr-only">Schritt </span>
                  {i + 1}
                </div>
                <h3 className="mt-3 text-base font-bold sm:text-lg">{s.t}</h3>
                <p className="mt-2 text-sm leading-relaxed text-stone-600">
                  {s.d}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* FAQ */}
      <section
        id="faq"
        aria-labelledby="faq-heading"
        className="mx-auto max-w-3xl scroll-mt-24 px-4 py-14 sm:px-6 sm:py-16 md:py-24"
      >
        <div className="text-center">
          <span className="text-xs font-bold uppercase tracking-widest text-amber-700">
            Häufige Fragen
          </span>
          <h2 id="faq-heading" className="mt-3 text-balance text-2xl font-extrabold tracking-tight sm:text-3xl md:text-4xl">
            Bevor du loslegst
          </h2>
        </div>
        <div className="mt-8 divide-y divide-stone-200 rounded-2xl border border-stone-200 bg-white shadow-sm sm:mt-10">
          {faq.map((f) => (
            <details
              key={f.q}
              className="group px-4 py-4 open:bg-stone-50/60 sm:px-6"
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-1 text-left text-sm font-semibold text-stone-900 focus:outline-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2 sm:text-base">
                <span>{f.q}</span>
                <span aria-hidden="true" className="flex h-7 w-7 flex-none items-center justify-center rounded-full bg-stone-100 text-stone-500 transition group-open:rotate-180 group-open:bg-amber-100 group-open:text-amber-700">
                  <ChevronIcon />
                </span>
              </summary>
              <p className="pb-2 pt-3 text-sm leading-relaxed text-stone-600">
                {f.a}
              </p>
            </details>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section aria-labelledby="cta-heading" className="px-4 pb-16 sm:px-6 sm:pb-20">
        <div className="mx-auto max-w-4xl overflow-hidden rounded-3xl bg-gradient-to-br from-stone-900 via-stone-800 to-amber-950 p-7 text-center shadow-xl sm:p-10 md:p-14">
          <h2 id="cta-heading" className="text-balance text-2xl font-extrabold text-amber-50 sm:text-3xl md:text-4xl">
            Bereit, deinen Clan zu durchleuchten?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-sm text-stone-300 sm:text-base">
            Gib oben deinen Clan-Tag ein oder teste zuerst mit dem Demo-Clan
            SOLUNA. Kein Account nötig.
          </p>
          <a
            href="#clan-tag-input"
            onClick={(e) => {
              e.preventDefault();
              window.scrollTo({ top: 0, behavior: "smooth" });
              setTimeout(() => {
                document.getElementById("clan-tag-input")?.focus();
              }, 500);
            }}
            className="mt-7 inline-flex items-center gap-2 rounded-xl bg-amber-500 px-6 py-3.5 text-sm font-semibold text-stone-900 shadow-lg transition hover:bg-amber-400 focus:outline-none focus-visible:ring-4 focus-visible:ring-amber-300 sm:mt-8 sm:px-7 sm:text-base"
          >
            Jetzt Clan-Tag eingeben
            <ArrowIcon />
          </a>
        </div>
      </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-stone-200 bg-stone-100/80">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 text-sm text-stone-600 sm:px-6 md:flex-row">
          <p className="text-center md:text-left">
            © {new Date().getFullYear()}{" "}
            <span className="font-semibold text-stone-900">SOLUNA</span>. Nicht
            von Supercell gesponsert oder genehmigt.
          </p>
          <nav aria-label="Footer" className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            <a
              href="/Datenschutzrichtlinien"
              className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
            >
              Datenschutz
            </a>
            <a
              href="/ueber_uns"
              className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
            >
              Über uns
            </a>
            <a
              href="https://discord.gg/G2Br635S4B"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
            >
              Discord
              <span className="sr-only"> (öffnet in neuem Tab)</span>
            </a>
          </nav>
        </div>
      </footer>
    </div>
  );
}

/* ---------- Content ---------- */

const features = [
  {
    title: "Aktivitäts-Score (v3)",
    body:
      "Ungedeckelte lineare Punktesumme aus Spenden, Angriffen (trophäen-skaliert) und Kriegs-Sternen. Wer mehr leistet, hat mehr Punkte — keine künstliche 0–100-Deckelung.",
    icon: <TargetIcon />,
  },
  {
    title: "Spenden-Bilanz & Top-Spender",
    body:
      "Gegeben vs. erhalten pro Spieler, Netto-Summe, Konzentrations-Analyse und Warnung bei zu starker Abhängigkeit von einzelnen Spendern.",
    icon: <BalanceIcon />,
  },
  {
    title: "Kriegs-Sterne-Leader",
    body:
      "Lifetime-Kriegssterne pro Mitglied. Erkenne erfahrene Veteranen und sieh den Clan-Durchschnitt — die zeigt wahre Kriegs-DNA.",
    icon: <StarIcon />,
  },
  {
    title: "Rathaus- & Rollen-Verteilung",
    body:
      "Donut-Charts für TH-Spanne und Rollen. Mit Hinweis, wie sich eure Zusammensetzung auf Clan-Krieg-Matchmaking auswirkt.",
    icon: <HomeIcon />,
  },
  {
    title: "Automatische Interpretation",
    body:
      "Der Report erklärt sich selbst: rechts-schief, Konzentration, Netto-Spenden — alles in einfacher Sprache, mit konkreten Handlungsempfehlungen.",
    icon: <LightbulbIcon />,
  },
  {
    title: "Inaktive erkennen",
    body:
      "Automatische Warnung für Mitglieder mit unter 50 Spenden UND unter 20 Angriffen. Handlungsfähig, ohne manuelle Tabellen-Arbeit.",
    icon: <AlertIcon />,
  },
];

const steps = [
  {
    t: "Clan-Tag eingeben",
    d: "Nimm deinen Tag aus dem Spiel (unter dem Clan-Namen, beginnt mit #). Leer lassen startet den Demo-Clan SOLUNA.",
  },
  {
    t: "Daten werden live geholt",
    d: "Parallele Abfrage aller Mitglieder gegen die offizielle Clash-of-Clans-API. Dauert typischerweise 5–15 Sekunden.",
  },
  {
    t: "Analyse lesen",
    d: "Metrik-Karten oben, Interpretation mit Erklärungen, sieben interaktive Charts, volle Rangliste — und ein HTML-Download-Button für den Clan-Chat.",
  },
];

/* ---------- SVG Icons (Lucide-style, inline) ---------- */

function ShieldIcon() {
  return (
    <svg
      width="26"
      height="26"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-amber-700"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}

function SparkleIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden
    >
      <path d="M12 2l2.09 5.91L20 10l-5.91 2.09L12 18l-2.09-5.91L4 10l5.91-2.09L12 2z" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="transition group-hover:translate-x-0.5"
    >
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

function Spinner() {
  return (
    <svg
      className="h-5 w-5 animate-spin"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}

function ChevronIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function TargetIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  );
}

function BalanceIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3v18" />
      <path d="M3 7h18" />
      <path d="M5 7l-3 9c1 2 5 2 6 0L5 7z" />
      <path d="M19 7l-3 9c1 2 5 2 6 0L19 7z" />
    </svg>
  );
}

function StarIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );
}

function HomeIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function LightbulbIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M9 18h6" />
      <path d="M10 22h4" />
      <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}
