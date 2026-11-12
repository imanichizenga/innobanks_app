import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { asArray, fetchAPI, getMediaUrl } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { buildMetadata, toAbsoluteUrl } from "@/lib/seo";
import { SITE_NAME } from "@/lib/site";
import ContactUtilityActions from "@/app/components/school/ContactUtilityActions";

interface ContactPageData {
  id?: number;
  title?: string;
  subtitle?: string;
  description?: string;
  hero_image?: string;
  banner_title?: string;
  banner_description?: string;
  office_hours?: string;
  map_embed_link?: string;
  meta_title?: string;
  meta_description?: string;
  is_active?: boolean;
}

interface ContactInfoCardData {
  id?: number;
  title?: string;
  value?: string;
  icon_image?: string;
  order?: number;
  is_active?: boolean;
}

interface ContactOfficeData {
  id?: number;
  name?: string;
  address?: string;
  phone?: string;
  email?: string;
  office_hours?: string;
  map_embed_link?: string;
  image?: string;
  order?: number;
  is_active?: boolean;
}

interface SocialLinkData {
  id?: number;
  name?: string;
  url?: string;
  icon_image?: string;
  order?: number;
  is_active?: boolean;
}

const defaultTitle = "Contact Us";
const defaultSubtitle = "Reach our admissions and administration teams for support and guidance.";
const mapPlaceholder = "Map location will appear here when a Google Maps embed link is added in admin.";

const byOrder = <T extends { order?: number }>(items: T[]) =>
  [...items].sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

