from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Inicia o bot do Discord'

    def handle(self, *args, **kwargs):
        from bot.bot import bot
        import os
        bot.run(os.getenv('DISCORD_TOKEN'))