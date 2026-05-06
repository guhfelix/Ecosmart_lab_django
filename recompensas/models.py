from django.db import models
from django.conf import settings


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
