import random
import string

from django.conf import settings
from django.db import models, transaction


class Beneficio(models.Model):
    TIPO_CHOICES = [
        ('DESCONTO', 'Desconto'),
        ('VOUCHER', 'Voucher'),
        ('OUTRO', 'Outro'),
    ]

    nome = models.CharField('Nome', max_length=120)
    descricao = models.TextField('Descrição', blank=True, default='')
    custo_pontos = models.IntegerField('Custo em Pontos')
    tipo = models.CharField('Tipo', max_length=50, choices=TIPO_CHOICES, blank=True, default='')
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Benefício'
        verbose_name_plural = 'Benefícios'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.custo_pontos} pts)'

    def resgatar_para_usuario(self, usuario):
        """
        Encapsula toda a lógica de negócio do resgate de benefício.

        Verifica o saldo, deduz os pontos e cria o registro de Resgate
        dentro de uma transação atómica, garantindo que os dados nunca
        ficam em estado inconsistente em caso de erro.

        Args:
            usuario: instância do modelo Usuario (AUTH_USER_MODEL)

        Returns:
            Resgate: o objeto de resgate criado com sucesso

        Raises:
            ValueError: se o saldo do utilizador for insuficiente
            ValueError: se o benefício estiver inativo
        """
        if not self.ativo:
            raise ValueError(f"O benefício '{self.nome}' não está disponível.")

        if usuario.saldo_pontos < self.custo_pontos:
            raise ValueError(
                f"Saldo insuficiente. Você tem {usuario.saldo_pontos} pontos "
                f"e este benefício custa {self.custo_pontos} pontos."
            )

        codigo = 'ECO-' + ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )

        with transaction.atomic():
            # Usa select_for_update para evitar condição de corrida
            # em ambientes com múltiplos utilizadores simultâneos
            usuario_lock = (
                usuario.__class__.objects
                .select_for_update()
                .get(pk=usuario.pk)
            )

            # Verifica novamente após obter o lock
            if usuario_lock.saldo_pontos < self.custo_pontos:
                raise ValueError(
                    f"Saldo insuficiente. Você tem {usuario_lock.saldo_pontos} pontos "
                    f"e este benefício custa {self.custo_pontos} pontos."
                )

            usuario_lock.saldo_pontos -= self.custo_pontos
            usuario_lock.save(update_fields=['saldo_pontos'])

            resgate = Resgate.objects.create(
                usuario=usuario_lock,
                beneficio=self,
                pontos_utilizados=self.custo_pontos,
                codigo_voucher=codigo,
                status='ATIVO',
            )

        # Atualiza o objeto em memória para refletir o novo saldo
        usuario.saldo_pontos = usuario_lock.saldo_pontos

        return resgate


class Resgate(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('USADO', 'Usado'),
        ('EXPIRADO', 'Expirado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resgates',
        verbose_name='Usuário'
    )
    beneficio = models.ForeignKey(
        Beneficio,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resgates',
        verbose_name='Benefício'
    )
    data_resgate = models.DateTimeField('Data do Resgate', auto_now_add=True)
    pontos_utilizados = models.IntegerField('Pontos Utilizados')
    codigo_voucher = models.CharField('Código do Voucher', max_length=50)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ATIVO')

    class Meta:
        verbose_name = 'Resgate'
        verbose_name_plural = 'Resgates'
        ordering = ['-data_resgate']

    def __str__(self):
        return f'{self.usuario} — {self.beneficio} ({self.codigo_voucher})'


class Auditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias',
        verbose_name='Usuário'
    )
    acao = models.CharField('Ação', max_length=255)
    data = models.DateTimeField('Data', auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Auditoria'
        verbose_name_plural = 'Registros de Auditoria'
        ordering = ['-data']

    def __str__(self):
        return f'[{self.data}] {self.usuario}: {self.acao}'
