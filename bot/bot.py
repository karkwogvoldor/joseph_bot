from asgiref.sync import sync_to_async
from nades.models import Granada
from discord.ext import commands
import discord
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command(name='smoke')
async def smoke(ctx, mapa: str, destino: str = None):
    if destino is None:
        buscar = sync_to_async(lambda: list(Granada.objects.filter(
            mapa__slug=mapa.lower(),
            tipo='smoke'
        ).values_list('destino', flat=True).distinct()))

        destinos = await buscar()

        if not destinos:
            await ctx.send(f'Nenhuma smoke encontrada para o mapa **{mapa}**.')
            return

        resposta = f'🟡 **Smokes disponíveis no {mapa}:**\n\n'
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
                await ctx.send(f'❌ Opção inválida. Use `!smoke {mapa}` para tentar novamente.')
                return

            destino_escolhido = destinos[escolha - 1]

            buscar_origens = sync_to_async(lambda: list(Granada.objects.filter(
                mapa__slug=mapa.lower(),
                tipo='smoke',
                destino__iexact=destino_escolhido
            )))

            resultados = await buscar_origens()
            
            if len(resultados) == 1:
                granada = resultados[0]
                await ctx.send(f'🎬 **{granada.destino}** | {granada.origem} ({granada.lado})\n{granada.video_url}')
                return

            resposta = f'🟡 **Smokes para {destino_escolhido} no {mapa}:**\n\n'
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
            await ctx.send(f'🎬 **{granada.destino}** | {granada.origem} ({granada.lado})\n{granada.video_url}')

        except TimeoutError:
            await ctx.send(f'⏱️ Tempo esgotado. Use `!smoke {mapa}` para tentar novamente.')

    else:
        buscar = sync_to_async(lambda: list(Granada.objects.filter(
            mapa__slug=mapa.lower(),
            tipo='smoke',
            destino__iexact=destino.lower()
        )))

        resultados = await buscar()

        if not resultados:
            await ctx.send(f'Nenhuma smoke encontrada para **{destino}** no mapa **{mapa}**.')
            return

        resposta = f'🟡 **Smokes para {destino} no {mapa}:**\n\n'
        for i, g in enumerate(resultados, 1):
            resposta += f'`{i}` - {g.origem} ({g.lado})\n'
        resposta += '\nDigite o número da opção:'
        await ctx.send(resposta)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)

            if not msg.content.isdigit():
                await ctx.send('❌ Digite apenas o número da opção. Use `!smoke {mapa} {destino}` para tentar novamente.')
                return

            escolha = int(msg.content)

            if escolha < 1 or escolha > len(resultados):
                await ctx.send(f'❌ Opção inválida. Use `!smoke {mapa} {destino}` para tentar novamente.')
                return

            granada = resultados[escolha - 1]
            await ctx.send(f'🎬 **{granada.destino}** | {granada.origem} ({granada.lado})\n{granada.video_url}')

        except TimeoutError:
            await ctx.send('⏱️ Tempo esgotado. Use `!smoke {mapa} {destino}` para tentar novamente.')