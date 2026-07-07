# 0003 - Serviços simples, sem MediatR

**Status:** aceita
**Data:** 2026-07-06

## Contexto

Em Clean Architecture com ASP.NET Core é comum usar o MediatR para implementar
casos de uso como Commands/Queries desacoplados via um mediador, com pipeline
de behaviors (validação, logging, transação) plugado por DI.

O MVP do BMP Commerce tem poucos casos de uso por sprint (Doc 04 §2-§7) e o
time optou por avaliar se o ganho de desacoplamento do MediatR compensa a
complexidade adicional (uma camada de indireção a mais, uma dependência a
mais, uma convenção a mais para todo desenvolvedor aprender) nesta fase do
produto (Doc 03 §8, nota sobre MediatR).

## Decisão

Casos de uso do MVP são **serviços simples**: uma classe por caso de uso
(`RegistrarVenda`, `CadastrarProduto`, `ListarProdutosAbaixoDoMinimo`...),
chamada diretamente pelo Controller via injeção de dependência — sem MediatR,
sem Commands/Queries/Handlers (Doc 03 §10 DECIDIDO 1, Doc 04 §8).

Convenção de nomes: verbo + substantivo (`RegistrarVenda`), registrado em
`Application/Operations/<Recurso>/` (Doc 04 §8).

## Consequências

**Prós:**
- Menos indireção: o Controller chama o serviço diretamente, sem passar por
  um mediador genérico — mais fácil de seguir "quem chama o quê" com poucos
  casos de uso.
- Uma dependência a menos no projeto.

**Contras / riscos aceitos:**
- Sem pipeline de behaviors pronto (validação, logging, transação) — cada
  caso de uso precisa aplicar essas preocupações explicitamente (ex.:
  FluentValidation chamado no início do serviço, Doc 03 §2.2).
- Se o número de casos de uso crescer muito ou o time desejar cross-cutting
  concerns uniformes, essa decisão pode ser revisitada — não é uma exclusão
  permanente do MediatR, apenas o ponto de partida do MVP.
