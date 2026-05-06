from django.test import TestCase

from accounts.models import Usuario
from coleta.forms import DescarteForm
from coleta.models import Descarte, PontoColeta


def criar_usuario(email='teste@ecosmart.com', saldo=0):
    """Helper para criar utilizador de teste."""
    return Usuario.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='senha123',
        nome='Utilizador Teste',
        saldo_pontos=saldo,
    )


def criar_ponto():
    """Helper para criar ponto de coleta de teste."""
    return PontoColeta.objects.create(
        nome='Ponto Teste',
        endereco='Rua Teste, 1',
        tipos_aceitos='Plástico, Vidro',
    )


# ─────────────────────────────────────────────────────────────────
# Testes do Modelo Descarte
# ─────────────────────────────────────────────────────────────────

class DescarteModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.ponto = criar_ponto()

    def test_calcular_pontos_retorna_valor_correto(self):
        """1 kg = 10 pontos. 2,5 kg deve gerar 25 pontos."""
        descarte = Descarte(peso_kg=2.5)
        self.assertEqual(descarte.calcular_pontos(), 25)

    def test_calcular_pontos_arredonda_para_baixo(self):
        """1,9 kg deve gerar 19 pontos (int trunca a parte decimal)."""
        descarte = Descarte(peso_kg=1.9)
        self.assertEqual(descarte.calcular_pontos(), 19)

    def test_save_calcula_pontos_automaticamente(self):
        """Ao salvar um Descarte, pontos_gerados deve ser preenchido automaticamente."""
        descarte = Descarte.objects.create(
            usuario=self.usuario,
            ponto=self.ponto,
            tipo_residuo='Plástico',
            peso_kg=3.0,
        )
        self.assertEqual(descarte.pontos_gerados, 30)

    def test_save_atualiza_saldo_do_usuario(self):
        """Ao salvar um Descarte, o saldo do utilizador deve ser incrementado."""
        saldo_inicial = self.usuario.saldo_pontos
        Descarte.objects.create(
            usuario=self.usuario,
            ponto=self.ponto,
            tipo_residuo='Vidro',
            peso_kg=2.0,
        )
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.saldo_pontos, saldo_inicial + 20)

    def test_save_nao_atualiza_saldo_em_edicao(self):
        """Editar um Descarte existente NAO deve alterar o saldo do utilizador."""
        descarte = Descarte.objects.create(
            usuario=self.usuario,
            ponto=self.ponto,
            tipo_residuo='Metal',
            peso_kg=1.0,
        )
        self.usuario.refresh_from_db()
        saldo_apos_criacao = self.usuario.saldo_pontos

        # Edita o descarte (nao deve alterar o saldo novamente)
        descarte.tipo_residuo = 'Alumínio'
        descarte.save()

        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.saldo_pontos, saldo_apos_criacao)

    def test_save_multiplos_descartes_acumula_saldo(self):
        """Múltiplos descartes devem acumular o saldo corretamente."""
        Descarte.objects.create(
            usuario=self.usuario, ponto=self.ponto,
            tipo_residuo='Plástico', peso_kg=1.0,
        )
        Descarte.objects.create(
            usuario=self.usuario, ponto=self.ponto,
            tipo_residuo='Vidro', peso_kg=2.0,
        )
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.saldo_pontos, 30)  # 10 + 20


# ─────────────────────────────────────────────────────────────────
# Testes do Formulário DescarteForm
# ─────────────────────────────────────────────────────────────────

class DescarteFormTest(TestCase):

    def setUp(self):
        self.ponto = criar_ponto()

    def _dados_validos(self, **override):
        dados = {
            'ponto': self.ponto.pk,
            'tipo_residuo': 'Plástico',
            'peso_kg': 1.5,
        }
        dados.update(override)
        return dados

    def test_formulario_valido(self):
        form = DescarteForm(data=self._dados_validos())
        self.assertTrue(form.is_valid(), form.errors)

    def test_peso_zero_invalido(self):
        form = DescarteForm(data=self._dados_validos(peso_kg=0))
        self.assertFalse(form.is_valid())
        self.assertIn('peso_kg', form.errors)

    def test_peso_negativo_invalido(self):
        form = DescarteForm(data=self._dados_validos(peso_kg=-5))
        self.assertFalse(form.is_valid())
        self.assertIn('peso_kg', form.errors)

    def test_peso_acima_do_limite_invalido(self):
        form = DescarteForm(data=self._dados_validos(peso_kg=6000))
        self.assertFalse(form.is_valid())
        self.assertIn('peso_kg', form.errors)

    def test_tipo_residuo_vazio_invalido(self):
        form = DescarteForm(data=self._dados_validos(tipo_residuo=''))
        self.assertFalse(form.is_valid())
        self.assertIn('tipo_residuo', form.errors)

    def test_tipo_residuo_normalizado_para_title_case(self):
        form = DescarteForm(data=self._dados_validos(tipo_residuo='plástico'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['tipo_residuo'], 'Plástico')

    def test_peso_arredondado_para_2_casas(self):
        # Python usa 'banker's rounding' (arredondamento para o par mais próximo),
        # por isso 1.555 arredonda para 1.55 (não 1.56).
        # O teste valida que o arredondamento ocorre (não que o valor é 1.555).
        form = DescarteForm(data=self._dados_validos(peso_kg=1.555))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['peso_kg'], round(1.555, 2))
