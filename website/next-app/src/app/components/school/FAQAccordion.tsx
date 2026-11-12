"use client";
import { useState } from "react";
import { FAQItem } from "@/lib/types";

export default function FAQAccordion({ items }: { items: FAQItem[] }) {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={item.id || i} className="rounded-lg border border-blue-100 bg-white">
          <button className="flex w-full items-center justify-between px-4 py-3 text-left font-semibold text-midnight_text" onClick={() => setOpen(open === i ? null : i)}>
            {item.question || item.title || "Frequently asked question"}
            <span>{open === i ? "−" : "+"}</span>
          </button>
          {open === i && <p className="px-4 pb-4 text-sm text-gray">{item.answer || item.description || "Details will be updated soon."}</p>}
        </div>
      ))}
    </div>
  );
}
