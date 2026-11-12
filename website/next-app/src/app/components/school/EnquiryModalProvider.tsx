"use client";

import { createContext, FormEvent, ReactNode, useCallback, useContext, useMemo, useState } from "react";

type FormState = {
  full_name: string;
  phone_number: string;
  email: string;
  location: string;
  description: string;
};

const initialForm: FormState = {
  full_name: "",
  phone_number: "",
  email: "",
  location: "",
  description: "",
};

type EnquiryModalContextValue = {
  openEnquiryForm: () => void;
};

const EnquiryModalContext = createContext<EnquiryModalContextValue | null>(null);

export function useEnquiryModal() {
  const context = useContext(EnquiryModalContext);
  if (!context) throw new Error("useEnquiryModal must be used within EnquiryModalProvider");
  return context;
}

export default function EnquiryModalProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [formState, setFormState] = useState<FormState>(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const closeModal = useCallback(() => {
    setIsOpen(false);
    setErrorMessage("");
    setIsSuccess(false);
  }, []);

  const validate = useCallback(() => {
    if (!formState.full_name.trim() || !formState.phone_number.trim() || !formState.email.trim()) {
      setErrorMessage("Please complete full name, phone number, and email.");
      return false;
    }

    if (!/^\S+@\S+\.\S+$/.test(formState.email.trim())) {
      setErrorMessage("Please enter a valid email address.");
      return false;
    }

    setErrorMessage("");
    return true;
  }, [formState.email, formState.full_name, formState.phone_number]);

  const handleSubmit = useCallback(
    async (event: FormEvent) => {
      event.preventDefault();
      if (!validate()) return;

      setIsSubmitting(true);
      setErrorMessage("");

      try {
        const response = await fetch("/api/home-enquiry-submissions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formState),
        });

        if (!response.ok) {
          const payload = (await response.json().catch(() => null)) as
            | { detail?: string; error?: string }
            | Record<string, string[]>
            | null;
          const fallbackMessage = "Unable to submit enquiry at the moment.";
          const message =
            payload && typeof payload === "object"
              ? "detail" in payload && typeof payload.detail === "string"
                ? payload.detail
                : "error" in payload && typeof payload.error === "string"
                  ? payload.error
                  : fallbackMessage
              : fallbackMessage;
          throw new Error(message);
        }

        setIsSuccess(true);
        setFormState(initialForm);

        setTimeout(() => {
          closeModal();
        }, 1600);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Something went wrong while submitting. Please try again shortly.");
      } finally {
        setIsSubmitting(false);
      }
    },
    [closeModal, formState, validate],
  );

  const value = useMemo(() => ({ openEnquiryForm: () => setIsOpen(true) }), []);

  return (
    <EnquiryModalContext.Provider value={value}>
      {children}
      {isOpen ? (
        <div className="fixed inset-0 z-[220] flex items-center justify-center bg-slate-900/70 p-4">
          <div className="w-full max-w-xl rounded-2xl bg-white p-5 shadow-2xl md:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h4 className="!text-xl !text-midnight_text">Enquiry Form</h4>
              <button type="button" onClick={closeModal} className="rounded-md bg-blue-50 px-3 py-1 text-sm font-semibold text-primary">
                Close
              </button>
            </div>

            {isSuccess ? (
              <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-sm font-medium text-green-700">
                Thank you. Your enquiry has been submitted successfully.
              </div>
            ) : (
              <form className="space-y-3" onSubmit={handleSubmit}>
                <input
                  value={formState.full_name}
                  onChange={(event) => setFormState((prev) => ({ ...prev, full_name: event.target.value }))}
                  type="text"
                  placeholder="Full name"
                  className="rounded-lg border border-blue-100 px-4 py-3"
                />
                <div className="grid gap-3 md:grid-cols-2">
                  <input
                    value={formState.phone_number}
                    onChange={(event) => setFormState((prev) => ({ ...prev, phone_number: event.target.value }))}
                    type="tel"
                    placeholder="Phone number"
                    className="rounded-lg border border-blue-100 px-4 py-3"
                  />
                  <input
                    value={formState.email}
                    onChange={(event) => setFormState((prev) => ({ ...prev, email: event.target.value }))}
                    type="email"
                    placeholder="Email address"
                    className="rounded-lg border border-blue-100 px-4 py-3"
                  />
                </div>
                <input
                  value={formState.location}
                  onChange={(event) => setFormState((prev) => ({ ...prev, location: event.target.value }))}
                  type="text"
                  placeholder="Location"
                  className="rounded-lg border border-blue-100 px-4 py-3"
                />
                <textarea
                  value={formState.description}
                  onChange={(event) => setFormState((prev) => ({ ...prev, description: event.target.value }))}
                  placeholder="Message"
                  rows={4}
                  className="rounded-lg border border-blue-100 px-4 py-3"
                />

                {errorMessage ? <p className="text-sm text-red-600">{errorMessage}</p> : null}

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex w-full items-center justify-center rounded-lg bg-primary px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {isSubmitting ? "Submitting..." : "Submit Enquiry"}
                </button>
              </form>
            )}
          </div>
        </div>
      ) : null}
    </EnquiryModalContext.Provider>
  );
}
