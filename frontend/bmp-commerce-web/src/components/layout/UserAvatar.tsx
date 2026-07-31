import { cn } from '@/lib/utils'

export function getInitials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

interface UserAvatarProps {
  name: string
  avatar: string | null | undefined
  className?: string
}

/** Foto de perfil quando houver; iniciais sobre o azul da marca quando não. */
export function UserAvatar({ name, avatar, className }: UserAvatarProps) {
  if (avatar) {
    return (
      <img
        src={avatar}
        alt={`Foto de ${name}`}
        className={cn('shrink-0 rounded-full object-cover', className)}
      />
    )
  }

  return (
    <div
      className={cn(
        'flex shrink-0 select-none items-center justify-center rounded-full bg-primary font-semibold text-primary-foreground',
        className,
      )}
      aria-hidden="true"
    >
      {getInitials(name)}
    </div>
  )
}
