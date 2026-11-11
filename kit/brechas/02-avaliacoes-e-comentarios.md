> **Uso defensivo:** só teste aplicativos que são SEUS ou que você tem permissão escrita para testar, sempre numa cópia de teste (staging/sandbox), nunca em produção com clientes. Este kit é para PROTEGER, não para invadir os outros.

# Avaliações e comentários

## O que é

Um comentário pode ficar salvo e ser mostrado a outras pessoas.
Se o app interpreta esse texto como HTML ativo, conteúdo do autor pode executar no navegador de quem lê: é XSS armazenado.
Isso pode alterar a tela ou redirecionar alguém para um login falso.
A verificação aqui usa apenas marcação inofensiva, sem capturar dados ou criar telas falsas.

## Como saber se o seu app tem

1. Em staging, publique com A o texto `Teste <b>visível</b> & confirmação` num registro fictício.
2. Abra a avaliação com B, inclusive em listagens e moderação. Se a proposta é aceitar só texto, as tags devem aparecer literalmente, sem negrito.
3. Se formatação é permitida, negrito por si só não é falha. Revise o código que limita tags, atributos e protocolos dos links.
4. Inspecione os pontos que montam HTML com conteúdo recebido. Não injete script, redirecionamento nem formulário de login. Remova o comentário de teste.

## Como corrigir

Prefira texto simples. Valide tamanho na entrada e renderize como texto, com escape adequado ao contexto. Não concatene comentários em scripts, atributos ou URLs. Se houver formatação, use um sanitizador mantido, baseado em parser e lista de permissões; expressões regulares não são um sanitizador de HTML. Adicione CSP restritiva como defesa adicional, sem substituir o tratamento da saída.

```text
salvar_comentario(usuario, texto):
    exigir usuario autorizado e texto e uma string
    exigir tamanho(texto) <= 2000
    banco.salvar(texto)

mostrar_comentario(registro):
    elemento.textContent = registro.texto
    # template no servidor: usar escape automatico no contexto de texto

mostrar_formatacao_opcional(registro):
    seguro = sanitizar_com_parser(registro.texto,
        tags=[p, b, em, ul, li], atributos=[], protocolos=[])
    renderizar_html_sanitizado(seguro)

resposta.headers[Content-Security-Policy] =
    "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
```

Adapte a CSP aos recursos necessários e teste antes de aplicar. Não libere scripts inline indiscriminadamente só para eliminar erros.

## Como confirmar que corrigiu

- A marcação de teste aparece como texto no modo simples, em todas as telas.
- No modo formatado, testes do renderizador comprovam remoção de tags e atributos fora da lista e URLs com protocolos não permitidos.
- Comentários antigos também passam pela saída segura.
- CSP aparece na resposta HTTP real; o fluxo legítimo de publicar e ler continua funcionando.
