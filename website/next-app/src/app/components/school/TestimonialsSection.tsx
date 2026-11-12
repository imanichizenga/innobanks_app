"use client";

import Image from "next/image";
import { useMemo, useState } from "react";
import { fallbackImages } from "@/lib/fallbacks";
import { extractMediaPath, getMediaUrl } from "@/lib/api";

type TestimonialItem = {
  id?: number;
  message: string;
  full_name: string;
  role: string;
  rating?: number;
  image?: unknown;
};

type SubmissionState = "idle" | "submitting" | "success" | "error";

const SUBMIT_ENDPOINT = "/api/home-testimonials/";

const clampRating = (value?: number) => Math.max(1, Math.min(5, Math.round(value || 5)));

export default function TestimonialsSection({ items }: { items: TestimonialItem[] }) {
  const [showAll, setShowAll] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [status, setStatus] = useState<SubmissionState>("idle");
  const [errorText, setErrorText] = useState("");
  const [form, setForm] = useState({
    full_name: "",
    role: "",
    rating: "5",
    message: "",
  });
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const displayItems = useMemo(() => (showAll ? items : items.slice(0, 6)), [items, showAll]);

  const submitStory = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.full_name.trim() || !form.message.trim()) {
      setStatus("error");
      setErrorText("Please enter your name and story message.");
      return;
    }

    setStatus("submitting");
    setErrorText("");

    try {
      const payload = new FormData();
      payload.append("full_name", form.full_name.trim());
      payload.append("role", form.role.trim());
      payload.append("rating", String(clampRating(Number(form.rating))));
      payload.append("message", form.message.trim());
      if (selectedImage) payload.append("image", selectedImage);

      const res = await fetch(SUBMIT_ENDPOINT, {
        method: "POST",
        body: payload,
      });

      if (!res.ok) {
        let detail = "Failed to submit";
        try {
          const data = await res.json();
          if (typeof data?.error === "string") {
            detail = data.error;
          } else if (typeof data?.detail === "string") {
            detail = data.detail;
          } else if (data && typeof data === "object") {
            const firstFieldError = Object.values(data).find((value) =>
              Array.isArray(value) ? Boolean(value[0]) : typeof value === "string",
            );
            if (Array.isArray(firstFieldError) && typeof firstFieldError[0] === "string") {
              detail = firstFieldError[0];
            } else if (typeof firstFieldError === "string") {
              detail = firstFieldError;
            }
          }
        } catch {
          // ignore JSON parse errors and fall back to generic message
        }
        throw new Error(detail);
      }

      setStatus("success");
      setForm({ full_name: "", role: "", rating: "5", message: "" });
      setSelectedImage(null);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
      setTimeout(() => {
        setOpenModal(false);
        setStatus("idle");
      }, 1500);
    } catch (error) {
      setStatus("error");
      const defaultMessage = "We could not submit your story right now. Please try again shortly.";
      if (process.env.NODE_ENV !== "production" && error instanceof Error && error.message.trim()) {
        setErrorText(`${defaultMessage} (${error.message.trim()})`);
      } else {
        setErrorText(defaultMessage);
      }
    }
  };

  return (
    <section>
      <div className="container mx-auto max-w-screen-xl px-4">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h3 className="!text-2xl !text-midnight_text">Student & Parent Stories</h3>
            <p className="mt-2 max-w-3xl text-sm text-gray">Authentic voices from our school community.</p>
          </div>
          <button
            type="button"
            onClick={() => {
              setOpenModal(true);
              setStatus("idle");
              setErrorText("");
              setSelectedImage(null);
              if (previewUrl) URL.revokeObjectURL(previewUrl);
              setPreviewUrl(null);
            }}
            className="rounded-lg border border-primary px-4 py-2 text-sm font-semibold text-primary transition hover:bg-blue-50"
          >
            Share Your Story
          </button>
        </div>

        {items.length ? (
          <>
            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {displayItems.map((item, idx) => (
                <article key={`${item.full_name}-${item.id || idx}`} className="flex h-full flex-col rounded-xl border border-blue-100 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:shadow-property">
                  <p className="text-sm leading-7 text-gray">“{item.message}”</p>
                  <div className="mt-4 flex items-center gap-3">
                    <Image
                      src={getMediaUrl(item.image, fallbackImages.avatar)}
                      alt={item.full_name}
                      width={56}
                      height={56}
                      className={`h-12 w-12 object-cover ${extractMediaPath(item.image) ? "rounded-lg" : "rounded-full"}`}
                    />
                    <div>
                      <p className="text-sm font-semibold text-midnight_text">{item.full_name}</p>
                      <p className="text-xs text-gray">{item.role || "School Community"}</p>
                    </div>
                  </div>
                  {item.rating ? <p className="mt-3 text-xs text-amber-600">{"★".repeat(clampRating(item.rating))}</p> : null}
                </article>
              ))}
            </div>

            {items.length > 6 ? (
              <div className="mt-5 text-center">
                <button
                  type="button"
                  onClick={() => setShowAll((v) => !v)}
                  className="rounded-lg border border-blue-100 px-4 py-2 text-sm font-semibold text-primary transition hover:bg-blue-50"
                >
                  {showAll ? "Show fewer stories" : `View all ${items.length} stories`}
                </button>
              </div>
            ) : null}
          </>
        ) : (
          <div className="mt-5 rounded-xl border border-blue-100 bg-white p-5 text-sm text-gray">
            No approved stories are published yet. Be the first to share your experience.
          </div>
        )}
      </div>

      {openModal ? (
        <div className="fixed inset-0 z-[180] bg-black/50 p-4" onClick={() => status !== "submitting" && setOpenModal(false)}>
          <div className="mx-auto mt-10 w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h4 className="!text-xl !text-midnight_text">Share your story</h4>
            <p className="mt-1 text-sm text-gray">Your story is reviewed by our team and appears after admin approval.</p>

            <form className="mt-5 space-y-4" onSubmit={submitStory}>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm((prev) => ({ ...prev, full_name: e.target.value }))}
                placeholder="Full name"
                className="w-full rounded-lg border border-blue-100 px-4 py-2 text-sm outline-none transition focus:border-primary"
                maxLength={255}
                required
              />
              <input
                type="text"
                value={form.role}
                onChange={(e) => setForm((prev) => ({ ...prev, role: e.target.value }))}
                placeholder="Role (Student, Parent, Alumni, Guardian...)"
                className="w-full rounded-lg border border-blue-100 px-4 py-2 text-sm outline-none transition focus:border-primary"
                maxLength={100}
              />
              <select
                value={form.rating}
                onChange={(e) => setForm((prev) => ({ ...prev, rating: e.target.value }))}
                className="w-full rounded-lg border border-blue-100 px-4 py-2 text-sm outline-none transition focus:border-primary"
              >
                {[5, 4, 3, 2, 1].map((value) => (
                  <option key={value} value={value}>{value} star{value > 1 ? "s" : ""}</option>
                ))}
              </select>
              <textarea
                value={form.message}
                onChange={(e) => setForm((prev) => ({ ...prev, message: e.target.value }))}
                placeholder="Write your experience..."
                rows={5}
                className="w-full rounded-lg border border-blue-100 px-4 py-2 text-sm outline-none transition focus:border-primary"
                required
              />
              <div>
                <label className="mb-1 block text-sm font-medium text-midnight_text">Photo (optional)</label>
                <input
                  type="file"
                  accept="image/*"
                  className="w-full rounded-lg border border-blue-100 px-3 py-2 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-1 file:text-xs file:font-semibold file:text-primary hover:file:bg-blue-100"
                  onChange={(e) => {
                    const file = e.target.files?.[0] || null;
                    setSelectedImage(file);
                    if (previewUrl) URL.revokeObjectURL(previewUrl);
                    setPreviewUrl(file ? URL.createObjectURL(file) : null);
                  }}
                />
                {previewUrl ? (
                  <div className="mt-3 flex items-center gap-3 rounded-lg border border-blue-100 bg-blue-50/40 p-2">
                    <Image src={previewUrl} alt="Selected preview" width={64} height={64} className="h-14 w-14 rounded-lg object-cover" unoptimized />
                    <p className="text-xs text-gray">Selected image will be sent with your story for admin review.</p>
                  </div>
                ) : null}
              </div>

              {status === "error" ? <p className="text-sm text-red-600">{errorText}</p> : null}
              {status === "success" ? <p className="text-sm text-green-600">Thank you! Your story was submitted for approval.</p> : null}

              <div className="flex flex-wrap gap-3">
                <button
                  type="submit"
                  disabled={status === "submitting"}
                  className="rounded-lg bg-primary px-5 py-2 text-sm font-semibold text-white transition hover:bg-[#245fcd] disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {status === "submitting" ? "Submitting..." : "Submit Story"}
                </button>
                <button
                  type="button"
                  disabled={status === "submitting"}
                  onClick={() => {
                    setOpenModal(false);
                    setSelectedImage(null);
                    if (previewUrl) URL.revokeObjectURL(previewUrl);
                    setPreviewUrl(null);
                  }}
                  className="rounded-lg border border-blue-100 px-5 py-2 text-sm font-semibold text-primary transition hover:bg-blue-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </section>
  );
}
