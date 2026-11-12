"use client";

import Image from "next/image";
import { useMemo, useState } from "react";
import { fallbackImages } from "@/lib/fallbacks";
import { extractMediaPath, getMediaUrl } from "@/lib/api";

interface GalleryItem {
  image?: unknown;
  title?: string | null;
  caption?: string | null;
  id?: number;
  category?: unknown;
}

type NormalizedCategory = {
  key: string;
  label: string;
} | null;

const CATEGORY_KEYS = ["title", "name", "label", "category", "value", "text"];

function toHumanLabel(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function readCategoryCandidate(value: unknown, depth = 0): string | null {
  if (depth > 2 || value === null || value === undefined) return null;

  if (typeof value === "string") {
    const cleaned = value.replace(/\s+/g, " ").trim();
    return cleaned || null;
  }

  if (typeof value === "number" || typeof value === "bigint") {
    return String(value);
  }

  if (typeof value === "object") {
    if (Array.isArray(value)) {
      for (const entry of value) {
        const nested = readCategoryCandidate(entry, depth + 1);
        if (nested) return nested;
      }
      return null;
    }

    const objectValue = value as Record<string, unknown>;
    for (const key of CATEGORY_KEYS) {
      if (key in objectValue) {
        const nested = readCategoryCandidate(objectValue[key], depth + 1);
        if (nested) return nested;
      }
    }
  }

  return null;
}

function normalizeCategory(value: unknown): NormalizedCategory {
  const candidate = readCategoryCandidate(value);
  if (!candidate) return null;

  const key = candidate.toLocaleLowerCase().replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim();
  if (!key) return null;

  return {
    key,
    label: toHumanLabel(candidate),
  };
}

export default function ImageGallery({ items }: { items: GalleryItem[] }) {
  const [activeCategory, setActiveCategory] = useState("all");
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showAll, setShowAll] = useState(false);

  const normalizedItems = useMemo(
    () =>
      items.map((item) => {
        const normalized = normalizeCategory(item.category);
        return {
          ...item,
          _categoryKey: normalized?.key || null,
          _categoryLabel: normalized?.label || null,
        };
      }),
    [items],
  );

  const categories = useMemo(() => {
    const deduped = new Map<string, string>();
    normalizedItems.forEach((item) => {
      if (item._categoryKey && item._categoryLabel && !deduped.has(item._categoryKey)) {
        deduped.set(item._categoryKey, item._categoryLabel);
      }
    });

    return [{ key: "all", label: "All" }, ...Array.from(deduped.entries()).map(([key, label]) => ({ key, label }))];
  }, [normalizedItems]);

  const filtered = useMemo(() => {
    const base =
      activeCategory === "all"
        ? normalizedItems
        : normalizedItems.filter((item) => item._categoryKey === activeCategory);
    return showAll ? base : base.slice(0, 10);
  }, [normalizedItems, activeCategory, showAll]);

  const selected = selectedIndex === null ? null : filtered[selectedIndex];

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center gap-2">
        {categories.map((category) => (
          <button
            key={category.key}
            type="button"
            onClick={() => {
              setActiveCategory(category.key);
              setSelectedIndex(null);
              setShowAll(false);
            }}
            className={`rounded-full border px-3 py-1 text-xs font-semibold transition ${
              activeCategory === category.key
                ? "border-primary bg-primary text-white"
                : "border-blue-100 bg-white text-midnight_text hover:border-primary/40"
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((item, i) => {
          const hasImage = Boolean(extractMediaPath(item.image));

          return (
            <button
              key={item.id || i}
              className="group overflow-hidden rounded-2xl border border-blue-100 bg-white text-left shadow-sm transition hover:-translate-y-1 hover:shadow-property"
              onClick={() => setSelectedIndex(i)}
            >
              <div className="relative h-56 w-full overflow-hidden bg-blue-50 sm:h-60 md:h-64">
                {hasImage ? (
                  <Image
                    src={getMediaUrl(item.image, fallbackImages.gallery)}
                    alt={item.title?.trim() || "Gallery image"}
                    fill
                    className="object-cover transition duration-500 group-hover:scale-105"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 p-4 text-center">
                    <p className="text-xs font-medium text-gray">Image will be updated soon</p>
                  </div>
                )}
              </div>

              {(item.title?.trim() || item.caption?.trim()) && (
                <div className="p-4">
                  {item.title?.trim() ? (
                    <h4 className="line-clamp-1 text-sm font-semibold text-midnight_text">{item.title}</h4>
                  ) : null}
                  {item.caption?.trim() ? (
                    <p className="mt-2 line-clamp-2 text-xs text-gray">{item.caption}</p>
                  ) : null}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {filtered.length === 0 ? <p className="mt-4 text-sm text-gray">No images found for this category yet.</p> : null}

      {(activeCategory === "all"
        ? normalizedItems.length
        : normalizedItems.filter((i) => i._categoryKey === activeCategory).length) > 10 ? (
        <div className="mt-5 text-center">
          <button
            type="button"
            className="rounded-lg border border-blue-100 px-4 py-2 text-sm font-semibold text-primary transition hover:bg-blue-50"
            onClick={() => setShowAll((v) => !v)}
          >
            {showAll ? "Show less" : "View all photos"}
          </button>
        </div>
      ) : null}

      {selected ? (
        <div className="fixed inset-0 z-[170] bg-black/70 p-4" onClick={() => setSelectedIndex(null)}>
          <div className="mx-auto mt-8 max-w-4xl rounded-xl bg-white p-3" onClick={(e) => e.stopPropagation()}>
            <Image
              src={getMediaUrl(selected.image, fallbackImages.gallery)}
              alt={selected.title?.trim() || "Preview"}
              width={1400}
              height={850}
              className="max-h-[72vh] w-full rounded-lg object-cover"
            />
            {(selected.title?.trim() || selected.caption?.trim()) ? (
              <p className="px-1 pt-3 text-sm text-gray">{selected.title || selected.caption}</p>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}