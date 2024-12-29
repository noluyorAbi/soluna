"use client";
import Head from "next/head";
import Link from "next/link";

export default function Features() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Head>
        <title>Funktionen & Vorteile | SOLUNA</title>
        <meta
          name="description"
          content="Entdecken Sie die Vorteile von SOLUNA: Stärken Sie Ihren Clan durch verbesserte Aktivität und Zusammenarbeit."
        />
      </Head>

      {/* Navbar */}
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link href={"/"} className="text-xl font-semibold text-blue-600">
            SOLUNA Dashboard
          </Link>
          <nav>
            <ul className="flex space-x-8">
              <li>
                <Link
                  href={"/"}
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200"
                >
                  Startseite
                </Link>
              </li>
              <li>
                <a
                  href="https://discord.gg/G2Br635S4B"
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Kontakt
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      {/* Hauptinhalt */}
      <main className="container mx-auto px-6 py-16">
        <section className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Gemeinsam stärker mit SOLUNA
          </h1>
          <p className="text-gray-700 text-lg">
            Entdecken Sie, wie SOLUNA Ihren Clan transformiert.
          </p>
        </section>

        <section className="grid md:grid-cols-2 gap-12 mb-16">
          <div>
            <h3 className="text-2xl font-semibold text-blue-600 mb-4">
              Unser Clan, unsere Regeln
            </h3>
            <p className="text-gray-700 leading-relaxed">
              SOLUNA ist mehr als nur ein Name – es ist unser Clan und unsere
              Gemeinschaft. Dieses Tool wurde von uns speziell entwickelt, um
              den Clan noch aktiver und erfolgreicher zu machen. Ob Spenden,
              Angriffe oder Strategien: Mit dem SOLUNA-Dashboard bleiben wir
              immer auf dem Laufenden und arbeiten zusammen, um stärker zu
              werden.
            </p>
          </div>
          <div className="flex items-center justify-center">
            {/* Hier könnte ein passendes Icon oder eine Grafik eingefügt werden */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-16 h-16 text-blue-500"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M10.5 6a7.5 7.5 0 107.5 7.5h-7.5V6z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.5 10.5H21A7.5 7.5 0 0013.5 3v7.5z"
              />
            </svg>
          </div>
        </section>

        <section className="grid md:grid-cols-2 gap-12 mb-16">
          <div className="flex items-center justify-center">
            {/* Hier könnte ein passendes Icon oder eine Grafik eingefügt werden */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-16 h-16 text-blue-500"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-2xl font-semibold text-blue-600 mb-4">
              Aktiv bleiben leicht gemacht
            </h3>
            <p className="text-gray-700 leading-relaxed">
              Wie oft habt ihr euch gefragt, wer wie viel spendet oder wer die
              meisten Angriffe durchführt? Unser Tool bringt Licht ins Dunkel
              und zeigt euch auf einen Blick, wie aktiv jedes Clanmitglied ist.
              So können wir unsere Leistungen besser einschätzen und uns
              gegenseitig motivieren.
            </p>
          </div>
        </section>

        <section className="grid md:grid-cols-2 gap-12 mb-16">
          <div>
            <h3 className="text-2xl font-semibold text-blue-600 mb-4">
              Echtzeit-Feedback für den Erfolg
            </h3>
            <p className="text-gray-700 leading-relaxed">
              Mit Echtzeit-Updates behält der gesamte Clan den Überblick. Ob
              während eines Krieges oder in der täglichen Planung – das
              SOLUNA-Dashboard sorgt dafür, dass jeder die richtigen
              Informationen hat, um die besten Entscheidungen zu treffen.
            </p>
          </div>
          <div className="flex items-center justify-center">
            {/* Hier könnte ein passendes Icon oder eine Grafik eingefügt werden */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-16 h-16 text-blue-500"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4.5 12.75l7.5-7.5 7.5 7.5m-15 6l7.5-7.5 7.5 7.5"
              />{" "}
              {/* Einfacher Pfeil */}
            </svg>
          </div>
        </section>

        <section className="grid md:grid-cols-2 gap-12 mb-16">
          <div className="flex items-center justify-center">
            {/* Hier könnte ein passendes Icon oder eine Grafik eingefügt werden */}
            <svg
              width="100"
              height="100"
              viewBox="0 0 100 100"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="30" cy="30" r="10" fill="#3498db" />
              <circle cx="70" cy="30" r="10" fill="#3498db" />
              <circle cx="50" cy="70" r="10" fill="#3498db" />
              <line
                x1="37.071"
                y1="37.071"
                x2="62.929"
                y2="37.071"
                stroke="#3498db"
                stroke-width="3"
              />
              <line
                x1="35.355"
                y1="39.645"
                x2="44.645"
                y2="60.355"
                stroke="#3498db"
                stroke-width="3"
              />
              <line
                x1="64.645"
                y1="39.645"
                x2="55.355"
                y2="60.355"
                stroke="#3498db"
                stroke-width="3"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-2xl font-semibold text-blue-600 mb-4">
              Motivation und Gemeinschaft
            </h3>
            <p className="text-gray-700 leading-relaxed">
              Unser Ziel war es, nicht nur ein praktisches Tool zu schaffen,
              sondern auch den Spaß am Spiel zu fördern. SOLUNA hilft uns,
              unsere Fortschritte zu feiern und als Gemeinschaft
              zusammenzuwachsen. Jeder Punkt, jeder Sieg und jede Spende trägt
              zum Erfolg unseres Clans bei.
            </p>
          </div>
        </section>

        <section className="text-center">
          <p className="text-lg text-gray-700">
            Werden Sie Teil einer aktiven und motivierten Gemeinschaft!
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-8">
        <div className="container mx-auto px-6 text-center">
          <p className="mb-2">
            © {new Date().getFullYear()}{" "}
            <span className="font-semibold text-white">SOLUNA</span>. Alle
            Rechte vorbehalten.
          </p>
          {/* Link zur Kontaktseite könnte hier sinnvoll sein */}
        </div>
      </footer>
    </div>
  );
}
