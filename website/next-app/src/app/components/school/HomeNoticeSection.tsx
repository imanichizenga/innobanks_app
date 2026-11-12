"use client";

import { useMemo } from "react";
import Image from "next/image";
import { extractMediaPath, getMediaUrl } from "@/lib/api";
import { fallbackImages } from "@/lib/fallbacks";
import { useEnquiryModal } from "./EnquiryModalProvider";

type HomeNoticeItem = {
  id?: number;
  title?: string | null;
  subtitle?: string | null;
  description?: string | null;
  button_text?: string | null;
  badge_label?: string | null;
  background_image?: unknown;
  is_active?: boolean;
};

export default function HomeNoticeSection({ notices }: { notices: HomeNoticeItem[] }) {
  const { openEnquiryForm } = useEnquiryModal();
  const activeNotice = useMemo(() => notices.find((item) => item?.is_active !== false) || notices[0], [notices]);
  if (!activeNotice) return null;

  const title = activeNotice.title?.trim() || "Admissions Notice";
  const subtitle = activeNotice.subtitle?.trim() || "New intake open now";
  const description =
    activeNotice.description?.trim() ||
    "Speak with our admissions team to receive guidance about classes, requirements, and enrollment timelines.";
  const buttonText = activeNotice.button_text?.trim() || "Register Interest";

  return (
    <section>
      <div className="container mx-auto max-w-screen-xl px-4">
        <div className="relative overflow-hidden rounded-3xl border border-blue-100 bg-primary px-6 py-10 text-white md:px-10 md:py-12">
          {extractMediaPath(activeNotice.background_image) ? (
            <Image
              src={getMediaUrl(activeNotice.background_image, fallbackImages.heroAlt)}
              alt={title}
              fill
              className="object-cover opacity-20"
            />
          ) : null}
          <div className="absolute inset-0 bg-gradient-to-r from-[#0d2f70] to-[#2f73f2]/90" />

          <div className="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <p className="mb-3 inline-flex rounded-full border border-white/30 bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]">
                {activeNotice.badge_label?.trim() || "Important Notice"}
              </p>
              <h2 className="!text-white">{title}</h2>
              <p className="mt-2 text-blue-100">{subtitle}</p>
              <p className="mt-3 max-w-xl text-sm text-blue-50 md:text-base">{description}</p>
            </div>

            <button
              type="button"
              onClick={openEnquiryForm}
              className="inline-flex w-full items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-bold uppercase tracking-wide text-primary transition hover:bg-blue-50 md:w-auto"
            >
              {buttonText}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
