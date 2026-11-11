#!/usr/bin/env python3
"""Uso defensivo: só teste apps SEUS ou com permissão escrita em staging/sandbox.
Nunca em produção com clientes. Este kit é para PROTEGER, não invadir os outros.
Testes offline: rede bloqueada por mock, inclusive em regressões do CLI.
"""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

KIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checa', KIT / 'scripts' / 'checa.py')
checa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checa)

VULNERAVEL = '''<form><input name="account_id"><input name="workspace_id">
<input name="price" value="100"><textarea name="review"></textarea></form>
<script>const config = {super_admin: false, price: 100};</script>'''
SEGURO = '''<label>Comentário<textarea name="review"></textarea></label>
<p id="saida"></p><script>saida.textContent = campo.value;</script>'''
HEADERS = {'Content-Security-Policy': "default-src 'self'; frame-ancestors 'none'",
           'X-Frame-Options': 'DENY', 'X-Content-Type-Options': 'nosniff',
           'Strict-Transport-Security': 'max-age=31536000'}


class TestesLogica(unittest.TestCase):
    def setUp(self):
        bloqueio = patch('urllib.request.OpenerDirector.open', side_effect=AssertionError('Rede proibida nos testes'))
        bloqueio.start()
        self.addCleanup(bloqueio.stop)

    def estados(self, texto, headers=None):
        return {a['id']: a['estado'] for a in checa.analisar_html(texto, headers or {})['achados']}

    def test_fixture_vulneravel(self):
        r = self.estados(VULNERAVEL)
        for chave in ('reset-de-senha', 'avaliacoes-e-comentarios', 'checkout-e-preco'):
            self.assertEqual(r[chave], checa.INDICIO)
        for chave in ('chatbot-do-site', 'email-e-agente'):
            self.assertEqual(r[chave], checa.INDETERMINADO)

    def test_fixture_seguro(self):
        r = self.estados(SEGURO, HEADERS)
        self.assertNotIn(checa.INDICIO, r.values())
        self.assertEqual(len(r), 5)
        self.assertEqual(r['checkout-e-preco'], checa.AUSENTE)

    def test_exemplos_reais(self):
        vulneravel = (KIT / 'exemplos' / 'app-vulneravel.html').read_text(encoding='utf-8')
        seguro = (KIT / 'exemplos' / 'app-seguro.html').read_text(encoding='utf-8')
        self.assertEqual(self.estados(vulneravel), self.estados(VULNERAVEL))
        self.assertEqual(self.estados(seguro), self.estados(SEGURO))

    def test_headers_case_insensitive(self):
        self.assertTrue(all(checa.analisar_headers(HEADERS).values()))
        self.assertTrue(all(checa.analisar_headers({k.upper(): v for k, v in HEADERS.items()}).values()))
        self.assertFalse(any(checa.analisar_headers({}).values()))

    def test_report_only_nao_equivale_a_csp(self):
        r = checa.analisar_headers({'Content-Security-Policy-Report-Only': "default-src 'self'", 'X-Frame-Options': '  '})
        self.assertFalse(r['content-security-policy'])
        self.assertFalse(r['x-frame-options'])

    def test_html_sink_continua_indicio_com_marcador_seguro(self):
        r = self.estados(SEGURO + '<script>outro.innerHTML = dado;</script>')
        self.assertEqual(r['avaliacoes-e-comentarios'], checa.INDICIO)

    def test_preco_json_e_atributo_sem_aspas(self):
        for texto in ('<script>{"price": 100}</script>', '<input name=price value=100>'):
            self.assertEqual(self.estados(texto)['checkout-e-preco'], checa.INDICIO)

    def test_texto_comum_nao_dispara_preco(self):
        self.assertEqual(self.estados('<p>Preço: consulte o catálogo. Total de pessoas.</p>')['checkout-e-preco'], checa.AUSENTE)

    def test_vazio_nao_atesta_seguranca(self):
        r = checa.analisar_html('', {})
        self.assertNotIn(checa.INDICIO, [a['estado'] for a in r['achados']])
        self.assertIn('não é prova', r['limites'])

    def test_sem_permissao_nao_busca(self):
        with patch.object(checa, 'buscar_home') as busca, contextlib.redirect_stderr(io.StringIO()) as saida:
            with self.assertRaises(SystemExit) as erro:
                checa.main(['--url', 'https://staging.test'])
            self.assertEqual(erro.exception.code, 2)
            busca.assert_not_called()
            self.assertIn('Recusado', saida.getvalue())

    def test_url_restrita(self):
        for url in ('file:///etc/passwd', 'https://u:senha@staging.test',
                    'https://staging.test?token=segredo', 'https://staging.test/#x',
                    'http://', 'http://staging.test:invalida', 'https://staging.test/\n'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                checa.validar_url(url)
        self.assertEqual(checa.validar_url('http://localhost:8000/'), 'http://localhost:8000/')

    def test_redirecionamento_nao_segue(self):
        self.assertIsNone(checa.SemRedirecionamento().redirect_request(None, None, 302, '', {}, 'https://outro.test'))

    def test_cli_rede_e_http_falham_sem_conclusao(self):
        erros = [urllib.error.URLError('falha'), TimeoutError(),
                 urllib.error.HTTPError('https://staging.test', 302, 'redirect', {}, None),
                 urllib.error.HTTPError('https://staging.test', 403, 'negado', {}, None)]
        for erro in erros:
            with patch.object(checa, 'buscar_home', side_effect=erro), contextlib.redirect_stdout(io.StringIO()) as saida:
                self.assertEqual(checa.main(['--url', 'https://staging.test', '--eu-tenho-permissao']), 1)
                self.assertNotIn('RELATÓRIO PASSIVO', saida.getvalue())

    def test_cli_relatorio_e_json_offline(self):
        for extra in ([], ['--json']):
            with patch.object(checa, 'buscar_home', return_value=(VULNERAVEL, {})), contextlib.redirect_stdout(io.StringIO()) as saida:
                self.assertEqual(checa.main(['--url', 'https://staging.test', '--eu-tenho-permissao'] + extra), 0)
                texto = saida.getvalue()
                self.assertIn('PROTEGER', texto)
                self.assertIn(checa.INDICIO, texto)
                if extra:
                    self.assertEqual(len(checa.json.loads(texto)['achados']), 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
