from django.test import TestCase

from accounts.models import Usuario
from recompensas.models import Beneficio, Resgate


def criar_usuario(email='teste@ecosmart.com', saldo=100):
    """Helper para criar utilizador de teste com saldo inicial."""
    return Usuario.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='senha123',
        nome='Utilizador Teste',
        saldo_pontos=saldo,
    )


def criar_beneficio(nome='Desconto Água', custo=50, ativo=True):
    """Helper para criar benefício de teste."""
    return Beneficio.objects.create(
        nome=nome,
        descricao='Desconto na conta de água.',
        custo_pontos=custo,
        tipo='DESCONTO',
        ativo=ativo,
    )


# ─────────────────────────────────────────────────────────────────
# Testes do Modelo Beneficio — método resgatar_para_usuario()
# ─────────────────────────────────────────────────────────────────

class BeneficioResgateTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario(saldo=100)
        self.beneficio = criar_beneficio(custo=50)

    def test_resgate_bem_sucedido_cria_registro(self):
        """Um resgate válido deve criar um objeto Resgate na base de dados."""
        resgate = self.beneficio.resgatar_para_usuario(self.usuario)
        self.assertIsNotNone(resgate.pk)
        self.assertEqual(Resgate.objects.count(), 1)

    def test_resgate_deduz_saldo_do_usuario(self):
        """Após o resgate, o saldo do utilizador deve ser reduzido."""
        self.beneficio.resgatar_para_usuario(self.usuario)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.saldo_pontos, 50)  # 100 - 50

    def test_resgate_gera_codigo_voucher(self):
        """O voucher gerado deve começar com 'ECO-' e ter 12 caracteres."""
        resgate = self.beneficio.resgatar_para_usuario(self.usuario)
        self.assertTrue(resgate.codigo_voucher.startswith('ECO-'))
        self.assertEqual(len(resgate.codigo_voucher), 12)  # 'ECO-' + 8 chars

    def test_resgate_com_saldo_insuficiente_lanca_excecao(self):
        """Tentar resgatar sem saldo suficiente deve lançar ValueError."""
        usuario_pobre = criar_usuario(email='pobre@ecosmart.com', saldo=10)
        with self.assertRaises(ValueError) as ctx:
            self.beneficio.resgatar_para_usuario(usuario_pobre)
        self.assertIn('Saldo insuficiente', str(ctx.exception))

    def test_resgate_com_saldo_insuficiente_nao_altera_saldo(self):
        """Falha no resgate não deve alterar o saldo do utilizador."""
        usuario_pobre = criar_usuario(email='pobre2@ecosmart.com', saldo=10)
        try:
            self.beneficio.resgatar_para_usuario(usuario_pobre)
        except ValueError:
            pass
        usuario_pobre.refresh_from_db()
        self.assertEqual(usuario_pobre.saldo_pontos, 10)

    def test_resgate_com_saldo_insuficiente_nao_cria_registro(self):
        """Falha no resgate não deve criar nenhum Resgate na base de dados."""
        usuario_pobre = criar_usuario(email='pobre3@ecosmart.com', saldo=10)
        try:
            self.beneficio.resgatar_para_usuario(usuario_pobre)
        except ValueError:
            pass
        self.assertEqual(Resgate.objects.count(), 0)

    def test_resgate_de_beneficio_inativo_lanca_excecao(self):
        """Tentar resgatar um benefício inativo deve lançar ValueError."""
        beneficio_inativo = criar_beneficio(nome='Inativo', custo=10, ativo=False)
        with self.assertRaises(ValueError) as ctx:
            beneficio_inativo.resgatar_para_usuario(self.usuario)
        self.assertIn('não está disponível', str(ctx.exception))

    def test_resgate_com_saldo_exato_funciona(self):
        """Utilizador com saldo exatamente igual ao custo deve conseguir resgatar."""
        usuario_exato = criar_usuario(email='exato@ecosmart.com', saldo=50)
        resgate = self.beneficio.resgatar_para_usuario(usuario_exato)
        usuario_exato.refresh_from_db()
        self.assertEqual(usuario_exato.saldo_pontos, 0)
        self.assertIsNotNone(resgate.pk)

    def test_dois_resgates_acumulam_deducao(self):
        """Dois resgates consecutivos devem deduzir o saldo corretamente."""
        usuario = criar_usuario(email='rico@ecosmart.com', saldo=200)
        self.beneficio.resgatar_para_usuario(usuario)
        self.beneficio.resgatar_para_usuario(usuario)
        usuario.refresh_from_db()
        self.assertEqual(usuario.saldo_pontos, 100)  # 200 - 50 - 50


# ─────────────────────────────────────────────────────────────────
# Testes do Formulário RegistroForm
# ─────────────────────────────────────────────────────────────────

class RegistroFormTest(TestCase):

    def _dados_validos(self, **override):
        from accounts.forms import RegistroForm
        dados = {
            'nome': 'João Silva',
            'email': 'joao@ecosmart.com',
            'password1': 'SenhaForte@2026',
            'password2': 'SenhaForte@2026',
        }
        dados.update(override)
        return dados

    def _form(self, **override):
        from accounts.forms import RegistroForm
        return RegistroForm(data=self._dados_validos(**override))

    def test_formulario_valido(self):
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)

    def test_nome_sem_sobrenome_invalido(self):
        form = self._form(nome='João')
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_nome_com_numeros_invalido(self):
        form = self._form(nome='João123 Silva')
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_nome_normalizado_para_title_case(self):
        form = self._form(nome='joão silva')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['nome'], 'João Silva')

    def test_email_duplicado_invalido(self):
        """Registar com e-mail já existente deve ser inválido."""
        Usuario.objects.create_user(
            username='joao', email='joao@ecosmart.com',
            password='qualquer', nome='João Existente',
        )
        form = self._form()
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_email_normalizado_para_minusculas(self):
        form = self._form(email='JOAO@ECOSMART.COM')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'joao@ecosmart.com')
