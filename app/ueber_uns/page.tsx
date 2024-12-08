"use client";
import Head from "next/head";
import Link from "next/link";

export default function Features() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 via-white to-gray-100">
      <Head>
        <title>Features der Seite | SOLUNA</title>
        <meta
          name="description"
          content="Erfahren Sie, wie das SOLUNA-Tool den Clan aktiver und stärker macht."
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
              <a href="https://discord.gg/G2Br635S4B" className="text-gray-600 hover:text-blue-600">
                Kontakt
              </a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hauptinhalt */}
      <main className="flex-grow container mx-auto px-4 py-12 text-gray-800 mt-20">
        <h1 className="text-5xl  my-64 text-center rounded-md bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 text-blue-600 p-6">
          Gemeinsam stärker bei SOLUNA
        </h1>
        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Unser Clan, unsere Regeln
          </h3>
          <p className="text-lg mb-4">
            SOLUNA ist mehr als nur ein Name – es ist unser Clan und unsere
            Gemeinschaft. Dieses Tool wurde von uns speziell entwickelt, um den
            Clan noch aktiver und erfolgreicher zu machen. Ob Spenden, Angriffe
            oder Strategien: Mit SOLUNA-Dashboard bleiben wir immer auf dem Laufenden und
            arbeiten zusammen, um stärker zu werden.
          </p>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Aktiv bleiben leicht gemacht
          </h3>
          <p className="text-lg mb-4">
            Wie oft habt ihr euch gefragt, wer wie viel spendet oder wer die
            meisten Angriffe durchführt? Unser Tool bringt Licht ins Dunkel und
            zeigt euch auf einen Blick, wie aktiv jedes Clanmitglied ist. So
            können wir unsere Leistungen besser einschätzen und uns gegenseitig
            motivieren.
          </p>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Echtzeit-Feedback für den Erfolg
          </h3>
          <p className="text-lg mb-4">
            Mit Echtzeit-Updates behält der gesamte Clan den Überblick. Ob
            während eines Krieges oder in der täglichen Planung – SOLUNA-Dashboard sorgt
            dafür, dass jeder die richtigen Informationen hat, um die besten
            Entscheidungen zu treffen.
          </p>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            Motivation und Gemeinschaft
          </h3>
          <p className="text-lg mb-4">
            Unser Ziel war es, nicht nur ein praktisches Tool zu schaffen,
            sondern auch den Spaß am Spiel zu fördern. SOLUNA hilft uns, unsere
            Fortschritte zu feiern und als Gemeinschaft zusammenzuwachsen. Jeder
            Punkt, jeder Sieg und jede Spende trägt zum Erfolg unseres Clans
            bei.
          </p>
        </section>

        <section>
          <p className="text-lg">
            Wenn du auch Teil einer aktiven und motivierten Gemeinschaft werden
            willst, bist du bei uns genau richtig!
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
              href="/features"
              className="text-blue-400 hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              Features der Seite
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
