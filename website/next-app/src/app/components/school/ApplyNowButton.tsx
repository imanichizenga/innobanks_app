"use client";

import { useEnquiryModal } from "./EnquiryModalProvider";

export default function ApplyNowButton({ className, label = "Apply Now" }: { className?: string; label?: string }) {
  const { openEnquiryForm } = useEnquiryModal();

  return (
    <button type="button" onClick={openEnquiryForm} className={className}>
      {label}
    </button>
  );
}
