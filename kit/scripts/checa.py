#!/usr/bin/env python3
"""Uso defensivo: só teste apps SEUS ou com permissão escrita, em staging/sandbox.
Nunca em produção com clientes. Este kit é para PROTEGER, não invadir os outros.
"""
import argparse
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

AVISO = ('Só teste aplicativos que são SEUS ou que você tem permissão escrita para testar, '
         'sempre numa cópia de teste (staging/sandbox), nunca em produção com clientes. '
         'Este kit é para PROTEGER, não para invadir os outros.')
LIMITE_BYTES = 1_000_000
TIMEOUT = 5
INDICIO = 'encontrei indício'
AUSENTE = 'não encontrei'
INDETERMINADO = 'não dá para saber passivamente'


def analisar_headers(headers):
    """Analisa presença, não eficácia, sem I/O; nomes são case-insensitive."""
    normalizados = {str(k).lower(): str(v).strip() for k, v in headers.items()}
    return {nome: bool(normalizados.get(nome, '')) for nome in (
        'content-security-policy', 'x-frame-options',
        'x-content-type-options', 'strict-transport-security')}


def analisar_html(texto, headers):
    """Retorna indícios e limitações; não executa HTML/JS nem comprova falhas."""
    fonte = html.unescape(texto)
    cabecalhos = analisar_headers(headers)
    ids = sorted(set(re.findall(r'\b(?:account_id|workspace_id|super_admin)\b',
                                fonte, flags=re.I)))
    preco = bool(re.search(
        r'''\b(?:name|id)\s*=\s*["']?(?:price|preco|preço|unit_price|total|amount)\b''',
        fonte, re.I) or re.search(
        r'''["']?\b(?:price|preco|preço|unit_price|amount|total)["']?\s*[:=]\s*["']?\d''',
        fonte, re.I))
    review = bool(re.search(
        r'<(?:form|textarea|input)\b[^>]*\b(?:review|comment|comentario|comentário|avaliacao|avaliação)\b',
        fonte, re.I))
    # São pistas de implementação, não prova de que protegem este campo.
    saida_texto = bool(re.search(r'\b(?:textContent|innerText|escapeHTML|escape_html|sanitize|sanitizar)\b', fonte, re.I))
    sink_html = bool(re.search(r'\b(?:innerHTML|outerHTML|insertAdjacentHTML)\b', fonte, re.I))
    evidencias_review = []
    if review and not saida_texto:
        evidencias_review.append('Campo de comentário/avaliação sem pista de tratamento na resposta recebida.')
    if review and sink_html:
        evidencias_review.append('Campo de comentário e ponto de inserção de HTML no mesmo documento; vínculo não comprovado.')

    def achado(chave, nome, evidencias, correcao, limite):
        return dict(id=chave, brecha=nome,
                    estado=INDICIO if evidencias else AUSENTE,
                    evidencias=evidencias, correcao=correcao, limite=limite)

    achados = [achado('reset-de-senha', 'Reset de senha',
        ['Referências no front: ' + ', '.join(ids) + '. Podem ter usos legítimos.'] if ids else [],
        'Derivar a conta só do token, com expiração e consumo único atômico; ignorar ID do cliente.',
        'A home não revela a autorização do reset; confirme a rota e o servidor com contas fictícias.'),
        achado('avaliacoes-e-comentarios', 'Avaliações e comentários', evidencias_review,
        'Renderizar texto com escape; sanitizar formatação por lista de permissões e aplicar CSP.',
        'Marcadores de tratamento não provam proteção. Não houve envio de comentário nem execução de código.'),
        dict(id='chatbot-do-site', brecha='Chatbot do site', estado=INDETERMINADO,
             evidencias=[], correcao='Classificar assunto (sim/não e confiança), validar saída, limitar uso e fixar a política no servidor.',
             limite='A home não revela classificação, cotas ou orçamento; revise o backend e simule poucas mensagens.'),
        achado('checkout-e-preco', 'Checkout e preço',
        ['Preço/total em campo ou atribuição do cliente; exibir preço é normal e não prova confiança do servidor.'] if preco else [],
        'Calcular preço no servidor e conferir pedido, valor, moeda e status no provedor de pagamento.',
        'Não houve checkout ou cobrança. Confirme cálculo e pagamento apenas em sandbox.'),
        dict(id='email-e-agente', brecha='E-mail e agente', estado=INDETERMINADO,
             evidencias=[], correcao='Dar acesso mínimo, tratar e-mails como dados e exigir confirmação humana para ações sensíveis.',
             limite='Permissões do agente e comportamento com mensagens não são visíveis na home.')]
    return {'achados': achados, 'headers': cabecalhos,
            'limites': 'Somente HTML e JS inline desta resposta. Não lê arquivos JS externos, outras rotas ou backend. Ausência de indícios não é prova de segurança.'}


