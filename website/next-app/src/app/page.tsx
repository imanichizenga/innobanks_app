import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { asArray, extractMediaPath, fetchAPI, getMediaUrl } from "@/lib/api";
import { fallbackImages, fallbackText } from "@/lib/fallbacks";
import { buildMetadata, toAbsoluteUrl } from "@/lib/seo";
import { SITE_NAME } from "@/lib/site";
import HeroSlider from "./components/school/HeroSlider";
import SectionHeading from "./components/school/SectionHeading";
import EmptyState from "./components/school/EmptyState";
import { GenericCard } from "./components/school/cards";
import ImageGallery from "./components/school/ImageGallery";
import HomeVideoCarousel from "./components/school/HomeVideoCarousel";
import HomeNoticeSection from "./components/school/HomeNoticeSection";
import QuickActionStrip from "./components/school/QuickActionStrip";
import ApplyNowButton from "./components/school/ApplyNowButton";
import AdmissionsJourneySection from "./components/school/AdmissionsJourneySection";
import TrustSection from "./components/school/TrustSection";
import TestimonialsSection from "./components/school/TestimonialsSection";
import { admissionsJourneyFallback, quickActions, testimonialFallback, trustHighlightsFallback } from "@/lib/siteUx";

type HomePageData = {
  id?: number;
  title?: string | null;
  description?: string | null;
  hero_title?: string | null;
  hero_subtitle?: string | null;
  hero_description?: string | null;
  hero_image?: unknown;
  hero_button_text?: string | null;
  hero_button_link?: string | null;
  hero_second_button_text?: string | null;
  hero_second_button_link?: string | null;
  welcome_title?: string | null;
  welcome_description?: string | null;
  welcome_image?: unknown;
  tour_title?: string | null;
  tour_description?: string | null;
  tour_thumbnail?: unknown;
  tour_video_url?: string | null;
  stats_title?: string | null;
  meta_title?: string | null;
  meta_description?: string | null;
  is_active?: boolean;
};

type HomeSliderItem = {
  id?: number;
  title?: string | null;
  subtitle?: string | null;
  description?: string | null;
  image?: unknown;
  button_text?: string | null;
  button_link?: string | null;
  second_button_text?: string | null;
  second_button_link?: string | null;
  order?: number | null;
  is_active?: boolean;
};

type HomeFeatureItem = {
  id?: number;
  title?: string | null;
  short_description?: string | null;
  icon_image?: unknown;
  order?: number | null;
  is_active?: boolean;
};

type HomeStatisticItem = {
  id?: number;
  label?: string | null;
  value?: string | number | null;
  icon_image?: unknown;
  order?: number | null;
};

type HomeGalleryItem = {
  id?: number;
  title?: string | null;
  image?: unknown;
  gallery_image?: unknown;
  caption?: string | null;
  order?: number | null;
};

type HomeVideoItem = {
  id?: number;
  title?: string | null;
  description?: string | null;
  video?: unknown;
  thumbnail?: unknown;
  order?: number | null;
  is_active?: boolean;
  created_at?: string | null;
};


type HomeTestimonialItem = {
  id?: number;
  full_name?: string | null;
  role?: string | null;
  message?: string | null;
  rating?: number | null;
  image?: unknown;
  is_approved?: boolean;
  order?: number | null;
};

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


export async function generateMetadata(): Promise<Metadata> {
  const pages = await fetchAPI<unknown>("/home-pages/");
  const home = asArray<HomePageData>(pages).find((item) => item?.is_active !== false) || asArray<HomePageData>(pages)[0];
  const title = home?.meta_title?.trim() || home?.hero_title?.trim() || SITE_NAME;
  const description = home?.meta_description?.trim() || home?.hero_description?.trim() || fallbackText.heroDescription;
  return buildMetadata({
    title,
    description,
    path: "/",
    image: getMediaUrl(home?.hero_image, fallbackImages.hero),
  });
}

