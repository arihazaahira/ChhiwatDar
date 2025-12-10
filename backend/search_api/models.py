from django.db import models

class  TranslationRequest(models.Model):
    text = models.TextField()             # le texte à traduire
    translated_text = models.TextField(null=True, blank=True)  # la traduction (optionnelle)
    created_at = models.DateTimeField(auto_now_add=True)       # date creation

    def __str__(self):
        return f"Request {self.id}"
