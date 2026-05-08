from asgiref.sync import sync_to_async
from nades.models import Granada
from discord.ext import commands
import discord
import os
from urllib.parse import quote
from bot.traducoes import TRADUCOES, NOMES_PT
from nades.models import Granada, Mapa

def traduzir_nome(mapa: str, nome_en: str) -> str:
    return NOMES_PT.get(mapa.lower(), {}).get(nome_en, nome_en)

def resolver_destino(mapa: str, termo: str) -> str:
    mapa_traducoes = TRADUCOES.get(mapa.lower(), {})
    termo_lower = termo.lower()
    
    for destino_en, aliases in mapa_traducoes.items():
        if termo_lower in [a.lower() for a in aliases]:
            return destino_en
    
    return termo

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.command(name='mapas')
async def mapas(ctx):
    buscar = sync_to_async(lambda: list(Mapa.objects.all().values_list('slug', flat=True)))
    mapas = await buscar()
    
    resposta = '🗺️ **Mapas disponíveis:**\n\n'
    for i, m in enumerate(mapas, 1):
        resposta += f'`{i}` - {m}\n'
    
    await ctx.send(resposta)
    
@bot.command(name='tipos')
async def tipos(ctx):
    resposta = '💣 **Tipos de granadas disponíveis:**\n\n'
    resposta += '`1` - 💨 smoke\n'
    resposta += '`2` - ⚡ flash\n'
    resposta += '`3` - 🔥 molotov\n'
    resposta += '`4` - 💥 he\n'
    await ctx.send(resposta)
    
@bot.command(name='help')
async def help_cmd(ctx):
    resposta = '📖 **Comandos disponíveis:**\n'
    resposta += '🕹️ Navegue de forma interativa buscando por número a granada desejada!\n\n'
    resposta += '💨 `!smoke <mapa> <destino>` — busca smokes\n'
    resposta += '⚡ `!flash <mapa> <destino>` — busca flashbangs\n'
    resposta += '🔥 `!molotov <mapa> <destino>` — busca molotovs\n'
    resposta += '💥 `!he <mapa> <destino>` — busca granadas HE\n\n'
    resposta += '🗺️ `!mapas` — lista os mapas disponíveis\n'
    resposta += '💣 `!tipos` — lista os tipos de granadas\n'
    resposta += '📖 `!help` — exibe essa mensagem\n\n'
    resposta += '💡 O `<destino>` é opcional — sem ele o bot lista os destinos disponíveis!\n'
    await ctx.send(resposta)

def formatar_info(granada) -> str:
    info = '📋 **Como executar:**\n'
    
    if granada.model_state:
        info += f'🧍 Posição: {granada.model_state}\n'
    if granada.throw_type:
        info += f'🖱️ Throw: {granada.throw_type}\n'
    if granada.move_keys:
        info += f'⌨️ Teclas: {granada.move_keys}\n'
    if granada.descricao:
        info += f'📝 {granada.descricao}\n'
    
    return info

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    
@bot.command(name='smoke')
async def smoke(ctx, mapa, destino=None):
    await buscar_nade(ctx, mapa, destino, 'smoke')

@bot.command(name='flash')
async def flash(ctx, mapa, destino=None):
    await buscar_nade(ctx, mapa, destino, 'flash')
    
@bot.command(name='he')
async def he(ctx, mapa, destino=None):
    await buscar_nade(ctx, mapa, destino, 'he')
    
@bot.command(name='molotov')
async def molotov(ctx, mapa, destino=None):
    await buscar_nade(ctx, mapa, destino, 'molotov')
    
async def buscar_nade(ctx, mapa: str, destino, tipo):
    if destino is None:
        buscar = sync_to_async(lambda: list(Granada.objects.filter(
            mapa__slug=mapa.lower(),
            tipo=tipo
        ).values_list('destino', flat=True).distinct()))

        destinos = await buscar()

        if not destinos:
            await ctx.send(f'Nenhuma {tipo} encontrada para o mapa **{mapa}**.')
            return

        resposta = f'🟡 **{tipo.capitalize()}s disponíveis no {mapa}:**\n\n'
        for i, d in enumerate(destinos, 1):
            resposta += f'`{i}` - {d}\n'
        resposta += '\nDigite o número do destino:'
        await ctx.send(resposta)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)

            if not msg.content.isdigit():
                await ctx.send('❌ Digite apenas o número da opção.')
                return

            escolha = int(msg.content)

            if escolha < 1 or escolha > len(destinos):
                await ctx.send(f'❌ Opção inválida. Use `!{tipo} {mapa}` para tentar novamente.')
                return

            destino_escolhido = destinos[escolha - 1]

            buscar_origens = sync_to_async(lambda: list(Granada.objects.filter(
                mapa__slug=mapa.lower(),
                tipo=tipo,
                destino__iexact=resolver_destino(mapa, destino_escolhido)
            )))

            resultados = await buscar_origens()
            
            if len(resultados) == 1:
                granada = resultados[0]
                await ctx.send(f'🎬 **{granada.destino}** | {granada.origem} ({granada.lado})')
                await ctx.send(granada.video_url)
                await ctx.send(formatar_info(granada))
                return

            resposta = f'🟡 **{tipo.capitalize()}s para {destino_escolhido} no {mapa}:**\n\n'
            for i, g in enumerate(resultados, 1):
                resposta += f'`{i}` - {g.origem} ({g.lado})\n'
            resposta += '\nDigite o número da opção:'
            await ctx.send(resposta)

            msg2 = await bot.wait_for('message', check=check, timeout=30.0)

            if not msg2.content.isdigit():
                await ctx.send('❌ Digite apenas o número da opção.')
                return

            escolha2 = int(msg2.content)

            if escolha2 < 1 or escolha2 > len(resultados):
                await ctx.send(f'❌ Opção inválida.')
                return

            granada = resultados[escolha2 - 1]
            await ctx.send(f'🎬 **{granada.destino}** | {granada.origem} ({granada.lado})')
            await ctx.send(granada.video_url)
            await ctx.send(formatar_info(granada))

        except TimeoutError:
            await ctx.send(f'⏱️ Tempo esgotado. Use `!{tipo} {mapa}` para tentar novamente.')

    else:
        buscar = sync_to_async(lambda: list(Granada.objects.filter(
            mapa__slug=mapa.lower(),
            tipo=tipo,
            destino__iexact=resolver_destino(mapa, destino)
        )))

        resultados = await buscar()

        if not resultados:
            await ctx.send(f'Nenhuma {tipo} encontrada para **{destino}** no mapa **{mapa}**.')
            return

        resposta = f'🟡 **{tipo.capitalize()}s para {destino} no {mapa}:**\n\n'
        for i, g in enumerate(resultados, 1):
            resposta += f'`{i}` - {g.origem} ({g.lado})\n'
        resposta += '\nDigite o número da opção:'
        await ctx.send(resposta)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)

            if not msg.content.isdigit():
                await ctx.send(f'❌ Digite apenas o número da opção. Use `!{tipo} {mapa} {destino}` para tentar novamente.')
                return

            escolha = int(msg.content)

            if escolha < 1 or escolha > len(resultados):
                await ctx.send(f'❌ Opção inválida. Use `!{tipo} {mapa} {destino}` para tentar novamente.')
                return

            granada = resultados[escolha - 1]
            await ctx.send(f'🎬 **{granada.destino}** | {granada.origem} ({granada.lado})')
            await ctx.send(granada.video_url)
            await ctx.send(formatar_info(granada))

        except TimeoutError:
            await ctx.send(f'⏱️ Tempo esgotado. Use `!{tipo} {mapa} {destino}` para tentar novamente.')