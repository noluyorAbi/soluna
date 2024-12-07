// app/api/clan-activity/route.ts

import { NextResponse } from "next/server";

export async function GET() {
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  try {
    const response = await fetch(`${backendUrl}/clan-activity`);
    const htmlContent = await response.text();

    return new NextResponse(htmlContent, {
      status: 200,
      headers: { "Content-Type": "text/html" },
    });
  } catch (error) {
    console.error("Fehler beim Abrufen der Clan-Aktivität:", error);
    return new NextResponse("Es gab ein Problem beim Laden der Daten.", {
      status: 500,
    });
  }
}
