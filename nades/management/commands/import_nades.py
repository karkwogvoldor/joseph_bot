import json
import zlib
import base64
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from nades.models import Mapa, Granada

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

class Command(BaseCommand):
    help = 'Importa granadas do csnades.app'

    def add_arguments(self, parser):
        parser.add_argument('--mapa', type=str, required=True)

    def handle(self, *args, **options):
        mapa_slug = options['mapa'].lower()
        url = f'https://csnades.app/{mapa_slug}'

        self.stdout.write(f'🔍 Buscando granadas de {mapa_slug}...')

        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        tag = soup.find('script', id='__NEXT_DATA__')

        if not tag:
            self.stdout.write('❌ __NEXT_DATA__ não encontrado.')
            return

        data = json.loads(tag.string)
        page_props = data['props']['pageProps']
        nades_zipped = page_props.get('nadesZipped', '')

        decoded = base64.b64decode(nades_zipped)
        decompressed = zlib.decompress(decoded, 16 + zlib.MAX_WBITS)
        nades = json.loads(decompressed)

        self.stdout.write(f'✅ {len(nades)} granadas encontradas!')

        mapa_obj, _ = Mapa.objects.get_or_create(
            slug=mapa_slug,
            defaults={'nome': mapa_slug.capitalize()}
        )

        criadas = 0
        ignoradas = 0

        for nade in nades:
            try:
                nade_data = nade.get('nadeData', {})

                tipo        = nade_data.get('nadeType', '')
                destino     = (nade_data.get('target') or {}).get('targetDisplayName') or ''
                origem      = (nade_data.get('origin') or {}).get('originDisplayName') or ''
                lado        = nade_data.get('baseTeam', '')
                posicao     = nade_data.get('setPos', '')
                model_state = nade_data.get('modelState', '')
                throw_type  = nade_data.get('throwType', '')
                descricao   = nade.get('description', '')

                videos = nade.get('videos', [])
                video_url = videos[0]['url'] if videos else ''

                moments = nade.get('moments', [])
                thumbnail = ''
                if moments:
                    spot = moments[0].get('spot', [])
                    if spot:
                        variants = spot[0].get('variants', [])
                        if variants:
                            thumbnail = variants[0]['data'].get('jpg', '')

                origem_url = f"https://csnades.app{nade.get('urlTitleName', '')}"

                if not destino or not video_url:
                    ignoradas += 1
                    continue

                Granada.objects.get_or_create(
                    mapa=mapa_obj,
                    tipo=tipo,
                    destino=destino,
                    origem=origem,
                    defaults={
                        'lado':        lado,
                        'video_url':   video_url,
                        'thumbnail':   thumbnail,
                        'origem_url':  origem_url,
                        'posicao':     posicao,
                        'model_state': model_state,
                        'throw_type':  throw_type,
                    }
                )
                criadas += 1

            except Exception as e:
                self.stdout.write(f'⚠️  Erro em uma granada: {e}')
                continue

        self.stdout.write(f'✅ {criadas} granadas salvas!')
        self.stdout.write(f'⚠️  {ignoradas} granadas ignoradas (sem destino ou vídeo)')