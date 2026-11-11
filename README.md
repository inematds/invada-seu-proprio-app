> **Uso defensivo:** só teste aplicativos que são SEUS ou que você tem permissão escrita para testar, sempre numa cópia de teste (staging/sandbox), nunca em produção com clientes. Este kit é para PROTEGER, não para invadir os outros.

# Invada seu próprio app — kit defensivo

[![Invada seu próprio app](guia/assets/banner.jpg)](https://inematds.github.io/invada-seu-proprio-app/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

Invada seu próprio app é um kit de revisão defensiva com um verificador, cinco guias de brechas e prompts para organizar os resultados. É para quem construiu um app com IA e consegue editar o projeto, mas não trabalha com segurança todos os dias. Ele ajuda a procurar sinais de falhas, corrigir as regras do app e conferir o resultado antes de publicar. Para usar, você precisa de uma cópia isolada do seu app, dados inventados, duas contas fictícias e Python 3.

## 📖 Guia de uso

https://inematds.github.io/invada-seu-proprio-app/guia/

Construiu um app com IA e quer conferir o que ficou exposto? Este kit ajuda a procurar sinais, corrigir decisões inseguras no servidor e repetir os testes antes de publicar. Foi escrito para quem consegue editar o app, mas não trabalha com segurança todos os dias.

## As cinco brechas

1. [Reset de senha](kit/brechas/01-reset-de-senha.md): um identificador vindo do navegador permite trocar a senha da conta errada.
2. [Avaliações e comentários](kit/brechas/02-avaliacoes-e-comentarios.md): conteúdo salvo é interpretado como código no navegador de quem lê.
3. [Chatbot do site](kit/brechas/03-chatbot-do-site.md): pedidos fora do negócio consomem a sua cota de inferência.
4. [Checkout e preço](kit/brechas/04-checkout-e-preco.md): o servidor aceita o valor que o comprador enviou.
5. [E-mail e agente](kit/brechas/05-email-e-agente.md): o agente trata instruções recebidas em uma mensagem como ordens do dono.

## Como usar

Siga [COMECE AQUI](kit/COMECE-AQUI.md). Prepare duas contas fictícias e dados descartáveis em staging. Execute:

```sh
python3 kit/scripts/checa.py --url https://staging.seu-app.test --eu-tenho-permissao
python3 kit/testes/run.py
```

O endereço acima ilustra o formato: substitua pelo endereço da sua cópia de teste. A flag declara sua autorização e o uso de staging; o script não consegue verificar a propriedade ou o ambiente.

O verificador faz um único GET, sem seguir redirecionamentos, sem login e sem enviar formulários. Analisa somente o HTML e o JavaScript inline recebidos: não baixa scripts externos nem visita outras rotas. Indícios não comprovam exploração; ausência de indícios não comprova segurança. Autorização, valores no banco, consumo do chatbot e ferramentas do agente exigem conferência manual.

Use os [prompts de teste simulado e relatório visual](kit/prompts/pentest-do-seu-app.md) para organizar a revisão. Os [exemplos locais](kit/exemplos/) são demonstrativos e não têm backend. O exemplo vulnerável não executa scripts recebidos nem envia dados.

[Endereço do guia](https://inematds.github.io/invada-seu-proprio-app/guia/) — referência de publicação; a página do guia não faz parte deste kit.

Python 3, sem dependências adicionais. Conteúdo autoral. Licença [MIT](LICENSE).

## Vídeo

[Assista no YouTube](https://www.youtube.com/watch?v=UDAJ66IITq0) · [Short 9:16](https://youtube.com/shorts/FeB3cM4KULo) · [Player com legendas e capítulos](https://inematds.github.io/invada-seu-proprio-app/videos/)