const byOrder = <T extends { order?: number | null }>(items: T[]) =>
  [...items].sort((a, b) => (a.order ?? Number.MAX_SAFE_INTEGER) - (b.order ?? Number.MAX_SAFE_INTEGER));

export default async function Home() {
  const [pages, slides, features, statistics, gallery, courses, news, events, videos, notices, testimonials] = await Promise.all([
    fetchAPI<unknown>("/home-pages/"),
    fetchAPI<unknown>("/home-sliders/"),
    fetchAPI<unknown>("/home-features/"),
    fetchAPI<unknown>("/home-statistics/"),
    fetchAPI<unknown>("/home-gallery/"),
    fetchAPI<unknown>("/courses/"),
    fetchAPI<unknown>("/news-items/"),
    fetchAPI<unknown>("/event-items/"),
    fetchAPI<unknown>("/home-videos/"),
    fetchAPI<unknown>("/home-notices/"),
    fetchAPI<unknown>("/home-testimonials/"),
  ]);

  const homePages = asArray<HomePageData>(pages);
  const homePage = homePages.find((item) => item?.is_active !== false) || homePages[0] || {};
  const slideItems = byOrder(asArray<HomeSliderItem>(slides).filter((item) => item?.is_active !== false));
  const featureItems = byOrder(asArray<HomeFeatureItem>(features).filter((item) => item?.is_active !== false));
  const statItems = byOrder(asArray<HomeStatisticItem>(statistics));
  const galleryItems = byOrder(asArray<HomeGalleryItem>(gallery)).map((item) => ({
    ...item,
    image: item.image ?? item.gallery_image ?? null,
  }));
  const homeVideos = byOrder(asArray<HomeVideoItem>(videos));
  const homeNotices = asArray<HomeNoticeItem>(notices);
  const testimonialItems = byOrder(asArray<HomeTestimonialItem>(testimonials).filter((item) => item?.is_approved !== false));
  const courseItems = asArray<any>(courses).slice(0, 6);
  const newsItems = asArray<any>(news).slice(0, 5);
  const eventItems = asArray<any>(events).slice(0, 5);

  const trustItems = statItems.length
    ? statItems.slice(0, 6).map((item) => ({
        title: item.label?.trim() || "School Metric",
        value: String(item.value ?? "—"),
        description: "Verified institutional data and outcomes.",
      }))
    : trustHighlightsFallback;

  const displayTestimonials = testimonialItems.length
    ? testimonialItems.map((item) => ({
        message: item.message?.trim() || "School community feedback will be available soon.",
        full_name: item.full_name?.trim() || "School Community",
        role: item.role?.trim() || "Parent / Student",
        rating: item.rating || undefined,
        image: item.image,
      }))
    : testimonialFallback.map((item) => ({
        message: item.quote,
        full_name: item.name,
        role: item.role,
        rating: item.rating,
      }));

  const heroFallbackSlide: HomeSliderItem[] = [
    {
      id: homePage.id,
      title: homePage.hero_title || fallbackText.heroTitle,
      subtitle: homePage.hero_subtitle || undefined,
      description: homePage.hero_description || undefined,
      image: homePage.hero_image || fallbackImages.hero,
      button_text: homePage.hero_button_text || undefined,
      button_link: homePage.hero_button_link || undefined,
      second_button_text: homePage.hero_second_button_text || undefined,
      second_button_link: homePage.hero_second_button_link || undefined,
    },
  ];

  const heroSlides = slideItems.length
    ? slideItems.map((slide) => ({
        ...slide,
        title: slide.title || homePage.hero_title || fallbackText.heroTitle,
        subtitle: slide.subtitle || homePage.hero_subtitle || undefined,
        description: slide.description || homePage.hero_description || undefined,
        second_button_text: slide.second_button_text || homePage.hero_second_button_text || undefined,
        second_button_link: slide.second_button_link || homePage.hero_second_button_link || undefined,
      }))
    : heroFallbackSlide;
  const primaryHeading = heroSlides[0]?.title?.trim() || homePage.hero_title?.trim() || fallbackText.heroTitle;

  const welcomeTitle = homePage.welcome_title?.trim() || "Welcome to our institution";
  const welcomeDescription = homePage.welcome_description?.trim() || homePage.description?.trim() || fallbackText.heroDescription;
  const hasWelcomeImage = Boolean(extractMediaPath(homePage.welcome_image));

  const tourTitle = homePage.tour_title?.trim() || "Take a Campus Tour";
  const tourDescription =
    homePage.tour_description?.trim() || "Explore our learning spaces, student life, and school facilities through our campus tour.";
  const tourVideoUrl = homePage.tour_video_url?.trim() || "";
  const hasTourThumbnail = Boolean(extractMediaPath(homePage.tour_thumbnail));

  const organizationJsonLd = {
    "@context": "https://schema.org",
    "@type": "EducationalOrganization",
    name: SITE_NAME,
    url: toAbsoluteUrl("/"),
    logo: toAbsoluteUrl("/favicon.ico"),
    description: welcomeDescription,
  };

  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }} />
      <h1 className="sr-only">{primaryHeading}</h1>
      <HeroSlider slides={heroSlides} />
      <QuickActionStrip actions={quickActions} />

     <section className="welcome-premium-section py-2 md:py-4">
  <div className="container mx-auto max-w-screen-xl px-4">
    <div className="welcome-shell relative overflow-hidden rounded-[2rem] border border-blue-100/80 bg-white shadow-[0_20px_60px_rgba(15,23,42,0.08)]">
      <div className="welcome-ambient absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.18),transparent_34%),radial-gradient(circle_at_bottom_left,rgba(37,99,235,0.14),transparent_30%)]" />
      <div className="welcome-orb-1 absolute right-0 top-0 h-44 w-44 rounded-full bg-blue-200/60 blur-3xl" />
      <div className="welcome-orb-2 absolute bottom-0 left-0 h-44 w-44 rounded-full bg-sky-200/60 blur-3xl" />

      <div className="relative grid items-center gap-10 p-5 md:p-8 lg:grid-cols-[1.05fr_0.95fr] lg:p-10 xl:p-12">
        <div className="welcome-copy relative z-10">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary shadow-sm">
            <span className="welcome-badge-dot h-2.5 w-2.5 rounded-full bg-primary" />
            Principal’s Welcome
          </div>

          <h2 className="max-w-2xl !text-midnight_text">
            {welcomeTitle}
          </h2>

          <p className="mt-5 max-w-2xl text-sm leading-7 text-gray md:text-base">
            {welcomeDescription}
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="welcome-info-card rounded-2xl border border-blue-100 bg-blue-50/70 p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
                Education for Skills
              </p>
              <p className="mt-2 text-sm leading-6 text-gray">
                We combine academic learning with practical skills that prepare students for real-life success.
              </p>
            </div>

            <div className="welcome-info-card rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
                Student-Centred Growth
              </p>
              <p className="mt-2 text-sm leading-6 text-gray">
                We nurture confidence, discipline, and excellence in a supportive and inspiring environment.
              </p>
            </div>
          </div>

          <div className="mt-8 grid gap-3 sm:flex sm:flex-wrap">
  <Link
    href="/about-us"
    className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-200 transition duration-300 hover:-translate-y-1 hover:scale-[1.03] hover:bg-[#245fcd]"
  >
    Discover Our Story
  </Link>

  <Link
    href="/contact-us"
    className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl border border-blue-200 bg-white px-6 py-3 text-sm font-semibold text-primary transition duration-300 hover:-translate-y-1 hover:scale-[1.03] hover:bg-blue-50"
  >
    Visit or Contact Us
  </Link>
</div>
        </div>

        <div className="welcome-visual relative z-10">
          <div className="welcome-float-shape absolute -left-8 top-8 hidden h-24 w-24 rounded-full border border-blue-200/80 bg-white/80 blur-[1px] lg:block" />
          <div className="welcome-float-shape-delayed absolute -right-5 -top-5 hidden h-32 w-32 rounded-full bg-blue-200/70 blur-2xl lg:block" />

          <div className="welcome-frame relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-white via-blue-50 to-blue-100 p-[8px] shadow-[0_25px_70px_rgba(37,99,235,0.18)]">
            <div className="welcome-shimmer pointer-events-none absolute inset-0 z-10" />

            <div className="relative overflow-hidden rounded-[1.7rem] border border-white/70 bg-white">
              <Image
                src={getMediaUrl(homePage.welcome_image, fallbackImages.gallery)}
                alt={welcomeTitle}
                width={900}
                height={700}
                className={`welcome-image w-full object-cover object-top ${
                  hasWelcomeImage ? "h-[360px] md:h-[480px]" : "h-72"
                }`}
              />

              <div className="welcome-image-overlay pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/35 via-slate-900/10 to-white/10" />
              <div className="pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-white/30 to-transparent" />

              <div className="welcome-pill absolute left-5 top-5 rounded-full border border-white/60 bg-white/88 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-primary shadow-lg backdrop-blur-md">
                Leadership & Vision
              </div>

              <div className="absolute bottom-5 left-5 right-5">
                <div className="welcome-caption max-w-sm rounded-2xl border border-white/30 bg-white/88 p-4 shadow-xl backdrop-blur-md">
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
                    School Principal
                  </p>
                  <p className="mt-2 text-sm font-semibold text-midnight_text md:text-base">
                    Committed to excellence, character, and future-ready education.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-300/60 to-transparent" />
    </div>
  </div>
</section>

      <HomeVideoCarousel videos={homeVideos} />
      <HomeNoticeSection notices={homeNotices} />

      <section>
        <div className="container mx-auto max-w-screen-xl px-4">
          <SectionHeading title="News & Events" subtitle="Recent stories, announcements, and school calendar highlights." />
          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <div className="mb-3 flex items-center justify-between gap-3">
                <h4 className="text-xl">Latest News</h4>
                <Link href="/news" className="text-xs font-semibold text-primary">View all</Link>
              </div>
              <div className="space-y-3">{newsItems.map((item: any) => <GenericCard key={item.id} item={item} hrefBase="/news" />)}</div>
            </div>
            <div>
              <div className="mb-3 flex items-center justify-between gap-3">
                <h4 className="text-xl">Upcoming Events</h4>
                <Link href="/events" className="text-xs font-semibold text-primary">View all</Link>
              </div>
              <div className="space-y-3">{eventItems.map((item: any) => <GenericCard key={item.id} item={item} hrefBase="/events" />)}</div>
            </div>
          </div>
        </div>
      </section>



      <section>
        <div className="container mx-auto max-w-screen-xl space-y-12 px-4">
          <div>
            <SectionHeading title="Courses" subtitle="Discover programs built for future-ready learners." />
            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{courseItems.length ? courseItems.map((item: any) => <GenericCard key={item.id} item={item} hrefBase="/courses" />) : <EmptyState message="Courses are currently unavailable." />}</div>
          </div>
          
          
          <TestimonialsSection items={displayTestimonials} />
          
          <div className="rounded-2xl bg-primary p-8 text-center text-white">
            <h3 className="!text-2xl !text-white">Begin your journey with {fallbackText.schoolName}</h3>
            <p className="mt-3 text-blue-100">Admissions are open for new students across multiple forms and programs.</p>
            <div className="mt-6 flex justify-center gap-3">
              <ApplyNowButton className="rounded-lg bg-white px-5 py-3 font-semibold text-primary transition hover:bg-blue-50" />
              <Link href="/contact-us" className="rounded-lg border border-white px-5 py-3 font-semibold text-white transition hover:bg-white/10">Contact Us</Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
