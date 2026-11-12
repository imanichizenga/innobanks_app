/**
 * Converts markdown content to HTML string
 * For static export, this is a simple passthrough since react-markdown handles rendering
 */
export default async function markdownToHtml(
  markdown: string
): Promise<string> {
  // For static site generation, we can return the markdown as-is
  // since react-markdown will handle the rendering on the client/server
  return markdown;
}
