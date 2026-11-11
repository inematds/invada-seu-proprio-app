> **Defensive use:** only test apps that are YOURS or that you have written permission to test, always on a test copy (staging/sandbox), never in production with customers. This kit is to PROTECT, not to attack others.

# Hack your own app — defensive kit

[![Hack your own app](guia/assets/banner-en.jpg)](https://inematds.github.io/invada-seu-proprio-app/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 English · 🇪🇸 [Español](README.es.md)**

## What it is

Hack your own app is a defensive review kit with a checker, five gap guides and prompts to organize the results. It is for anyone who built an app with AI and can edit the project, but does not work with security every day. It helps you look for signs of flaws, fix the app's rules and verify the result before publishing. To use it, you need an isolated copy of your app, made-up data, two fake accounts and Python 3.

## 📖 How to use

https://inematds.github.io/invada-seu-proprio-app/guia/en/

Built an app with AI and want to check what ended up exposed? This kit helps you look for signs, fix insecure decisions on the server and repeat the tests before publishing. It was written for people who can edit the app, but do not work with security every day.

## The five gaps

1. [Password reset](kit/brechas/01-reset-de-senha.md): an identifier coming from the browser lets you change the password of the wrong account.
2. [Reviews and comments](kit/brechas/02-avaliacoes-e-comentarios.md): saved content is interpreted as code in the reader's browser.
3. [Site chatbot](kit/brechas/03-chatbot-do-site.md): off-topic requests consume your inference quota.
4. [Checkout and price](kit/brechas/04-checkout-e-preco.md): the server accepts the value the buyer sent.
5. [Email and agent](kit/brechas/05-email-e-agente.md): the agent treats instructions received in a message as orders from the owner.

## How to use

Follow [START HERE](kit/COMECE-AQUI.md). Prepare two fake accounts and disposable data in staging. Run:

```sh
python3 kit/scripts/checa.py --url https://staging.seu-app.test --eu-tenho-permissao
python3 kit/testes/run.py
```

The address above illustrates the format: replace it with your test copy's address. The flag declares your authorization and the use of staging; the script cannot verify ownership or the environment.

The checker makes a single GET, without following redirects, without login and without submitting forms. It analyzes only the HTML and inline JavaScript received: it does not download external scripts or visit other routes. Signs do not prove exploitation; the absence of signs does not prove security. Authorization, values in the database, chatbot consumption and agent tools require manual checking.

Use the [simulated test and visual report prompts](kit/prompts/pentest-do-seu-app.md) to organize the review. The [local examples](kit/exemplos/) are demonstrative and have no backend. The vulnerable example does not run received scripts or send data.

[Guide address](https://inematds.github.io/invada-seu-proprio-app/guia/en/) — publishing reference; the guide page is not part of this kit.

Python 3, with no additional dependencies. Original content. [MIT](LICENSE) license.
