import type { Metadata } from "next";
import Image from "next/image";
import { asArray, fetchAPI, getMediaUrl } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import { GenericCard } from "@/app/components/school/cards";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { buildMetadata } from "@/lib/seo";

interface AdmissionPageData {
  id?: number;
  title?: string;
  subtitle?: string;
  description?: string;
  hero_image?: string;
  banner_title?: string;
  banner_description?: string;
  application_notice?: string;
  meta_title?: string;
  meta_description?: string;
  is_active?: boolean;
}

interface AdmissionCategoryData {
  id?: number;
  title?: string;
  slug?: string;
  short_description?: string;
  image?: string;
  form_type?: string;
  order?: number;
  is_active?: boolean;
}

const defaultTitle = "Admissions";
const defaultSubtitle = "View entry requirements and application pathways for each level.";

async function getAdmissionData() {
  const [pagesPayload, categoriesPayload] = await Promise.all([
    fetchAPI<unknown>("/admission-pages/"),
    fetchAPI<unknown>("/admission-categories/"),
  ]);

  const page =
    asArray<AdmissionPageData>(pagesPayload).find((item) => item?.is_active !== false) ||
    asArray<AdmissionPageData>(pagesPayload)[0] ||
    null;

  const categories = asArray<AdmissionCategoryData>(categoriesPayload)
    .filter((item) => item?.is_active !== false)
    .sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

  return { page, categories };
}

export async function generateMetadata(): Promise<Metadata> {
  const { page } = await getAdmissionData();

  return buildMetadata({
    title: page?.meta_title?.trim() || page?.title?.trim() || defaultTitle,
    description: page?.meta_description?.trim() || page?.description?.trim() || defaultSubtitle,
    path: "/admission",
    image: getMediaUrl(page?.hero_image, fallbackImages.heroAlt),
  });
}

export default async function AdmissionPage() {
  const { page, categories } = await getAdmissionData();

  return (
    <main>
      <section className="relative !py-0">
        <div className="relative h-[38vh] min-h-[260px] overflow-hidden">
          <Image
            src={getMediaUrl(page?.hero_image, fallbackImages.heroAlt)}
            alt={page?.title || defaultTitle}
            fill
            priority
            className="object-cover"
          />
          <div className="absolute inset-0 bg-[#102d47]/55" />
          <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-8">
            <div>
              <h1 className="!text-white">{page?.title || defaultTitle}</h1>
              {page?.subtitle?.trim() ? <p className="mt-2 max-w-2xl text-white/90">{page.subtitle}</p> : null}
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="container mx-auto max-w-screen-xl space-y-8 px-4">
          <SectionHeading
            title={page?.banner_title?.trim() || page?.title?.trim() || defaultTitle}
            subtitle={page?.banner_description?.trim() || page?.description?.trim() || defaultSubtitle}
          />

          {page?.application_notice?.trim() ? (
            <div className="rounded-xl border border-blue-100 bg-blue-50/70 p-4 text-sm text-midnight_text">
              {page.application_notice}
            </div>
          ) : null}

          {categories.length ? (
            <div className="grid gap-5 md:grid-cols-3">
              {categories.map((item) => (
                <GenericCard key={item.id || item.slug || item.title} item={item} hrefBase="/admission" />
              ))}
            </div>
          ) : (
            <EmptyState message="Admission categories are not available yet." />
          )}
        </div>
      </section>
    </main>
  );
}
