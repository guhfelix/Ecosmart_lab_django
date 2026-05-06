from django.conf import settings
from django.db import models, transaction


class PontoColeta(models.Model):
    nome = models.CharField('Nome', max_length=120)
    endereco = models.CharField('Endereço', max_length=255)
    telefone = models.CharField('Telefone', max_length=20, blank=True, default='')
    descricao = models.TextField('Descrição', blank=True, default='')
    tipos_aceitos = models.CharField('Tipos Aceitos', max_length=255)
    horario_funcionamento = models.CharField(
        'Horário de Funcionamento', max_length=120, blank=True, default=''
    )
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)

    class Meta:
        verbose_name = 'Ponto de Coleta'
        verbose_name_plural = 'Pontos de Coleta'
        ordering = ['nome']

    def tipos_aceitos_list(self):
        if not self.tipos_aceitos:
            return []
        return [tipo.strip() for tipo in self.tipos_aceitos.split(',') if tipo.strip()]

    def __str__(self):
        return self.nome


class Descarte(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='descartes',
        verbose_name='Usuário'
    )
    ponto = models.ForeignKey(
        PontoColeta,
        on_delete=models.SET_NULL,
        null=True,
        related_name='descartes',
        verbose_name='Ponto de Coleta'
    )
    data_hora = models.DateTimeField('Data/Hora', auto_now_add=True)
    tipo_residuo = models.CharField('Tipo de Resíduo', max_length=50)
    peso_kg = models.FloatField('Peso (kg)')
    pontos_gerados = models.IntegerField('Pontos Gerados', default=0)

    class Meta:
        verbose_name = 'Descarte'
        verbose_name_plural = 'Descartes'
        ordering = ['-data_hora']

    def calcular_pontos(self):
        """
        Regra de negócio central: 1 kg de resíduo = 10 pontos.
        Centralizada aqui para garantir consistência em toda a aplicação.
        """
        return int(self.peso_kg * 10)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o save() para garantir que:
        1. Os pontos gerados são sempre calculados automaticamente.
        2. O saldo do utilizador é atualizado na mesma transação atómica,
           evitando inconsistências caso o save() falhe a meio.
        """
        is_new = self.pk is None  # True apenas na criação, não em edições

        if is_new:
            self.pontos_gerados = self.calcular_pontos()

        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_new and self.usuario_id:
                # Usa F() + update() para evitar condições de corrida
                # e garantir que apenas o campo saldo_pontos é alterado
                type(self.usuario).objects.filter(pk=self.usuario_id).update(
                    saldo_pontos=models.F('saldo_pontos') + self.pontos_gerados
                )

    def __str__(self):
        return f'{self.usuario} — {self.tipo_residuo} ({self.peso_kg}kg)'
