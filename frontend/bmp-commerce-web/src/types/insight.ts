export type SeveridadeInsight = 'Alerta' | 'Oportunidade' | 'Info'

export interface Insight {
  tipo: string
  severidade: SeveridadeInsight
  titulo: string
  mensagem: string
  destaque: string | null
  acao: string | null
  valor: number | null
}

export interface ResumoInsights {
  alertas: number
  oportunidades: number
  informativos: number
}

export interface InsightsResponse {
  geradoEm: string
  resumo: ResumoInsights
  insights: Insight[]
}
