import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://british.schoolsoft.online/api";

const requiredFields = ["full_name", "phone_number", "email"] as const;

export async function POST(request: NextRequest) {
  let payload: Record<string, unknown>;

  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "Invalid request payload." }, { status: 400 });
  }

  const hasMissingRequired = requiredFields.some((field) => !String(payload[field] ?? "").trim());
  if (hasMissingRequired) {
    return NextResponse.json(
      { error: "Please complete full name, phone number, and email." },
      { status: 400 },
    );
  }

  const backendResponse = await fetch(`${API_BASE_URL}/home-enquiry-submissions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  const responseText = await backendResponse.text();
  let responseData: unknown = null;

  if (responseText) {
    try {
      responseData = JSON.parse(responseText);
    } catch {
      responseData = { detail: responseText };
    }
  }

  if (!backendResponse.ok) {
    return NextResponse.json(
      responseData || { error: "Unable to submit enquiry at the moment." },
      { status: backendResponse.status },
    );
  }

  return NextResponse.json(responseData || { success: true }, { status: backendResponse.status });
}
