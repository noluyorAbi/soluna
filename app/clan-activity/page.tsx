// app/clan-activity/page.tsx
"use client";
import { useEffect, useState } from "react";

const ClanActivityPage: React.FC = () => {
  const [htmlContent, setHtmlContent] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/clan-activity");
        const html = await response.text();
        setHtmlContent(html);
      } catch (error) {
        console.error("Fehler beim Abrufen der Clan-Aktivität:", error);
        setError("Es gab ein Problem beim Laden der Daten.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <p>Lädt...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
};

export default ClanActivityPage;
