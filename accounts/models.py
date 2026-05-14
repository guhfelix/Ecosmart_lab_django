from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    PAPEL_CHOICES = [
        ('CIDADAO', 'Cidadão'),
        ('GESTOR', 'Gestor Municipal'),
        ('PARCEIRO', 'Parceiro'),
        ('ADMIN', 'Administrador'),
    ]

    nome = models.CharField('Nome completo', max_length=100)
    email = models.EmailField('E-mail', unique=True)

    telefone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        default=''
    )

    papel = models.CharField(
        'Papel',
        max_length=20,
        choices=PAPEL_CHOICES,
        default='CIDADAO'
    )

    saldo_pontos = models.IntegerField('Saldo de Pontos', default=0)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    receber_notificacoes = models.BooleanField(
        'Receber notificações',
        default=True
    )

    raio_busca_km = models.PositiveIntegerField(
        'Raio de busca em km',
        default=5
    )

    consentimento_lgpd_em = models.DateTimeField(
        'Consentimento LGPD em',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.nome} ({self.email})'

    @property
    def is_gestor(self):
        return self.papel in ('GESTOR', 'ADMIN')

    @property
    def is_admin_ecosmart(self):
        return self.papel == 'ADMIN'