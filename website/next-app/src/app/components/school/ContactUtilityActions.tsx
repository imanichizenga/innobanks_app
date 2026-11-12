"use client";

import { useState } from "react";

export default function ContactUtilityActions({ phone, email }: { phone?: string; email?: string }) {
  const [copied, setCopied] = useState<string>("");

  const copyText = async (value: string, label: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(`${label} copied`);
      setTimeout(() => setCopied(""), 1500);
    } catch {
      setCopied("Copy not supported");
    }
  };

  const cleanPhone = phone?.replace(/\s+/g, "") || "";
  const wa = phone ? `https://wa.me/${phone.replace(/[^\d]/g, "")}` : "";

  return (
    <div className="mt-3 space-y-2">
      <div className="flex flex-wrap gap-2 text-xs">
        {phone ? <a href={`tel:${cleanPhone}`} className="rounded-md border border-blue-100 bg-white px-3 py-2 font-semibold text-primary hover:bg-blue-50">Call</a> : null}
        {phone ? <a href={wa} target="_blank" rel="noopener noreferrer" className="rounded-md border border-blue-100 bg-white px-3 py-2 font-semibold text-primary hover:bg-blue-50">WhatsApp</a> : null}
        {email ? <a href={`mailto:${email}`} className="rounded-md border border-blue-100 bg-white px-3 py-2 font-semibold text-primary hover:bg-blue-50">Email</a> : null}
        {phone ? <button type="button" onClick={() => copyText(phone, "Phone")} className="rounded-md border border-blue-100 bg-white px-3 py-2 font-semibold text-midnight_text hover:bg-blue-50">Copy phone</button> : null}
        {email ? <button type="button" onClick={() => copyText(email, "Email")} className="rounded-md border border-blue-100 bg-white px-3 py-2 font-semibold text-midnight_text hover:bg-blue-50">Copy email</button> : null}
      </div>
      {copied ? <p className="text-xs text-gray">{copied}</p> : <p className="text-xs text-gray">We usually reply within 1 business day.</p>}
    </div>
  );
}
