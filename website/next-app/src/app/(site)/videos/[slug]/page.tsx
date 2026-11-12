import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { buildMetadata, toAbsoluteUrl } from "@/lib/seo";
import { getHomeVideos } from "@/lib/videos";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const videos = await getHomeVideos();
  const video = videos.find((item) => item.slug === slug);

  if (!video) {
    return buildMetadata({
      title: "Video Not Found",
      description: "The requested video does not exist.",
      path: `/videos/${slug}`,
      noIndex: true,
    });
  }

  return buildMetadata({
    title: video.title?.trim() || "School Video",
    description: video.description?.trim() || "Watch this school video.",
    path: `/videos/${video.slug}`,
    image: video.thumbnailUrl,
  });
}

export default async function VideoWatchPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const videos = await getHomeVideos();
  const video = videos.find((item) => item.slug === slug);

  if (!video) {
    notFound();
  }

  const canonicalPath = `/videos/${video.slug}`;
  const uploadDate = video.created_at || undefined;

  const videoJsonLd = {
    "@context": "https://schema.org",
    "@type": "VideoObject",
    name: video.title?.trim() || "School Video",
    description: video.description?.trim() || "Featured school video.",
    thumbnailUrl: [video.thumbnailUrl],
    uploadDate,
    contentUrl: video.videoUrl,
    embedUrl: video.videoUrl,
    publisher: {
      "@type": "EducationalOrganization",
      name: "British Opening Schools",
      url: toAbsoluteUrl("/"),
    },
    mainEntityOfPage: toAbsoluteUrl(canonicalPath),
  };

  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(videoJsonLd) }} />
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-5 px-4">
          <p className="inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-primary">Video Watch Page</p>
          <h1>{video.title?.trim() || "School Video"}</h1>
          <p className="max-w-3xl text-gray">{video.description?.trim() || "Discover student life, academics, and school highlights in this official video."}</p>

          <article className="overflow-hidden rounded-2xl border border-blue-100 bg-white p-3 md:p-5">
            <video controls playsInline preload="metadata" poster={video.thumbnailUrl} className="h-auto w-full rounded-xl bg-black">
              <source src={video.videoUrl} />
              Your browser does not support the video tag.
            </video>
            {uploadDate ? <p className="mt-3 text-sm text-gray">Published on {new Date(uploadDate).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</p> : null}
          </article>
        </div>
      </section>
    </main>
  );
}
