import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://soluna-clan.vercel.app"),
  title: {
    default: "SOLUNA · Clash of Clans Aktivitäts-Dashboard",
    template: "%s · SOLUNA",
  },
  description:
    "Kostenloses Clash-of-Clans Analyse-Tool: Aktivitäts-Score, Spenden-Bilanz, Top-Angreifer, Kriegs-Sterne, Rathaus-Verteilung und automatische Interpretation für jeden Clan. Einfach Clan-Tag eingeben.",
  keywords: [
    "Clash of Clans",
    "CoC Dashboard",
    "Clan-Aktivität",
    "Clan-Analyse",
    "Clash of Clans Statistiken",
    "Clan-Tool",
    "CoC Spenden",
    "CoC Angriffe",
    "Kriegs-Sterne",
    "Clan-Rangliste",
    "Clash of Clans Deutsch",
    "Clan-Tag Suche",
    "Rathaus",
    "Aktivitäts-Score",
    "SOLUNA",
  ],
  authors: [{ name: "Alpi" }],
  creator: "Alpi",
  openGraph: {
    type: "website",
    locale: "de_DE",
    url: "https://soluna-clan.vercel.app",
    title: "SOLUNA · Clash of Clans Aktivitäts-Dashboard",
    description:
      "Analysiere jeden CoC-Clan in Echtzeit: Aktivitäts-Score, Top-Spender, Kriegs-Sterne und mehr — automatisch interpretiert.",
    siteName: "SOLUNA",
  },
  twitter: {
    card: "summary_large_image",
    title: "SOLUNA · Clash of Clans Aktivitäts-Dashboard",
    description:
      "Analysiere jeden CoC-Clan in Echtzeit: Aktivität, Spenden, Kriegs-Sterne, Rathaus-Verteilung — automatisch interpretiert.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "/",
  },
  category: "Gaming",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
