import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"

const navLinks: { title: string; slug: FullSlug }[] = [
  { title: "Non-sci writing", slug: "posts/index" as FullSlug },
]

const Header: QuartzComponent = ({ children, fileData }: QuartzComponentProps) => {
  if (children.length === 0) return null
  const [titleEl, ...rest] = children
  return (
    <header>
      {titleEl}
      <nav class="site-nav">
        {navLinks.map(({ title, slug }) => (
          <a href={resolveRelative(fileData.slug!, slug)}>{title}</a>
        ))}
      </nav>
      {rest}
    </header>
  )
}

export default (() => Header) satisfies QuartzComponentConstructor
