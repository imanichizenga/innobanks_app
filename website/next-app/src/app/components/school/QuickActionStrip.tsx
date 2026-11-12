"use client";

import Link from "next/link";
import { QuickActionItem } from "@/lib/siteUx";
import { useEnquiryModal } from "./EnquiryModalProvider";

const iconMap: Record<QuickActionItem["icon"], string> = {
  apply: "M12 4v16m8-8H4",
  prospectus: "M7 4h8l4 4v12H7z",
  fees: "M12 4v16m-4-4h8",
  calendar: "M7 5h10M7 9h10M7 13h6",
  results: "M6 15l3-3 2 2 5-6",
  admissions: "M4 7h16M4 12h12M4 17h8",
};

export default function QuickActionStrip({ actions }: { actions: QuickActionItem[] }) {
  const { openEnquiryForm } = useEnquiryModal();
  const validActions = actions.filter((item) => item.key === "apply" || item.href);
  if (!validActions.length) return null;

  return (
    <section className="!py-8 md:!py-10">
      <div className="container mx-auto max-w-screen-xl px-4">
        <div className="rounded-2xl border border-blue-100 bg-white p-3 shadow-sm md:p-4">
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {validActions.map((action) => {
              if (action.key === "apply") {
                return (
                  <button
                    key={action.key}
                    type="button"
                    onClick={openEnquiryForm}
                    className="group flex items-center gap-3 rounded-xl border border-blue-100 bg-section px-3 py-3 text-left transition hover:border-primary/30 hover:bg-blue-50"
                  >
                    <span className="inline-flex h-9 w-9 flex-none items-center justify-center rounded-lg bg-white text-primary shadow-sm">
                      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
                        <path d={iconMap[action.icon]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </span>
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-semibold text-midnight_text group-hover:text-primary">{action.label}</span>
                      {action.description ? <span className="block truncate text-xs text-gray">{action.description}</span> : null}
                    </span>
                  </button>
                );
              }

              const isExternal = action.external || action.href?.startsWith("http");
              return (
                <Link
                  key={action.key}
                  href={action.href!}
                  target={isExternal ? "_blank" : undefined}
                  rel={isExternal ? "noopener noreferrer" : undefined}
                  className="group flex items-center gap-3 rounded-xl border border-blue-100 bg-section px-3 py-3 transition hover:border-primary/30 hover:bg-blue-50"
                >
                  <span className="inline-flex h-9 w-9 flex-none items-center justify-center rounded-lg bg-white text-primary shadow-sm">
                    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
                      <path d={iconMap[action.icon]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-midnight_text group-hover:text-primary">{action.label}</span>
                    {action.description ? <span className="block truncate text-xs text-gray">{action.description}</span> : null}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
