-- character_prompts_v2 테이블 생성
create table if not exists character_prompts_v2 (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    original_id uuid references character_prompts(id),
    name text not null,
    mbti text not null,
    species text not null,
    type text not null,
    voice text,
    greeting text,
    system_prompt text not null,
    character_info jsonb not null,
    
    -- 유니크 제약 조건
    constraint unique_name unique (name),
    constraint unique_original_id unique (original_id)
);

-- RLS 정책 설정
alter table character_prompts_v2 enable row level security;

-- 인증된 사용자는 모든 작업 가능
create policy "인증된 사용자는 모든 작업 가능"
on character_prompts_v2
for all
to authenticated
using (true)
with check (true);

-- 공개 읽기 허용
create policy "누구나 읽기 가능"
on character_prompts_v2
for select
to anon
using (true);

-- 인덱스 생성
create index if not exists idx_character_prompts_v2_name on character_prompts_v2 (name);
create index if not exists idx_character_prompts_v2_mbti on character_prompts_v2 (mbti);
create index if not exists idx_character_prompts_v2_species on character_prompts_v2 (species);

-- 코멘트 추가
comment on table character_prompts_v2 is '캐릭터 프롬프트 v2 - MBTI와 종족 특성이 반영된 개선된 프롬프트';
comment on column character_prompts_v2.id is '고유 식별자';
comment on column character_prompts_v2.created_at is '생성 시간';
comment on column character_prompts_v2.original_id is '원본 character_prompts 테이블의 ID';
comment on column character_prompts_v2.name is '캐릭터 이름';
comment on column character_prompts_v2.mbti is 'MBTI 유형';
comment on column character_prompts_v2.species is '종족';
comment on column character_prompts_v2.type is '캐릭터 타입';
comment on column character_prompts_v2.voice is '말투 스타일';
comment on column character_prompts_v2.greeting is '인사말';
comment on column character_prompts_v2.system_prompt is '시스템 프롬프트';
comment on column character_prompts_v2.character_info is '캐릭터 정보 전체 (JSON)'; 