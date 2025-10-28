import whisper

model = whisper.load_model("base")
result = model.transcribe("/Users/nishanyueksel/Downloads/test_audio1.mp3")
print(result["text"])
