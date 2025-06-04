from datasets import load_dataset
import json
import os
from tqdm import tqdm  # ✅ tqdm import

# 🔹 데이터셋 로드
dataset = load_dataset("heegyu/namuwiki", split="train")

# 🔹 저장 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = os.path.join(BASE_DIR, "data", "species", "namuwiki_species.json")
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

# 🔹 데이터 미리보기
print(f"✅ 전체 문서 수: {len(dataset)}")
print("📝 예시:")
print(dataset[0])

# 🔹 tqdm으로 딕셔너리 형태 저장
processed_dict = {}
for entry in tqdm(dataset, desc="🔄 변환 중"):
    title = entry["title"]
    text = entry["text"]
    if title and text:
        processed_dict[title] = text

# 🔹 저장
with open(SAVE_PATH, "w", encoding="utf-8") as f:
    json.dump(processed_dict, f, ensure_ascii=False, indent=2)

print(f"✅ 저장 완료: {SAVE_PATH}")
