import type { Metadata } from "next";
import "./globals.css";
import NextTopLoader from "nextjs-toploader";
import Footer from "./components/layout/footer";
import Header from "./components/layout/header";
import { AppContextProvider } from "@/context-api/PropertyContext";
import { DEFAULT_OG_IMAGE, SITE_NAME, SITE_URL } from "@/lib/site";
import MobileActionBar from "./components/school/MobileActionBar";
import EnquiryModalProvider from "./components/school/EnquiryModalProvider";
import { mobileActions } from "@/lib/siteUx";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SITE_NAME,
    template: `%s | ${SITE_NAME}`,
  },
  description:
    "A modern learning community focused on academic excellence, leadership, and student growth.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: SITE_NAME,
    description:
      "A modern learning community focused on academic excellence, leadership, and student growth.",
    url: SITE_URL,
    siteName: SITE_NAME,
    type: "website",
    locale: "en_US",
    images: [
      {
        url: DEFAULT_OG_IMAGE,
        width: 512,
        height: 512,
        alt: SITE_NAME,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_NAME,
    description:
      "A modern learning community focused on academic excellence, leadership, and student growth.",
    images: [DEFAULT_OG_IMAGE],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans pt-20 lg:pt-24">
        <AppContextProvider>
          <EnquiryModalProvider>
            <Header />
            <NextTopLoader
              color="#2F73F2"
              showSpinner={false}
              crawlSpeed={180}
              easing="ease"
              speed={220}
            />
            {children}
            <MobileActionBar
              phone="255655400420"
              whatsapp="255655400420"
              showApply={mobileActions.apply}
            />
            <Footer />
          </EnquiryModalProvider>
        </AppContextProvider>
      </body>
    </html>
  );
}