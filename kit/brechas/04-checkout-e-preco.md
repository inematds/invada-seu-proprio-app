> **Uso defensivo:** só teste aplicativos que são SEUS ou que você tem permissão escrita para testar, sempre numa cópia de teste (staging/sandbox), nunca em produção com clientes. Este kit é para PROTEGER, não para invadir os outros.

# Checkout e preço

## O que é

O navegador é controlado pelo comprador e qualquer valor enviado por ele pode mudar.
A brecha aparece quando o servidor usa esse valor como preço final do pedido.
Um produto de 100 pode acabar registrado como pago por 1.
Mostrar o preço correto na página não protege a cobrança nem a entrega.

## Como saber se o seu app tem

1. Configure pagamento em sandbox e um produto fictício de 100 unidades monetárias.
2. Observe no painel de rede se o checkout envia preço, total ou desconto. Isso é um indício, não comprovação.
3. Só em sandbox, reenvie uma única solicitação do produto de teste alterando o preço informado para 1. O servidor deve ignorá-lo ou rejeitá-lo.
4. Confira o pedido no banco e a cobrança de teste. Nenhum pagamento real ou entrega real deve ocorrer. Revise também a confirmação de pagamento.

## Como corrigir

Receba produto e quantidade; consulte preços e regras de desconto no servidor. Use unidades monetárias inteiras (centavos), valide quantidade e moeda. Grave o total esperado antes de abrir a cobrança. Na confirmação, autentique a notificação e consulte o provedor, conferindo pedido, valor, moeda e status. Trate eventos repetidos sem repetir entrega.

```text
criar_pedido(usuario, produto_id, quantidade):
    exigir quantidade inteira entre 1 e limite_do_produto
    produto = banco.produto_ativo(produto_id)
    total = calcular_no_servidor(produto, quantidade, descontos_autorizados)
    pedido = salvar_pendente(usuario, total_centavos=total, moeda=produto.moeda)
    cobranca = sandbox.criar_cobranca(pedido.id, total, pedido.moeda,
                                    chave_idempotencia=pedido.id)
    vincular_cobranca(pedido.id, cobranca.id)

confirmar(evento):
    exigir assinatura_valida(evento)
    cobranca = consultar_provedor(evento.cobranca_id)
    em transacao:
        pedido = buscar_e_bloquear_por_cobranca(cobranca.id)
        exigir cobranca.pedido_id == pedido.id
        exigir cobranca.total == pedido.total e cobranca.moeda == pedido.moeda
        exigir cobranca.status == "pago"
        se pedido.ja_entregue: retornar
        marcar_pago_e_agendar_entrega_unica(pedido)
```

## Como confirmar que corrigiu

- Alterar preço no cliente não reduz o valor calculado no servidor.
- Quantidade negativa, fracionada ou acima do limite é recusada.
- Pagamento pendente ou com valor/moeda divergente não libera entrega.
- Repetir o mesmo evento não duplica entrega; o checkout legítimo em sandbox continua funcionando.
