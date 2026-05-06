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
        resposta += f'\n💡 Use `!smoke {mapa} <destino>` para ver as origens!'
        await ctx.send(resposta)

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
        await ctx.send(resposta)