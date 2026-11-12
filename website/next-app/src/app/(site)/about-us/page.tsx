import type { Metadata } from "next";
import Image from "next/image";
import { asArray, fetchAPI, getMediaUrl } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import { GenericCard } from "@/app/components/school/cards";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { buildMetadata, toAbsoluteUrl } from "@/lib/seo";
import { SITE_NAME } from "@/lib/site";

interface AboutPageData {
  id?: number;
  title?: string;
  subtitle?: string;
  description?: string;
  hero_image?: string;
  mission?: string;
  vision?: string;
  core_values?: string;
  meta_title?: string;
  meta_description?: string;
  is_active?: boolean;
}

interface AboutMenuItemData {
  id?: number;
  title?: string;
  slug?: string;
  short_description?: string;
  image?: string;
  order?: number;
  is_active?: boolean;
}

interface LeadershipMemberData {
  id?: number;
  full_name?: string;
  role?: string;
  image?: string;
  email?: string;
  phone?: string;
  order?: number;
  is_active?: boolean;
}

const defaultTitle = "About Us";
const defaultSubtitle = "Mission, vision and leadership that shape our school community.";

const byOrder = <T extends { order?: number }>(items: T[]) =>
  [...items].sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

async function getAboutData() {
  const [pagesPayload, menusPayload, leadersPayload] = await Promise.all([
    fetchAPI<unknown>("/about-pages/"),
    fetchAPI<unknown>("/about-menu-items/"),
    fetchAPI<unknown>("/leadership-members/"),
  ]);

  const page =
    asArray<AboutPageData>(pagesPayload).find((item) => item?.is_active !== false) || asArray<AboutPageData>(pagesPayload)[0] || null;

  const menuItems = byOrder(asArray<AboutMenuItemData>(menusPayload).filter((item) => item?.is_active !== false));
  const leaders = byOrder(asArray<LeadershipMemberData>(leadersPayload).filter((item) => item?.is_active !== false));

  return { page, menuItems, leaders };
}

export async function generateMetadata(): Promise<Metadata> {
  const { page } = await getAboutData();

  return buildMetadata({
    title: page?.meta_title?.trim() || page?.title?.trim() || defaultTitle,
    description: page?.meta_description?.trim() || page?.description?.trim() || defaultSubtitle,
    path: "/about-us",
    image: getMediaUrl(page?.hero_image, fallbackImages.heroAlt),
  });
}

export default async function AboutPage() {
  const { page, menuItems, leaders } = await getAboutData();
  const organizationJsonLd = {
    "@context": "https://schema.org",
    "@type": "EducationalOrganization",
    name: SITE_NAME,
    url: toAbsoluteUrl("/"),
    description: page?.description?.trim() || defaultSubtitle,
    slogan: page?.subtitle?.trim() || undefined,
  };

  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }} />
      <section className="relative !py-0">
        <div className="relative h-[38vh] min-h-[260px] overflow-hidden">
          <Image src={getMediaUrl(page?.hero_image, fallbackImages.heroAlt)} alt={page?.title || defaultTitle} fill priority className="object-cover" />
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
          <SectionHeading title={page?.title?.trim() || defaultTitle} subtitle={page?.description?.trim() || defaultSubtitle} />

          {(page?.mission?.trim() || page?.vision?.trim() || page?.core_values?.trim()) && (
            <div className="grid gap-4 md:grid-cols-3">
              {page?.mission?.trim() ? (
                <article className="rounded-xl border border-blue-100 bg-white p-5">
                  <h3 className="mb-2 !text-lg !text-midnight_text">Mission</h3>
                  <p className="text-sm text-gray">{page.mission}</p>
                </article>
              ) : null}
              {page?.vision?.trim() ? (
                <article className="rounded-xl border border-blue-100 bg-white p-5">
                  <h3 className="mb-2 !text-lg !text-midnight_text">Vision</h3>
                  <p className="text-sm text-gray">{page.vision}</p>
                </article>
              ) : null}
              {page?.core_values?.trim() ? (
                <article className="rounded-xl border border-blue-100 bg-white p-5">
                  <h3 className="mb-2 !text-lg !text-midnight_text">Core Values</h3>
                  <p className="text-sm text-gray">{page.core_values}</p>
                </article>
              ) : null}
            </div>
          )}

          {menuItems.length ? (
            <div className="grid gap-5 md:grid-cols-2">
              {menuItems.map((item) => (
                <GenericCard key={item.id || item.slug || item.title} item={item} hrefBase="/about-us" />
              ))}
            </div>
          ) : (
            <EmptyState message="About menu items are not available yet." />
          )}

          <div>
            <h4 className="mb-4 text-xl">Leadership Team</h4>
            {leaders.length ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {leaders.map((member) => (
                  <div key={member.id || `${member.full_name}-${member.order}`} className="rounded-xl border border-blue-100 bg-white p-4 text-center">
                    <Image
                      src={getMediaUrl(member.image, fallbackImages.avatar)}
                      alt={member.full_name || "Leadership member"}
                      width={100}
                      height={100}
                      className="mx-auto mb-3 h-24 w-24 rounded-full object-cover"
                    />
                    <p className="font-semibold text-midnight_text">{member.full_name || "Staff Member"}</p>
                    <p className="text-xs text-gray">{member.role || "Leadership"}</p>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message="Leadership profiles are not available yet." />
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
