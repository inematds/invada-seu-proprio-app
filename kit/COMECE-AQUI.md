> **Uso defensivo:** só teste aplicativos que são SEUS ou que você tem permissão escrita para testar, sempre numa cópia de teste (staging/sandbox), nunca em produção com clientes. Este kit é para PROTEGER, não para invadir os outros.

# Comece aqui: cinco passos

1. **Prepare staging.** Copie a estrutura do app, use dados inventados e duas contas suas, A e B. Desative envio real de e-mail, cobrança real e integrações que alteram sistemas externos. Use uma caixa de e-mail de teste e pagamento em sandbox. Anote URL, rotas permitidas, responsável e autorização. Faça um backup da cópia.
2. **Rode o checa.** Execute `python3 kit/scripts/checa.py --url https://staging.seu-app.test --eu-tenho-permissao`, trocando a URL pela sua. Leia os limites do relatório. Se houver erro de rede ou redirecionamento, confira manualmente o destino e informe a URL final autorizada. Não conclua que o app é seguro por ausência de indícios.
3. **Leia as cinco brechas.** Siga os documentos em [brechas](brechas/), de 01 a 05. Marque cada uma como aplicável, não aplicável ou pendente. Só use contas e registros fictícios sob seu controle. Registre comportamento esperado, observado e evidências sem senhas, tokens ou dados pessoais.
4. **Aplique a correção.** Corrija a regra no servidor, não só na tela. Use os pseudocódigos como contratos de comportamento, adaptando ao seu projeto. Revise também rotas alternativas. Faça uma mudança por vez para entender o resultado.
5. **Confirme.** Repita o cenário recusado e o fluxo legítimo, verificando banco, logs e estado final. Rode `python3 kit/testes/run.py` para validar o verificador; esse teste não valida seu app. Documente pendências antes de publicar e mantenha toda tentativa de segurança em staging.

Para cada achado, registre: brecha, rota, conta fictícia usada, evidência, risco, correção, resultado do reteste e responsável. Se precisar de ajuda de um assistente, use o [prompt com escopo fechado](prompts/pentest-do-seu-app.md).
