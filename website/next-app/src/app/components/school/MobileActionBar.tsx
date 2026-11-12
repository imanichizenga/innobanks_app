"use client";

import { useState } from "react";
import { useEnquiryModal } from "./EnquiryModalProvider";

interface MobileActionBarProps {
  phone?: string;
  whatsapp?: string;
  showApply?: boolean;
}

const icon = {
  call: "M5 4h3l2 5-2 1a12 12 0 0 0 5 5l1-2 5 2v3a2 2 0 0 1-2 2h-1C9 20 4 15 4 8V6a2 2 0 0 1 1-2Z",
  whatsapp: "M20 11.6a8.4 8.4 0 0 1-12.4 7.4L4 20l1.1-3.3A8.4 8.4 0 1 1 20 11.6Z",
  apply: "M12 5v14m7-7H5",
  menu: "M12 5v14m7-7H5",
};

export default function MobileActionBar({ phone, whatsapp, showApply = true }: MobileActionBarProps) {
  const { openEnquiryForm } = useEnquiryModal();
  const [desktopOpen, setDesktopOpen] = useState(false);

  const cleanPhone = phone?.replace(/\s+/g, "") || "";
  const waLink = whatsapp ? `https://wa.me/${whatsapp.replace(/[^\d]/g, "")}` : "";

  const items = [
    phone ? { key: "call", label: "Call", href: `tel:${cleanPhone}` } : null,
    waLink ? { key: "whatsapp", label: "WhatsApp", href: waLink, external: true } : null,
    showApply ? { key: "apply", label: "Apply" } : null,
  ].filter(Boolean) as { key: "call" | "whatsapp" | "apply"; label: string; href?: string; external?: boolean }[];

  if (!items.length) return null;

  return (
    <>
      <div className="fixed bottom-5 right-5 z-[150] hidden lg:block">
        <div className="flex flex-col items-end gap-2">
          {desktopOpen ? (
            <div className="space-y-2">
              {items.map((item) =>
                item.key === "apply" ? (
                  <button
                    key={item.key}
                    type="button"
                    onClick={() => {
                      openEnquiryForm();
                      setDesktopOpen(false);
                    }}
                    className="flex min-w-[140px] items-center justify-between rounded-full border border-blue-100 bg-white px-4 py-2 text-sm font-semibold text-midnight_text shadow-property transition hover:bg-blue-50 hover:text-primary"
                  >
                    {item.label}
                    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden><path d={icon[item.key]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  </button>
                ) : (
                  <a
                    key={item.key}
                    href={item.href}
                    target={item.external ? "_blank" : undefined}
                    rel={item.external ? "noopener noreferrer" : undefined}
                    className="flex min-w-[140px] items-center justify-between rounded-full border border-blue-100 bg-white px-4 py-2 text-sm font-semibold text-midnight_text shadow-property transition hover:bg-blue-50 hover:text-primary"
                  >
                    {item.label}
                    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden><path d={icon[item.key]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  </a>
                ),
              )}
            </div>
          ) : null}

          <button
            type="button"
            onClick={() => setDesktopOpen((v) => !v)}
            className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary text-white shadow-property transition hover:bg-[#245fcd]"
            aria-expanded={desktopOpen}
            aria-label="Toggle quick actions"
          >
            <svg viewBox="0 0 24 24" className={`h-5 w-5 transition-transform ${desktopOpen ? "rotate-45" : ""}`} fill="none" aria-hidden>
              <path d={icon.menu} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>

      <div className="fixed inset-x-3 bottom-3 z-[150] lg:hidden">
        <nav className={`grid gap-1 rounded-xl border border-blue-100 bg-white/95 p-1 shadow-property backdrop-blur ${items.length === 3 ? "grid-cols-3" : "grid-cols-2"}`} aria-label="Quick mobile actions">
          {items.map((item) =>
            item.key === "apply" ? (
              <button
                key={item.key}
                type="button"
                onClick={openEnquiryForm}
                className="rounded-lg px-2 py-2 text-center text-xs font-semibold text-midnight_text transition hover:bg-blue-50 hover:text-primary"
              >
                {item.label}
              </button>
            ) : (
              <a
                key={item.key}
                href={item.href}
                target={item.external ? "_blank" : undefined}
                rel={item.external ? "noopener noreferrer" : undefined}
                className="rounded-lg px-2 py-2 text-center text-xs font-semibold text-midnight_text transition hover:bg-blue-50 hover:text-primary"
              >
                {item.label}
              </a>
            ),
          )}
        </nav>
      </div>
    </>
  );
}
