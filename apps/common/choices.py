from django.db import models


class LetterCategory(models.TextChoices):
    CONVITE = "KVT", "Konvite"
    AUDENCIA = "AUD", "Audensia"
    PEDIDU = "PED", "Pedidu (skala kiik)"
    PROPOSTA = "PRP", "Proposta (skala boot)"