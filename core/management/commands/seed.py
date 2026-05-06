from django.core.management.base import BaseCommand
from coleta.models import PontoColeta
from recompensas.models import Beneficio


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais do EcoSmart'

    def handle(self, *args, **options):
        # Pontos de Coleta
        if PontoColeta.objects.count() == 0:
            pontos = [
                PontoColeta(
                    nome='Ponto Central',
                    endereco='Praca Central, 123',
                    tipos_aceitos='Plastico, Vidro, Papel, Metal',
                    horario_funcionamento='08h as 17h'
                ),
                PontoColeta(
                    nome='EcoPonto Bairro Verde',
                    endereco='Av. das Arvores, 456',
                    tipos_aceitos='Eletronicos, Pilhas, Baterias',
                    horario_funcionamento='09h as 18h'
                ),
                PontoColeta(
                    nome='Coleta Municipal',
                    endereco='Rua da Prefeitura, 789',
                    tipos_aceitos='Vidro, Metal',
                    horario_funcionamento='07h as 16h'
                ),
            ]
            PontoColeta.objects.bulk_create(pontos)
            self.stdout.write(self.style.SUCCESS(f'  {len(pontos)} pontos de coleta criados.'))
        else:
            self.stdout.write('  Pontos de coleta ja existem, pulando...')

        # Beneficios
        if Beneficio.objects.count() == 0:
            beneficios = [
                Beneficio(
                    nome='Desconto na Conta de Agua',
                    descricao='R$ 20,00 de desconto na proxima fatura de agua.',
                    custo_pontos=100,
                    tipo='DESCONTO'
                ),
                Beneficio(
                    nome='Desconto na Conta de Luz',
                    descricao='R$ 15,00 de desconto na fatura de energia.',
                    custo_pontos=80,
                    tipo='DESCONTO'
                ),
                Beneficio(
                    nome='Voucher em Loja Parceira',
                    descricao='Voucher de R$ 30,00 para compras em parceira local.',
                    custo_pontos=150,
                    tipo='VOUCHER'
                ),
            ]
            Beneficio.objects.bulk_create(beneficios)
            self.stdout.write(self.style.SUCCESS(f'  {len(beneficios)} beneficios criados.'))
        else:
            self.stdout.write('  Beneficios ja existem, pulando...')

        self.stdout.write(self.style.SUCCESS('Seed concluido com sucesso!'))
