from django.db import models

class Mapa(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nome
    
class Granada(models.Model):
    TIPO_CHOICES = [
        ('smoke', 'Smoke'),
        ('flash', 'Flash'),
        ('molotov', 'Molotov'),
        ('he', 'HE Grenade'),
    ]

    LADO_CHOICES = [
        ('tr', 'Terrorista'),
        ('ct', 'Contra-Terrorista'),
        ('ambos', 'Ambos'),
    ]

    mapa        = models.ForeignKey(Mapa, on_delete=models.CASCADE)
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
    destino     = models.CharField(max_length=200)
    origem      = models.CharField(max_length=200)
    lado        = models.CharField(max_length=10, choices=LADO_CHOICES)
    video_url   = models.URLField()
    thumbnail   = models.URLField(blank=True)
    origem_url  = models.URLField(blank=True)
    criado_em   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mapa} | {self.tipo} | {self.destino} ({self.origem})"