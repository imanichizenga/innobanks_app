"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { fallbackImages } from "@/lib/fallbacks";
import { schoolNav } from "@/lib/navigation";
import ApplyNowButton from "@/app/components/school/ApplyNowButton";

const Chevron = ({ open = false }: { open?: boolean }) => (
  <svg className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
    <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const Header = () => {
  const pathname = usePathname();
  const [open, setOpen] = useState<string | null>(null);
  const closeTimerRef = useRef<number | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileDropdownOpen, setMobileDropdownOpen] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 8);
    handleScroll();
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setOpen(null);
    setMobileDropdownOpen(null);
    setMobileOpen(false);
  }, [pathname]);

  const cancelScheduledClose = () => {
    if (closeTimerRef.current) {
      window.clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }
  };

  const scheduleClose = () => {
    cancelScheduledClose();
    closeTimerRef.current = window.setTimeout(() => setOpen(null), 140);
  };

  return (
    <header className={`fixed left-0 right-0 top-0 z-[100] border-b border-blue-100 bg-white ${scrolled ? "shadow-lg" : "shadow-sm"}`}>
      <div className="container mx-auto flex max-w-screen-xl items-center justify-between px-4 py-4">
        <Link href="/" className="flex items-center gap-3">
          <Image src={fallbackImages.logo} alt="School logo" width={42} height={42} />
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-primary">The British</p>
            <p className="text-sm font-semibold text-midnight_text">Opening School</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-4 lg:flex">
          {schoolNav.map((item) => {
            const isOpen = open === item.label;
            const hasChildren = Boolean(item.children?.length);
            const parentHref = item.href || "#";
            const isParentActive = pathname === parentHref || pathname.startsWith(`${parentHref}/`);
            const homeLabel = `${item.label} Home`;
            const menuChildren = hasChildren
              ? [{ label: homeLabel, href: parentHref }, ...(item.children || [])]
              : [];

            return (
              <div
                className="relative"
                key={item.label}
                onMouseEnter={() => {
                  if (!hasChildren) return;
                  cancelScheduledClose();
                  setOpen(item.label);
                }}
                onMouseLeave={() => {
                  if (hasChildren) scheduleClose();
                }}
              >
                {hasChildren ? (
                  <div className="flex items-stretch rounded-md border border-transparent bg-transparent transition hover:border-blue-100 hover:bg-blue-50/80 focus-within:border-blue-100 focus-within:bg-blue-50/80">
                    <Link
                      href={parentHref}
                      className={`flex items-center px-3 py-3 text-sm font-medium transition hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 ${isParentActive ? "text-primary" : "text-midnight_text"}`}
                    >
                      {item.label}
                    </Link>
                    <button
                      type="button"
                      className={`flex items-center px-2 py-3 text-midnight_text transition hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 ${isOpen ? "text-primary" : ""}`}
                      aria-expanded={isOpen}
                      aria-haspopup="menu"
                      aria-label={`Toggle ${item.label} submenu`}
                      onClick={() => {
                        cancelScheduledClose();
                        setOpen((prev) => (prev === item.label ? null : item.label));
                      }}
                      onKeyDown={(event) => {
                        if (event.key === "Escape") setOpen(null);
                      }}
                    >
                      <Chevron open={isOpen} />
                    </button>
                  </div>
                ) : (
                  <Link
                    href={parentHref}
                    className={`block rounded-md px-3 py-3 text-sm font-medium transition hover:bg-blue-50 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 ${pathname === parentHref ? "text-primary" : "text-midnight_text"}`}
                  >
                    {item.label}
                  </Link>
                )}

                {hasChildren ? <div className="absolute left-0 top-full h-3 w-full" aria-hidden /> : null}

                {hasChildren && isOpen && (
                  <div
                    className="absolute left-0 top-full z-[140] mt-2 w-64 rounded-lg border border-blue-100 bg-white p-2 shadow-property"
                    onMouseEnter={cancelScheduledClose}
                    onMouseLeave={scheduleClose}
                    role="menu"
                    aria-label={`${item.label} submenu`}
                  >
                    {menuChildren.map((child) => (
                      <Link
                        key={`${item.label}-${child.href}`}
                        href={child.href}
                        className={`block rounded-md px-3 py-2 text-sm transition hover:bg-blue-50 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 ${pathname === child.href ? "bg-blue-50 text-primary" : "text-gray"}`}
                        onClick={() => setOpen(null)}
                      >
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        <div className="flex items-center gap-2 sm:gap-3">
          <ApplyNowButton className="hidden rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white lg:inline-block" />
          <button
            className="rounded border border-blue-100 p-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 lg:hidden"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            <span className="block h-0.5 w-6 bg-midnight_text" />
            <span className="mt-1 block h-0.5 w-6 bg-midnight_text" />
            <span className="mt-1 block h-0.5 w-6 bg-midnight_text" />
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="border-t border-blue-100 bg-white p-4 shadow-lg lg:hidden">
          {schoolNav.map((item) => {
            const hasChildren = Boolean(item.children?.length);
            const isOpen = mobileDropdownOpen === item.label;
            const parentHref = item.href || "#";
            const mobileChildren = hasChildren
              ? [{ label: `${item.label} Home`, href: parentHref }, ...(item.children || [])]
              : [];

            return (
              <div key={item.label} className="mb-2 rounded-lg border border-blue-50">
                <div className="flex items-center justify-between px-3 py-2">
                  <Link
                    href={parentHref}
                    className={`min-h-11 flex-1 py-1 font-medium ${pathname === parentHref ? "text-primary" : "text-midnight_text"}`}
                    onClick={() => setMobileOpen(false)}
                  >
                    {item.label}
                  </Link>
                  {hasChildren ? (
                    <button
                      type="button"
                      className="min-h-11 rounded px-2 text-midnight_text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
                      onClick={() => setMobileDropdownOpen((prev) => (prev === item.label ? null : item.label))}
                      aria-expanded={isOpen}
                      aria-label={`Toggle ${item.label} submenu`}
                    >
                      <Chevron open={isOpen} />
                    </button>
                  ) : null}
                </div>
                {hasChildren && isOpen && (
                  <div className="mx-3 mb-3 space-y-1 rounded border border-blue-100 bg-blue-50 p-2">
                    {mobileChildren.map((child) => (
                      <Link
                        key={`${item.label}-${child.href}`}
                        href={child.href}
                        className={`block rounded px-2 py-2 text-sm hover:bg-white hover:text-primary ${pathname === child.href ? "bg-white text-primary" : "text-gray"}`}
                        onClick={() => setMobileOpen(false)}
                      >
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </header>
  );
};

export default Header;
