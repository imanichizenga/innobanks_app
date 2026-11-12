"use client";

import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

import { useEffect, useMemo, useState } from "react";
import Slider from "react-slick";
import Image from "next/image";
import Link from "next/link";
import { extractMediaPath, getMediaUrl } from "@/lib/api";
import type { HomeVideoItem } from "@/lib/videos";
import { getVideoSlug } from "@/lib/videos";
import { fallbackImages } from "@/lib/fallbacks";

const formatUploadedDate = (value?: string | null) => {
  if (!value) return "Recently added";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recently added";
  const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] as const;
  const month = monthLabels[date.getUTCMonth()];
  const day = date.getUTCDate();
  const year = date.getUTCFullYear();

  return `${month} ${day}, ${year}`;
};

export default function HomeVideoCarousel({ videos }: { videos: HomeVideoItem[] }) {
  const [activeSlide, setActiveSlide] = useState(0);

  const [mounted, setMounted] = useState(false);
  const activeVideos = useMemo(() => videos.filter((item) => item?.is_active !== false), [videos]);

  useEffect(() => setMounted(true), []);

  if (!activeVideos.length) return null;

  const settings = {
    dots: false,
    infinite: activeVideos.length > 1,
    speed: 550,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: activeVideos.length > 1,
    autoplay: activeVideos.length > 1,
    autoplaySpeed: 6000,
    pauseOnHover: true,
    afterChange: (index: number) => setActiveSlide(index),
    adaptiveHeight: false,
  };

  return (
    <section>
      <div className="container mx-auto max-w-screen-xl px-4">
        <div className="mb-7 flex items-end justify-between gap-3">
          <div>
            <p className="mb-2 inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
              Video Highlights
            </p>
            <h2 className="!text-midnight_text">Inside School Life</h2>
            <p className="mt-2 max-w-2xl text-sm text-gray md:text-base">
              Watch a quick look at our campus, classroom moments, and student experiences.
            </p>
          </div>
          <div className="rounded-full border border-blue-100 bg-white px-3 py-1 text-sm font-semibold text-primary">
            {mounted ? Math.min(activeSlide + 1, activeVideos.length) : 1}/{activeVideos.length}
          </div>
        </div>

        <div className="video-showcase-slider overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm">
          <Slider {...settings}>
            {activeVideos.map((item, index) => {
              const videoSrc = extractMediaPath(item.video);
              const hasVideo = Boolean(videoSrc);
              const videoHref = `/videos/${getVideoSlug(item, index)}`;

              return (
                <div key={item.id || index}>
                  <article className="grid gap-0 lg:grid-cols-[1.45fr_1fr]">
                    <div className="relative bg-[#06255e]">
                      {hasVideo ? (
                        <video
                          controls
                          playsInline
                          preload="metadata"
                          muted
                          autoPlay={index === activeSlide}
                          poster={getMediaUrl(item.thumbnail, fallbackImages.gallery)}
                          className="h-[250px] w-full bg-black object-cover sm:h-[350px] md:h-[430px]"
                        >
                          <source src={getMediaUrl(item.video)} />
                          Your browser does not support the video tag.
                        </video>
                      ) : (
                        <div className="relative h-[250px] w-full sm:h-[350px] md:h-[430px]">
                          <Image
                            src={getMediaUrl(item.thumbnail, fallbackImages.gallery)}
                            alt={item.title?.trim() || "School video thumbnail"}
                            fill
                            className="object-cover"
                          />
                          <div className="absolute inset-0 flex items-center justify-center bg-[#0d2f70]/50 text-sm font-semibold text-white">
                            Video will be available soon
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col justify-between gap-5 p-5 md:p-7">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-primary">Uploaded {formatUploadedDate(item.created_at)}</p>
                        <h3 className="mt-2 !text-2xl !text-midnight_text">{item.title?.trim() || "Campus Moments"}</h3>
                        <p className="mt-3 line-clamp-6 text-sm leading-7 text-gray md:text-base">
                          {item.description?.trim() || "Discover a day at our school through this featured video."}
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center gap-3">
                        <Link href={videoHref} className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
                          Watch full video
                        </Link>
                        <p className="rounded-xl bg-blue-50 px-4 py-3 text-xs font-medium text-primary">
                          Tip: Videos begin muted for a smooth autoplay experience. Use controls to unmute and expand.
                        </p>
                      </div>
                    </div>
                  </article>
                </div>
              );
            })}
          </Slider>
        </div>
      </div>
    </section>
  );
}
