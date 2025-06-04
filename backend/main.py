import sys
import os
import argparse

# ✅ 현재 경로를 Python path에 추가하여 상대 경로 모듈 import 지원
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import logging
logging.getLogger('numba').setLevel(logging.WARNING)

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RoomOutputOptions
from livekit.plugins import openai, deepgram, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from agents.character_loader import load_characters, get_character_by_alias
from utils.prompt_generator import generate_character_prompt
from livekit.agents.stf import FaceAnimatorSTF

load_dotenv()

# ✅ 캐릭터 정보는 환경변수에서 로드
def get_selected_character_from_env():
    return {
        "name": os.environ.get("CHARACTER_NAME", "하루"),
        "greeting": os.environ.get("CHARACTER_GREETING", "안녕하세요!"),
        "voice": os.environ.get("CHARACTER_VOICE", "nova"),
        "type": os.environ.get("CHARACTER_TYPE", ""),
        "mbti": os.environ.get("CHARACTER_MBTI", ""),
        "species": os.environ.get("CHARACTER_SPECIES", "")
    }

# ✅ 에이전트 정의
class Assistant(Agent):
    def __init__(self, character: dict) -> None:
        instructions = generate_character_prompt(character)
        super().__init__(instructions=instructions)

# ✅ 세션 시작
async def entrypoint(ctx: agents.JobContext):
    try:
        print("🔵 [1] LiveKit 서버 연결 중...")
        await ctx.connect()

        selected_character = get_selected_character_from_env()

        print("🔵 [2] Deepgram STT 초기화 중...")
        stt = deepgram.STT(model="enhanced", language="ko")

        print("🔵 [3] OpenAI LLM 초기화 중...")
        llm = openai.LLM(model="gpt-4o-mini")

        print("🔵 [4] OpenAI TTS 초기화 중...")
        tts_model = openai.TTS(voice=selected_character["voice"])

        print("🔵 [5] STF 초기화 중...")
        stf = FaceAnimatorSTF(chunk_duration_sec=1.0)

        print("🔵 [6] Silero VAD 로딩 중...")
        vad = silero.VAD.load()

        print("🔵 [7] Turn Detector 초기화 중...")
        turn_detector = MultilingualModel()

        print("🔵 [8] AgentSession 생성 중...")
        session = AgentSession(
            stt=stt,
            llm=llm,
            tts=tts_model,
            stf=stf,
            vad=vad,
            turn_detection=turn_detector
        )

        print("🟢 [9] 세션 시작 중...")
        participant = await ctx.wait_for_participant()

        await session.start(
            room=ctx.room,
            agent=Assistant(selected_character),
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
                participant_identity=participant.identity
            ),
            room_output_options=RoomOutputOptions(
                audio_enabled=True,
                transcription_enabled=True,
                animation_enabled=True,
            )
        )

        print("🟢 [10] 인사말 전송 중...")
        await session.generate_reply(
            instructions=selected_character["greeting"]
        )

        print("✅ [완료] 에이전트 세션이 정상적으로 시작되었습니다.")

    except Exception as e:
        print("❌ [오류 발생] entrypoint 내에서 예외 발생:")
        print(e)

# ✅ CLI 실행 진입점
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="LiveKit 명령어 (dev/start/download-files 등)")
    parser.add_argument("--room", help="방 이름 (예: upstage_dev_room1)")
    parser.add_argument("--character", help="캐릭터 alias (예: haru, rex, doji 등)")
    args = parser.parse_args()

    # ✅ 캐릭터 로딩은 agent 실행일 때만 수행
    if args.command != "download-files":
        if not args.character:
            print("❌ --character 인자가 필요합니다.")
            sys.exit(1)

        characters = load_characters()
        try:
            selected_character = get_character_by_alias(args.character, characters)
        except ValueError as e:
            print(e)
            print("가능한 캐릭터 alias 목록:", ", ".join([c["alias"] for c in characters]))
            sys.exit(1)

        # 캐릭터 정보를 환경변수로 설정
        os.environ["CHARACTER_NAME"] = selected_character["name"]
        os.environ["CHARACTER_GREETING"] = selected_character.get("greeting") or "안녕하세요!"
        os.environ["CHARACTER_VOICE"] = selected_character.get("voice") or "nova"
        os.environ["CHARACTER_TYPE"] = selected_character.get("type") or ""
        os.environ["CHARACTER_MBTI"] = selected_character.get("mbti") or ""
        os.environ["CHARACTER_SPECIES"] = selected_character.get("species") or ""

    # ✅ LiveKit CLI 명령 실행
    if args.command == "dev":
        sys.argv = [sys.argv[0]] + [args.command]
    elif args.command == "connect":
        sys.argv = [sys.argv[0]] + [args.command, "--room", args.room]
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
