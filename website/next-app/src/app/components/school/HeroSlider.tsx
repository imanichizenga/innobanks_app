"use client";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

import Image from "next/image";
import Link from "next/link";
import Slider from "react-slick";
import { useEffect, useState } from "react";
import { fallbackImages, fallbackText } from "@/lib/fallbacks";
import { getMediaUrl } from "@/lib/api";

interface Slide {
  id?: number;
  title?: string | null;
  subtitle?: string | null;
  description?: string | null;
  image?: unknown;
  button_text?: string | null;
  button_link?: string | null;
  second_button_text?: string | null;
  second_button_link?: string | null;
}

const normalizeText = (value?: string | null) => {
  if (value === null || value === undefined) return undefined;
  const trimmed = value.trim();
  return trimmed.length ? trimmed : undefined;
};

export default function HeroSlider({ slides }: { slides: Slide[] }) {
  const data = slides.length
    ? slides
    : [
        {
          title: fallbackText.heroTitle,
          subtitle: fallbackText.heroDescription,
          image: fallbackImages.hero,
        },
      ];

  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    const first = data[0];
    const title = normalizeText(first.title);
    const subtitle = normalizeText(first.subtitle);
    const description = normalizeText(first.description);

    return (
      <section className="relative !py-0">
        <div className="relative h-[65vh] min-h-[420px]">
          <Image src={getMediaUrl(first.image, fallbackImages.hero)} alt={title ?? "School hero"} fill className="object-cover" priority />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0d2f70]/80 to-[#0d2f70]/30" />
          <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-center px-4">
            <div className="max-w-2xl text-white">
              <p className="mb-4 text-sm uppercase tracking-[0.2em] text-blue-100">Welcome to {fallbackText.schoolName}</p>
              {subtitle !== undefined ? <p className="mb-2 text-base font-medium text-blue-100">{subtitle}</p> : null}
              <h2 className="mb-5 !text-white">{title ?? fallbackText.heroTitle}</h2>
              <p className="mb-7 text-blue-50">{description ?? fallbackText.heroDescription}</p>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative !py-0">
      <Slider dots autoplay arrows={false} infinite className="hero-slider">
        {data.map((slide, i) => {
          const ctaText = normalizeText(slide.button_text);
          const ctaLink = normalizeText(slide.button_link);
          const secondCtaText = normalizeText(slide.second_button_text);
          const secondCtaLink = normalizeText(slide.second_button_link);
          const title = normalizeText(slide.title);
          const subtitle = normalizeText(slide.subtitle);
          const description = normalizeText(slide.description);
          const hasCta = Boolean(ctaText && ctaLink);
          const hasSecondCta = Boolean(secondCtaText && secondCtaLink);

          return (
            <div key={slide.id || i}>
              <div className="relative h-[65vh] min-h-[420px]">
                <Image src={getMediaUrl(slide.image, fallbackImages.hero)} alt={title ?? "School hero"} fill className="object-cover" priority={i === 0} />
                <div className="absolute inset-0 bg-gradient-to-r from-[#0d2f70]/80 to-[#0d2f70]/30" />
                <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-center px-4">
                  <div className="max-w-2xl text-white">
                    <p className="mb-4 text-sm uppercase tracking-[0.2em] text-blue-100">Welcome to {fallbackText.schoolName}</p>
                    {subtitle !== undefined ? <p className="mb-2 text-base font-medium text-blue-100">{subtitle}</p> : null}
                    <h2 className="mb-5 !text-white">{title ?? fallbackText.heroTitle}</h2>
                    <p className="mb-7 text-blue-50">{description ?? fallbackText.heroDescription}</p>
                    <div className="flex flex-wrap gap-3">
                      {hasCta ? (
                        <Link href={ctaLink as string} className="rounded-lg bg-primary px-5 py-3 font-semibold text-white">
                          {ctaText}
                        </Link>
                      ) : null}
                      {hasSecondCta ? (
                        <Link href={secondCtaLink as string} className="rounded-lg border border-white px-5 py-3 font-semibold text-white">
                          {secondCtaText}
                        </Link>
                      ) : (
                        <Link href="/academics" className="rounded-lg border border-white px-5 py-3 font-semibold text-white">
                          Explore Academics
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </Slider>
    </section>
  );
}
