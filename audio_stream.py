#!/usr/bin/env python3
import pyaudio


class AudioStream:
    def __init__(self, device_index=3):
        self.CHUNK = 128
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.DEVICE_INDEX = device_index
        self.p = pyaudio.PyAudio()

    def generate_audio(self):
        """Generate WAV audio stream"""
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=512,
            input_device_index=self.DEVICE_INDEX
        )

        # WAV header
        header = bytearray(44)
        header[0:4] = b'RIFF'
        header[4:8] = (0xFFFFFFFF).to_bytes(4, 'little')
        header[8:12] = b'WAVE'
        header[12:16] = b'fmt '
        header[16:20] = (16).to_bytes(4, 'little')
        header[20:22] = (1).to_bytes(2, 'little')
        header[22:24] = (self.CHANNELS).to_bytes(2, 'little')
        header[24:28] = (self.RATE).to_bytes(4, 'little')
        header[28:32] = (self.RATE * self.CHANNELS * 2).to_bytes(4, 'little')
        header[32:34] = (self.CHANNELS * 2).to_bytes(2, 'little')
        header[34:36] = (16).to_bytes(2, 'little')
        header[36:40] = b'data'
        header[40:44] = (0xFFFFFFFF).to_bytes(4, 'little')

        yield bytes(header)

        try:
            while True:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                yield data
        except Exception as e:
            print(f"Audio error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def cleanup(self):
        self.p.terminate()