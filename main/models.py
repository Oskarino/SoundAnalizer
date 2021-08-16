from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Audio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField()
    duration = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    mean_pitch = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    minimum_pitch = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    maximum_pitch = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    number_of_pulses = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    number_of_periods = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    number_of_voice_breaks = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    degree_of_voice_breaks = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    jitter = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    shimmer = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    mean_autocorrelation = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    mean_noise_th_ratio = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    mean_harmonics_tr_ratio = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    created_at = models.DateTimeField()
    class Meta:
        verbose_name = "Plik Audio"
        verbose_name_plural = "Pliki Audio"

    def __str__(self):
        return '<audio id={}>'.format(self.id)

