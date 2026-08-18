from django.db import models


class LetterCategory(models.TextChoices):
    CONVITE = "KVT", "Invitation"
    AUDENCIA = "AUD", "Audience"
    PEDIDU = "PED", "Request (small scale)"
    PROPOSTA = "PRP", "Proposal (large scale)"