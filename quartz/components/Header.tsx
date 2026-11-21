import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"

// `italic` is for taxon names, which take italics in running text and should
// keep them in the nav. `fullLoad` skips in-site navigation, so inline page
// scripts run (the Lactobacillaceae pages' chat panel).
const navLinks: { title: string; slug: FullSlug; italic?: boolean; fullLoad?: boolean }[] = [
  { title: "Posts", slug: "posts/index" as FullSlug },
  { title: "Lactobacillaceae", slug: "lactobacillaceae" as FullSlug, italic: true, fullLoad: true },
]

const Header: QuartzComponent = ({ children, fileData }: QuartzComponentProps) => {
  if (children.length === 0) return null
  const [titleEl, ...rest] = children
  return (
    <header>
      {titleEl}
      <nav class="site-nav">
        {navLinks.map(({ title, slug, italic, fullLoad }) => (
          <a
            href={resolveRelative(fileData.slug!, slug)}
            {...(fullLoad ? { "data-router-ignore": "" } : {})}
          >
            {italic ? <em>{title}</em> : title}
          </a>
        ))}
      </nav>
      {rest}
    </header>
  )
}

export default (() => Header) satisfies QuartzComponentConstructor
