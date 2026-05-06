from django.db import models
from django.conf import settings


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

    def save(self, *args, **kwargs):
        if not self.pontos_gerados:
            self.pontos_gerados = int(self.peso_kg * 10)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.usuario} — {self.tipo_residuo} ({self.peso_kg}kg)'
