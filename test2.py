import parselmouth
sound = parselmouth.Sound(r"C:\Users\oskar\PycharmProjects\SoundAnalizer\media\audio_2021_08_10_14_48_02.wav")
pitch = sound.to_pitch()
pulses = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

n_pulses = parselmouth.praat.call(pulses, "Get number of points")
n_periods = parselmouth.praat.call(pulses, "Get number of periods", 0.0, 0.0, 0.0001, 0.02, 1.3)
shimmer_local = parselmouth.praat.call([sound, pulses], "Get shimmer (local)...", 0.0, 0.0, 0.0001, 0.02, 1.3, 1.6)
voice_report_str = parselmouth.praat.call([sound, pitch, pulses], "Voice report", 0.0, 0.0, 75, 600, 1.3, 1.6, 0.03, 0.45)

max_voiced_period = 0.02  # This is the "longest period" parameter in some of the other queries
periods = [parselmouth.praat.call(pulses, "Get time from index", i+1) -
           parselmouth.praat.call(pulses, "Get time from index", i)
           for i in range(1, n_pulses)]
#Wysokość Głosu
mean_pitch = parselmouth.praat.call(pitch, "Get mean", 0.0, 0.0, "Hertz")
#ilosc łamań głosu
degree_of_voice_breaks = sum(period for period in periods if period > max_voiced_period) / sound.duration

parselmouth.praat.call(pitch, "Get quantile", 0.0, 0.0, 0.5, "Hertz")

print(voice_report_str)
print(shimmer_local)