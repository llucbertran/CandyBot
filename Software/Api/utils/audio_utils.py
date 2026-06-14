from __future__ import annotations
import audioop
from io import BytesIO
import wave

def ensure_mono_wav(audio_bytes: bytes) -> bytes:
    try:
        with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            if channels == 1:
                return audio_bytes
            if channels != 2:
                raise ValueError(
                    f"Unsupported WAV channel count: {channels}. Use mono or stereo."
                )
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
    except wave.Error as exc:
        raise ValueError("Unsupported WAV encoding.") from exc

    try:
        mono_frames = audioop.tomono(frames, sample_width, 0.5, 0.5)
    except audioop.error as exc:
        raise ValueError("Failed to convert WAV to mono.") from exc

    output = BytesIO()
    with wave.open(output, "wb") as wav_out:
        wav_out.setnchannels(1)
        wav_out.setsampwidth(sample_width)
        wav_out.setframerate(framerate)
        wav_out.writeframes(mono_frames)

    return output.getvalue()
