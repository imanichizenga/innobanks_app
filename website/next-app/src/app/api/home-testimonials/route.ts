import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://british.schoolsoft.online/api";

const REQUIRED_TEXT_FIELDS = ["full_name", "message"] as const;

function readField(formData: FormData, field: string): string {
  const value = formData.get(field);
  return typeof value === "string" ? value.trim() : "";
}

export async function POST(request: NextRequest) {
  let formData: FormData;

  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json({ error: "Invalid form submission." }, { status: 400 });
  }

  const hasMissingRequired = REQUIRED_TEXT_FIELDS.some((field) => !readField(formData, field));
  if (hasMissingRequired) {
    return NextResponse.json({ error: "Please provide your name and story message." }, { status: 400 });
  }

  const backendResponse = await fetch(`${API_BASE_URL}/home-testimonials/`, {
    method: "POST",
    body: formData,
    cache: "no-store",
  });

  const raw = await backendResponse.text();
  let data: unknown = null;

  if (raw) {
    try {
      data = JSON.parse(raw);
    } catch {
      data = { detail: raw };
    }
  }

  if (!backendResponse.ok) {
    return NextResponse.json(data || { error: "Unable to submit story right now." }, { status: backendResponse.status });
  }

  return NextResponse.json(data || { success: true, message: "Story submitted for approval." }, { status: backendResponse.status });
}
