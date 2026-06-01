import { ChevronLeft, ChevronRight } from "lucide-react"

export type PaginationProps = {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
}

export function Pagination({ page, pageSize, total, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="flex items-center justify-end gap-2">
      <div className="text-sm text-muted-foreground">Page {page} of {totalPages}</div>
      <div className="inline-flex items-center gap-1 rounded-md border border-border/60 bg-card p-1">
        <button
          type="button"
          aria-label="Previous page"
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page <= 1}
          className="inline-flex items-center rounded px-2 py-1 text-sm disabled:opacity-50"
        >
          <ChevronLeft className="size-4" />
        </button>
        <button
          type="button"
          aria-label="Next page"
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={page >= totalPages}
          className="inline-flex items-center rounded px-2 py-1 text-sm disabled:opacity-50"
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </div>
  )
}

export default Pagination
