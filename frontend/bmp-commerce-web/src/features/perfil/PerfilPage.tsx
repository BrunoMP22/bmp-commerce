import { UserCircle } from 'lucide-react'
import { PagePlaceholder } from '@/components/layout/PagePlaceholder'

export function PerfilPage() {
  return (
    <PagePlaceholder
      title="Perfil"
      description="A edição de perfil e senha será implementada em uma sprint futura."
      icon={UserCircle}
    />
  )
}
