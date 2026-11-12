import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { buildMetadata } from "@/lib/seo";
import { getHomeVideos } from "@/lib/videos";

export const metadata: Metadata = buildMetadata({
  title: "School Videos",
  description: "Watch official school videos, campus highlights, and student life stories.",
  path: "/videos",
});

export default async function VideosPage() {
  const videos = await getHomeVideos();

  return (
    <main>
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-8 px-4">
          <div>
            <h1>School Videos</h1>
            <p className="mt-2 max-w-3xl text-gray">Explore featured videos from British School including campus life, academics, and student activities.</p>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {videos.map((video) => (
              <article key={video.slug} className="overflow-hidden rounded-xl border border-blue-100 bg-white">
                <Link href={`/videos/${video.slug}`} className="block">
                  <div className="relative h-52">
                    <Image src={video.thumbnailUrl} alt={video.title?.trim() || "School video thumbnail"} fill className="object-cover" />
                  </div>
                  <div className="space-y-2 p-4">
                    <h2 className="!text-lg !text-midnight_text">{video.title?.trim() || "School Video"}</h2>
                    <p className="line-clamp-3 text-sm text-gray">{video.description?.trim() || "Watch this featured school video."}</p>
                  </div>
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