const getMapEmbedSrc = (value?: string | null) => {
  const raw = value?.trim();
  if (!raw) return null;

  const srcFromIframe = raw.match(/src=["']([^"']+)["']/i)?.[1];
  const candidate = srcFromIframe || raw;

  if (/^https?:\/\//i.test(candidate)) return candidate;

  return null;
};

async function getContactData() {
  const [pagesPayload, cardsPayload, officesPayload, socialsPayload] = await Promise.all([
    fetchAPI<unknown>("/contact-pages/"),
    fetchAPI<unknown>("/contact-info-cards/"),
    fetchAPI<unknown>("/contact-offices/"),
    fetchAPI<unknown>("/social-links/"),
  ]);

  const page =
    asArray<ContactPageData>(pagesPayload).find((item) => item?.is_active !== false) || asArray<ContactPageData>(pagesPayload)[0] || null;

  const cards = byOrder(asArray<ContactInfoCardData>(cardsPayload).filter((item) => item?.is_active !== false));
  const offices = byOrder(asArray<ContactOfficeData>(officesPayload).filter((item) => item?.is_active !== false));
  const socials = byOrder(asArray<SocialLinkData>(socialsPayload).filter((item) => item?.is_active !== false));

  return { page, cards, offices, socials };
}

export async function generateMetadata(): Promise<Metadata> {
  const { page } = await getContactData();

  return buildMetadata({
    title: page?.meta_title?.trim() || page?.title?.trim() || defaultTitle,
    description: page?.meta_description?.trim() || page?.description?.trim() || defaultSubtitle,
    path: "/contact-us",
    image: getMediaUrl(page?.hero_image, fallbackImages.heroAlt),
  });
}

export default async function ContactPage() {
  const { page, cards, offices, socials } = await getContactData();
  const globalMap = getMapEmbedSrc(page?.map_embed_link);
  const organizationJsonLd = {
    "@context": "https://schema.org",
    "@type": "EducationalOrganization",
    name: SITE_NAME,
    url: toAbsoluteUrl("/"),
    description: page?.description?.trim() || defaultSubtitle,
    telephone: offices.find((office) => office.phone?.trim())?.phone || undefined,
    email: offices.find((office) => office.email?.trim())?.email || undefined,
    address: offices[0]?.address?.trim()
      ? {
          "@type": "PostalAddress",
          streetAddress: offices[0].address,
        }
      : undefined,
    sameAs: socials.map((social) => social.url?.trim()).filter(Boolean),
  };

  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }} />
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

          {page?.office_hours?.trim() ? (
            <div className="rounded-xl border border-blue-100 bg-blue-50/70 p-4 text-sm text-midnight_text">
              <span className="font-semibold">General office hours:</span> {page.office_hours}
            </div>
          ) : null}

          <div className="flex flex-wrap items-center gap-3 rounded-xl border border-blue-100 bg-white p-4 text-sm">
            <span className="font-semibold text-midnight_text">Admissions enquiries:</span>
            <Link href="/admission" className="rounded-md bg-primary px-3 py-2 text-xs font-semibold text-white transition hover:bg-blue-700">Start Application</Link>
            <Link href="/contact-us" className="rounded-md border border-blue-100 px-3 py-2 text-xs font-semibold text-primary transition hover:bg-blue-50">Talk to Admissions</Link>
          </div>

          {cards.length ? (
            <div className="grid gap-4 md:grid-cols-3">
              {cards.map((card) => (
  <div
    key={card.id || `${card.title}-${card.order}`}
    className="overflow-hidden rounded-xl border border-blue-100 bg-white shadow-sm transition hover:shadow-md"
  >
    {/* ✅ TOP IMAGE (LIKE GALLERY) */}
    <div className="relative h-[180px] w-full overflow-hidden">
      {card.icon_image ? (
        <Image
          src={getMediaUrl(card.icon_image, fallbackImages.card)}
          alt={card.title || "card image"}
          fill
          className="object-cover"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-primary/10 text-4xl font-bold text-primary">
          {(card.title?.[0] || "•").toUpperCase()}
        </div>
      )}
    </div>

    {/* ✅ CONTENT */}
    <div className="p-4">
      <h4 className="!text-lg font-semibold">
        {card.title || "Contact"}
      </h4>

      <p className="mt-2 text-sm text-gray">
        {card.value || "Information unavailable."}
      </p>
    </div>
  </div>
))}
            </div>
          ) : (
            <EmptyState message="Contact information cards are not available yet." />
          )}

          <div className="rounded-xl border border-blue-100 bg-white p-4">
            <h4 className="mb-2 !text-lg">Main Location Map</h4>
            {globalMap ? (
              <iframe
                src={globalMap}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                className="h-[380px] w-full rounded-lg"
                title="School location map"
              />
            ) : (
              <p className="text-sm text-gray">{mapPlaceholder}</p>
            )}
            <p className="mt-3 text-xs text-gray">
              Admin helper: use the Google Maps <span className="font-semibold">Embed a map</span> URL (iframe <span className="font-semibold">src</span> value).
            </p>
          </div>

          {offices.length ? (
            <div className="space-y-4">
              {offices.map((office) => {
                const officeMap = getMapEmbedSrc(office.map_embed_link);
                return (
                  <article key={office.id || `${office.name}-${office.order}`} className="rounded-xl border border-blue-100 bg-section p-5">
                    <div className="grid gap-5 lg:grid-cols-3">
                      <div>
                        <h4 className="!text-lg">{office.name || "Office"}</h4>
                        <p className="mt-2 text-sm text-gray">{office.address || "Address will be updated soon."}</p>
                        {office.office_hours?.trim() ? <p className="mt-2 text-sm text-gray">Hours: {office.office_hours}</p> : null}
                        {office.email?.trim() ? (
                          <p className="mt-2 text-sm">
                            <Link href={`mailto:${office.email}`} className="text-primary underline">
                              {office.email}
                            </Link>
                          </p>
                        ) : null}
                        {office.phone?.trim() ? (
                          <p className="mt-1 text-sm">
                            <Link href={`tel:${office.phone}`} className="text-primary underline">
                              {office.phone}
                            </Link>
                          </p>
                        ) : null}
                        <ContactUtilityActions phone={office.phone} email={office.email} />
                      </div>

                      <div className="relative min-h-[180px] overflow-hidden rounded-lg border border-blue-100 bg-white">
                        <Image
                          src={getMediaUrl(office.image, fallbackImages.card)}
                          alt={office.name || "Office image"}
                          fill
                          className="object-cover"
                        />
                      </div>

                      <div className="rounded-lg border border-blue-100 bg-white p-3">
                        {officeMap ? (
                          <iframe
                            src={officeMap}
                            loading="lazy"
                            referrerPolicy="no-referrer-when-downgrade"
                            className="h-[180px] w-full rounded"
                            title={`${office.name || "Office"} map`}
                          />
                        ) : (
                          <p className="text-sm text-gray">Map link pending for this office.</p>
                        )}
                        <p className="mt-2 text-xs text-gray">Use Google Maps embed src URL for this office map field.</p>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <EmptyState message="Office locations are not available yet." />
          )}

          <div>
            <h4 className="mb-3 text-xl">Connect with us</h4>
            {socials.length ? (
              <div className="flex flex-wrap gap-3">
                {socials.map((social) => (
                  <a
                    key={social.id || `${social.name}-${social.order}`}
                    href={social.url || "#"}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-md border border-blue-100 bg-white px-3 py-2 text-sm text-midnight_text transition hover:border-primary"
                    aria-label={social.name || "Social link"}
                  >
                    {social.icon_image ? (
                      <Image
                        src={getMediaUrl(social.icon_image, fallbackImages.logo)}
                        alt={social.name || "social icon"}
                        width={18}
                        height={18}
                        className="h-[18px] w-[18px] object-contain"
                      />
                    ) : (
                      <span className="inline-flex h-[18px] w-[18px] items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary">
                        {(social.name?.trim()?.[0] || "S").toUpperCase()}
                      </span>
                    )}
                    <span>{social.name || "Social"}</span>
                  </a>
                ))}
              </div>
            ) : (
              <EmptyState message="Social links are not available yet." />
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
