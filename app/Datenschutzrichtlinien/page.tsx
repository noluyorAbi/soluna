"use client";
import Head from "next/head";
import Link from "next/link";

export default function Datenschutzrichtlinien() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 via-white to-gray-100">
      <Head>
        <title>Datenschutzrichtlinien | SOLUNA</title>
        <meta
          name="description"
          content="Erfahren Sie mehr über die Datenschutzrichtlinien des SOLUNA Clan-Aktivitäts-Dashboards."
        />
      </Head>

      {/* Navbar */}
      <header className="flex justify-between items-center p-6 bg-white shadow-md">
        <h1 className="text-2xl font-bold text-blue-600">
          <Link href={"/"}>SOLUNA Dashboard</Link>
        </h1>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link href={"/"}>Startseite</Link>
            </li>
            <li>
              <a href="/contact" className="text-gray-600 hover:text-blue-600">
                Kontakt
              </a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hauptinhalt */}
      <main className="flex-grow container mx-auto px-4 py-12 text-gray-800 mt-10">
        <h1 className="text-5xl  my-64 text-center rounded-md bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 text-blue-600 p-6">
          Datenschutzrichtlinien{" "}
        </h1>
        <section className="mb-8">
          <p className="text-lg mb-4">
            Willkommen bei den Datenschutzrichtlinien des{" "}
            <span className="font-semibold text-gray-900">
              SOLUNA Clan-Aktivitäts-Dashboards
            </span>
            . Der Schutz Ihrer Daten ist uns ein wichtiges Anliegen. In dieser
            Richtlinie erklären wir, wie wir mit den Daten umgehen, die von der
            Clash of Clans API stammen.
          </p>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Herkunft der Daten
          </h3>
          <p className="text-lg mb-4">
            Alle Daten, die im Dashboard angezeigt werden, stammen
            ausschließlich von der offiziellen{" "}
            <a
              href="https://developer.clashofclans.com/#/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Clash of Clans API
            </a>
            . Diese API wird von Supercell, dem Entwickler von Clash of Clans,
            bereitgestellt. Es werden keine persönlichen Daten erhoben, sondern
            lediglich öffentlich zugängliche Informationen über Clan-Aktivitäten
            wie Spenden, Angriffe und Spielerstatistiken abgerufen.
          </p>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Zweck der Datennutzung
          </h3>
          <p className="text-lg mb-4">
            Die abgerufenen Daten dienen ausschließlich dazu, eine Übersicht
            über die Aktivitäten innerhalb des Clans bereitzustellen. Dies hilft
            Clan-Mitgliedern, ihre Leistung zu analysieren und die
            Zusammenarbeit zu verbessern.
          </p>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Datenspeicherung und -sicherheit
          </h3>
          <p className="text-lg mb-4">
            Wir speichern keine Daten langfristig. Alle Informationen werden
            direkt von der API geladen und nur für die Dauer der Anzeige im
            Dashboard verwendet. Es erfolgt keine Weitergabe oder kommerzielle
            Nutzung dieser Daten.
          </p>
        </section>

        <section>
          <p className="text-lg">
            Sollten Sie weitere Fragen oder Bedenken haben, kontaktieren Sie uns
            gerne über die bereitgestellten Kontaktmöglichkeiten.
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-6">
        <div className="container mx-auto px-4 text-center">
          <p>
            © {new Date().getFullYear()}{" "}
            <span className="font-semibold text-white">SOLUNA</span>. Alle
            Rechte vorbehalten.
          </p>
          <p className="mt-2">
            <a
              href="/Datenschutzrichtlinien"
              className="text-blue-400 hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              Datenschutzrichtlinien
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
