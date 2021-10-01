from django.db import models
from django.utils.timezone import now


class Language(models.Model):
    English = 'en'
    Germany = 'de'
    LANGUAGECHOICE = [
        (English, 'English'),
        (Germany, 'German'),
    ]
    language_code = models.CharField(max_length=11, choices=LANGUAGECHOICE, default = English)
    sample_text = models.TextField(max_length=100,null=True,blank=True)
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.language_code)



class Translator(models.Model):
    language = models.ForeignKey(Language ,on_delete=models.CASCADE,null=True, blank=False)
    text = models.TextField(max_length=100)

    def __str__(self):
        return str(self.language)