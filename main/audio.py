import re
import parselmouth
from decimal import Decimal

from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings

from main.models import Audio


def _parse_number(pattern, content):
    result = re.search(pattern, content)
    if result:
        return Decimal(result.group(1))
    return None


def parse_report(content):
    return {
        'duration': _parse_number(r'[(]duration: (.+) seconds[)]', content),
        'mean_pitch': _parse_number(r'Mean pitch: (.+) Hz', content),
        'minimum_pitch': _parse_number(r'Minimum pitch: (.+) Hz', content),
        'maximum_pitch': _parse_number(r'Maximum pitch: (.+) Hz', content),
        'number_of_pulses': _parse_number(r'Number of pulses: (.+)', content),
        'number_of_periods': _parse_number(r'Number of periods: (.+)', content),
        'number_of_voice_breaks': _parse_number(r'Number of voice breaks: (.+)', content),
        'degree_of_voice_breaks': _parse_number(r'Degree of voice breaks: (.+)%', content),
        'jitter': _parse_number(r'Jitter [(]local[)]: (.+)%', content),
        'shimmer': _parse_number(r'Shimmer [(]local[)]: (.+)%', content),
        'mean_autocorrelation': _parse_number(r'Mean noise-to-harmonics ratio: (.+)', content),
        'mean_noise_th_ratio': _parse_number(r' Mean autocorrelation: (.+)', content),
        'mean_harmonics_tr_ratio': _parse_number(r'Mean harmonics-to-noise ratio: (.+) dB', content)
    }


def analyze(filename):
    sound = parselmouth.Sound(filename)
    pitch = sound.to_pitch()
    pulses = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")
    report = parselmouth.praat.call([sound, pitch, pulses], "Voice report", 0.0, 0.0, 75, 600, 1.3, 1.6, 0.03, 0.45)
    return parse_report(report)



def _make_file_name(now):
    return "audio_" + now.strftime("%Y_%m_%d_%H_%M_%S") + ".wav"


def process_user_file(file, user):
    now = timezone.now()
    file.name = _make_file_name(now)
    audio = Audio.objects.create(
        user=user,
        file=file,
        created_at=now,

    )
    details = analyze(audio.file.path)
    #file_name = str(settings.MEDIA_ROOT / default_storage.save(_make_file_name(now), file))
    Audio.objects.filter(id=audio.id).update(**details)
    return audio