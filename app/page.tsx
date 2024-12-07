// app/page.tsx

import Link from "next/link";
import Head from "next/head";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-gray-50">
      <Head>
        <title>SOLUNA Clan-Aktivitäts-Dashboard</title>
        <meta
          name="description"
          content="Verfolgen Sie die Aktivität der SOLUNA Clan-Mitglieder in Echtzeit."
        />
      </Head>

      {/* Navbar */}
      <header className="flex justify-between items-center p-6 bg-white shadow-md">
        <h1 className="text-2xl font-bold text-blue-600">SOLUNA Dashboard</h1>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <a href="#features" className="text-gray-600 hover:text-blue-600">
                Features
              </a>
            </li>
            <li>
              <a href="#about" className="text-gray-600 hover:text-blue-600">
                Über Uns
              </a>
            </li>
            <li>
              <a href="#contact" className="text-gray-600 hover:text-blue-600">
                Kontakt
              </a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hauptinhalt */}
      <main className="flex-grow flex flex-col items-center justify-center text-center px-4">
        <h2 className="text-5xl font-extrabold text-gray-800 mb-6 leading-tight">
          Willkommen zum{" "}
          <span className="text-blue-600">SOLUNA Clan-Aktivitäts-Dashboard</span>
        </h2>
        <p className="text-lg text-gray-700 mb-8 max-w-2xl">
          Verfolgen Sie die Aktivität der SOLUNA Clan-Mitglieder in Echtzeit.
          Analysieren Sie Spenden, erhaltene Spenden und gewonnene Angriffe mit
          interaktiven Diagrammen.
        </p>
        <Link
          href="/clan-activity"
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-full shadow-lg transition-transform transform hover:scale-105"
        >
          Zum Aktivitäts-Plot
        </Link>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-6">
        <div className="container mx-auto px-4 text-center">
          <p>
            © {new Date().getFullYear()}{" "}
            <span className="font-semibold text-white">SOLUNA</span>. Alle Rechte
            vorbehalten.
          </p>
          <p className="mt-2">
            <a
              href="https://example.com"
              className="text-blue-400 hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              Datenschutzrichtlinien
            </a>{" "}
            |{" "}
            <a
              href="https://example.com"
              className="text-blue-400 hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              Impressum
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
