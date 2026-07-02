# Diagrama de Arquitetura

```mermaid
flowchart TD
    A[Consultor ou usuário] --> B[API FastAPI]

    B --> C[Dados do cliente ACME]
    C --> C1[Documentos]
    C --> C2[Feedbacks]
    C --> C3[Questionário de segurança]

    B --> D[Busca baseada em documentos]
    D --> D1[Quebra dos textos em pedaços]
    D1 --> D2[Transformação dos textos em números]
    D2 --> D3[Armazenamento vetorial local]
    D3 --> D4[Resposta com fontes]

    B --> E[Agente com ferramentas]
    E --> E1[Busca de conhecimento]
    E --> E2[Questionário de segurança]
    E --> E3[Análise de feedback]
    E --> E4[Relatório de status]
    E --> E5[Estimativa de custo]
    E --> E6[Avaliação de arquitetura AWS]

    B --> F[Camada de modelo de linguagem]
    F --> F1[Modo local sem custo]
    F --> F2[Amazon Bedrock opcional]

    B --> G[Interface estilo MCP]
    G --> G1[Listagem de ferramentas]
    G --> G2[Chamada de ferramentas]

    H[Amazon S3] -. produção .-> C
    I[Amazon Bedrock] -. produção .-> F2
    J[CloudWatch, IAM e banco vetorial gerenciado] -. evolução futura .-> B
```

## Observações
- O projeto roda localmente por padrão.
- O Amazon Bedrock é opcional e manual.
- O Amazon S3 foi preparado com arquivos de exemplo do cliente.
- A camada MCP é uma demonstração no estilo MCP, não um servidor oficial completo.
- Os demais componentes AWS aparecem como plano de produção, não como infraestrutura já implantada.
