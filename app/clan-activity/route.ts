// app/api/clan-activity/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  const search = request.nextUrl.search;

  try {
    const response = await fetch(`${backendUrl}/clan-activity${search}`);
    const htmlContent = await response.text();

    return new NextResponse(htmlContent, {
      status: response.status,
      headers: { "Content-Type": "text/html" },
    });
  } catch (error) {
    console.error("Fehler beim Abrufen der Clan-Aktivität:", error);
    return new NextResponse("Es gab ein Problem beim Laden der Daten.", {
      status: 500,
    });
  }
}
