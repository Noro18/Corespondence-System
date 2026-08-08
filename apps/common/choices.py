from django.db import models


class LetterCategory(models.TextChoices):
    ASSUNTO = "ASU", "Asuntu"
    INFORMACAO = "INF", "Informasaun"
    CONVITE = "KVT", "Konvite"