class SemRedirecionamento(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validar_url(url):
    try:
        partes = urllib.parse.urlsplit(url)
        porta = partes.port
    except ValueError:
        raise ValueError('URL inválida: confira endereço e porta.') from None
    if (partes.scheme not in ('http', 'https') or not partes.hostname
            or partes.username is not None or partes.password is not None
            or partes.fragment or partes.query or any(c.isspace() for c in url)
            or any(ord(c) < 32 for c in url) or (porta is not None and porta < 1)):
        raise ValueError('Use URL HTTP/HTTPS de staging, sem credenciais, parâmetros ou fragmentos.')
    return url


def buscar_home(url):
    """Um GET, sem cookies, credenciais, redirecionamento ou busca de recursos."""
    url = validar_url(url)
    pedido = urllib.request.Request(url, headers={
        'User-Agent': 'KitDefensivo/1.0', 'Accept': 'text/html',
        'Accept-Encoding': 'identity'}, method='GET')
    opener = urllib.request.build_opener(SemRedirecionamento())
    with opener.open(pedido, timeout=TIMEOUT) as resposta:
        if resposta.headers.get_content_type() not in ('text/html', 'application/xhtml+xml'):
            raise ValueError('A resposta não é HTML; análise interrompida, sem conclusão sobre o app.')
        dados = resposta.read(LIMITE_BYTES + 1)
        if len(dados) > LIMITE_BYTES:
            raise ValueError('HTML excede o limite de 1 MB; análise interrompida, sem conclusão sobre o app.')
        charset = resposta.headers.get_content_charset() or 'utf-8'
        try:
            texto = dados.decode(charset, errors='replace')
        except LookupError:
            texto = dados.decode('utf-8', errors='replace')
        return texto, dict(resposta.headers.items())


def imprimir_relatorio(relatorio):
    print('\nRELATÓRIO PASSIVO — indício não confirma vulnerabilidade')
    for item in relatorio['achados']:
        print('\n' + item['brecha'] + ': ' + item['estado'])
        for evidencia in item['evidencias']:
            print('  Indício: ' + evidencia)
        print('  Limite: ' + item['limite'])
        print('  Correção: ' + item['correcao'])
    print('\nCabeçalhos HTTP de segurança (presença, não eficácia):')
    for nome, presente in relatorio['headers'].items():
        print('  ' + nome + ': ' + ('presente; conteúdo precisa de revisão' if presente else 'ausente ou vazio'))
    print('  CSP: restringir origens de scripts e enquadramento; Report-Only não impõe bloqueio.')
    print('  X-Frame-Options: usar DENY/SAMEORIGIN conforme o app; CSP frame-ancestors pode substituí-lo.')
    print('  X-Content-Type-Options: configurar nosniff. HSTS: aplicar apenas em HTTPS validado.')
    print('  Ausência de CSP não comprova XSS; presença de cabeçalhos não corrige autorização ou preços.')
    print('\n' + relatorio['limites'])


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False,
        usage='%(prog)s --url URL --eu-tenho-permissao [--json]',
        description=AVISO + ' Checagem passiva com um único GET e timeout de 5 segundos por operação de rede.')
    parser._optionals.title = 'Opções'
    parser.add_argument('-h', '--help', action='help', help='Mostra esta ajuda e encerra.')
    parser.add_argument('--url', required=True, help='URL da home do SEU app em staging; sem parâmetros ou credenciais.')
    parser.add_argument('--eu-tenho-permissao', action='store_true', help='Obrigatória: declara autorização e ambiente de teste isolado.')
    parser.add_argument('--json', action='store_true', help='Emite relatório JSON, incluindo aviso e limites.')
    args = parser.parse_args(argv)
    if not args.eu_tenho_permissao:
        parser.error('Recusado: declare --eu-tenho-permissao apenas se tiver autorização e usar staging/sandbox. Nenhuma requisição foi enviada.')
    try:
        texto, headers = buscar_home(args.url)
    except urllib.error.HTTPError as erro:
        if 300 <= erro.code < 400:
            print('Redirecionamento recusado. Confira o destino manualmente e use somente a URL final autorizada de staging.')
        else:
            print('Erro HTTP ' + str(erro.code) + ': não foi possível analisar a home. Nenhuma conclusão de segurança.')
        return 1
    except (urllib.error.URLError, OSError, ValueError) as erro:
        # Não exibe URL, corpo da resposta nem detalhes que possam conter segredos.
        print('Não foi possível analisar: ' + (str(erro) if isinstance(erro, ValueError) else 'falha de rede, TLS ou timeout. Confira a URL e a conexão.'))
        return 1
    relatorio = analisar_html(texto, headers)
    relatorio['aviso'] = AVISO
    if args.json:
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    else:
        print(AVISO)
        imprimir_relatorio(relatorio)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
