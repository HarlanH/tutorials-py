"""Voice date agent: speak a date question, hear the answer.

The agent listens via the microphone, transcribes with faster-whisper,
runs the DateAgent, and speaks the result via the macOS `say` command
(or pyttsx3 on other platforms).

Usage:
    uv run main.py          # live mic input, one question per Enter press
    uv run main.py --demo   # run pre-set questions without the mic
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

from date_agent import DateAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

MODEL = "qwen2.5-coder:7b"
SAMPLE_RATE = 16_000
RECORD_SECONDS = 15
WHISPER_MODEL = "tiny.en"

DEMO_QUESTIONS = [
    "What day is next Tuesday?",
    "When is the last Sunday of next month?",
    "How many days until Christmas?",
    "What date is two weeks from today?",
]


def date_context() -> str:
    from datetime import date
    today = date.today()
    return f"Today is {today.strftime('%A, %B')} {today.day} {today.year}."


def speak(text: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["say", "-v", "Ava", text])
    else:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.say(text)
        engine.runAndWait()


def listen(whisper: WhisperModel) -> str:
    print(f"  Listening for {RECORD_SECONDS} seconds...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    try:
        sf.write(tmp, audio, SAMPLE_RATE)
        segments, _ = whisper.transcribe(tmp, language="en")
        text = " ".join(s.text for s in segments).strip()
    finally:
        os.unlink(tmp)
    return text


def run_question(question: str, agent: DateAgent) -> None:
    print(f"\nQuestion: {question}")

    prompt = f"{date_context()}\n\n{question}"
    result = agent.seek(prompt)

    answer = result.final_answer or "Sorry, I could not work that out."
    for i, it in enumerate(result.iterations, 1):
        print(f"  Iteration {i}: {it.plan_result.plan.strip()}")
    print(f"Answer:   {answer}")
    speak(answer)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run pre-set questions without mic")
    args = parser.parse_args()

    if not check_ollama(MODEL):
        sys.exit(1)

    llm = LLMConfig(provider="ollama", model=MODEL)
    whisper = None if args.demo else WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

    print("Voice Date Agent")
    print("=" * 40)

    if args.demo:
        for question in DEMO_QUESTIONS:
            agent = DateAgent(llm=llm)
            run_question(question, agent)
    else:
        print("Press Enter to ask a question (Ctrl+C to quit).")
        while True:
            try:
                input("\n[Press Enter to speak]")
                text = listen(whisper)
                if not text:
                    print("  (nothing heard, try again)")
                    continue
                agent = DateAgent(llm=llm)
                run_question(text, agent)
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break


if __name__ == "__main__":
    main()
