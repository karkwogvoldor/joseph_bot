import json
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from nades.models import Mapa, Granada
import zlib, base64

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

        self.stdout.write('✅ JSON extraído com sucesso!')
        props = data.get('props', {})
        page_props = props.get('pageProps', {})
        nades_zipped = page_props.get('nadesZipped', '')
        decoded = base64.b64decode(nades_zipped)
        decompressed = zlib.decompress(decoded, 16 + zlib.MAX_WBITS)
        nades = json.loads(decompressed)
        self.stdout.write(f'Total de granadas: {len(nades)}')
        self.stdout.write(f'Primeira granada: {json.dumps(nades[0], indent=2)}')