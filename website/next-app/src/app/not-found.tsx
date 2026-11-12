import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";

export const metadata: Metadata = buildMetadata({
  title: "Page Not Found",
  description: "The page you are looking for does not exist or may have moved.",
  path: "/404",
  noIndex: true,
});

export default function NotFoundPage() {
  return (
    <main>
      <section>
        <div className="container mx-auto max-w-screen-xl px-4 py-20 text-center">
          <p className="mb-3 inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
            404 Error
          </p>
          <h1 className="!text-midnight_text">Page not found</h1>
          <p className="mx-auto mt-3 max-w-xl text-gray">
            Sorry, we couldn&apos;t find that page. It may have been removed or the URL may be incorrect.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link href="/" className="rounded-lg bg-primary px-5 py-3 font-semibold text-white transition hover:bg-blue-700">
              Go to Home
            </Link>
            <Link href="/contact-us" className="rounded-lg border border-blue-200 px-5 py-3 font-semibold text-primary transition hover:bg-blue-50">
              Contact Admissions
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
