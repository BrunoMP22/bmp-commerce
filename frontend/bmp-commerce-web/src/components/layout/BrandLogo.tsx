import { cn } from '@/lib/utils'

/**
 * Marca do BMP Commerce: sacola de compras com linha de tendência subindo —
 * comércio + insights. Traço em `currentColor`, então herda a cor do contexto
 * (branca sobre o badge azul, azul sobre fundo claro etc.).
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      stroke="currentColor"
      strokeWidth={2.2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M11.5 11V8.75a4.5 4.5 0 0 1 9 0V11" />
      <path d="M6.5 11h19l-1.16 13.06a3 3 0 0 1-2.99 2.74H10.65a3 3 0 0 1-2.99-2.74L6.5 11Z" />
      <polyline points="10.75 21.5 14.5 17.75 17 19.75 21.25 15.5" />
      <polyline points="18.25 15.5 21.25 15.5 21.25 18.5" />
    </svg>
  )
}

/** Badge quadrado com a marca — o "quadradinho" da sidebar e telas de auth. */
export function LogoBadge({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'flex shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground',
        className,
      )}
    >
      <LogoMark className="size-[70%]" />
    </div>
  )
}
