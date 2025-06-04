-- 새로운 프롬프트를 저장할 컬럼 추가
alter table character_prompts
add column if not exists system_prompt_v2 text;

-- 컬럼 설명 추가
comment on column character_prompts.system_prompt_v2 is 'MBTI와 종족 특성이 반영된 개선된 프롬프트'; 