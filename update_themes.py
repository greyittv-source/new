import sys

new_themes = '''THEMES = [
    {
        "day": 1,
        "name": "Cozy Rain Cafe",
        "music_prompt": "A cozy lo-fi hip hop track with soft melancholic piano chords, gentle rain tapping on a window, and warm ambient coffee shop atmosphere.",
        "image_prompt": "A cozy window-side seat in a coffee shop, rainy day, soft warm lighting, a hot cup of coffee with steam on the table, a sleeping cat curled up on a chair, aesthetic lofi artwork, 16:9 aspect ratio.",
        "sub_text": "Rainy Cafe Lofi Beats 🌧️",
        "title": "비 오는 날 당신의 감정을 다독여줄 조용한 카페 🌧️ | 번아웃 수면 유도 Lofi",
        "description": "On days when your head is heavy with complex thoughts, sit by the window of a rainy cafe and let your mind rest to the sound of rain and piano melodies. Your day was absolutely wonderful.\\n-\\n복잡한 생각들로 머리가 무거운 날, 비 오는 카페 창가 자리에 앉아 빗소리와 피아노 선율에 마음을 내려놓으세요. 당신의 하루는 충분히 훌륭했습니다.",
        "pinned_comment": "오늘 하루도 정말 고생 많으셨습니다. 지금 어떤 고민 때문에 밤을 지새우고 계시나요? 이곳에 편하게 털어놓고 가벼운 마음으로 잠드셨으면 좋겠습니다."
    },
    {
        "day": 2,
        "name": "Midnight Library",
        "music_prompt": "A mellow lo-fi study track featuring a slow acoustic nylon guitar melody, soft vinyl crackles, and quiet pages turning sounds.",
        "image_prompt": "A quiet vintage library at midnight, warm desk lamp illuminating open books, cozy leather armchair, a small glowing neon sign saying 'Greyit', soft glowing bokeh, aesthetic lofi artwork, 16:9 aspect ratio.",
        "sub_text": "Midnight Study Lofi 🌙",
        "title": "모두가 잠든 새벽 3시, 생각에 잠겨 듣는 도서관 Lofi 🌙 | 불면증, 공부 집중",
        "description": "In the quiet midnight library with no one around, this dreamy lofi beat is perfect to listen to while turning the pages under the soft desk lamp.\\n-\\n아무도 없는 고요한 심야의 도서관, 은은한 스탠드 조명 아래서 책장을 넘기며 듣기 좋은 몽환적인 감성 Lofi 비트입니다.",
        "pinned_comment": "새벽에 깨어계시는군요. 지금 어떤 공부를 하고 계시거나, 어떤 상상을 하고 계시나요? 당신의 꿈을 응원합니다. 🌙"
    },
    {
        "day": 3,
        "name": "Sunny Bedroom",
        "music_prompt": "An upbeat and heartwarming lo-fi track with a sunny electric piano riff, birds chirping softly, and a relaxed bedroom groove.",
        "image_prompt": "A bright cozy bedroom on a sunny Sunday morning, warm golden sunlight rays streaming through a large window, a small glowing neon sign saying 'Greyit' on the wall, aesthetic green house plants, pastel colors, 16:9 aspect ratio.",
        "sub_text": "Sunny Sunday Lofi ☕",
        "title": "지친 몸을 일으켜줄 따뜻한 일요일 아침 햇살 ☕ | 우울함 타파 기분전환 Lofi",
        "description": "On mornings when it's hard to get out of bed, this warm lofi music with pleasant piano melodies and birdsong will breathe a little energy into your day.\\n-\\n이불 밖으로 나오기 힘든 아침, 기분 좋은 피아노 선율과 새소리로 당신의 하루에 작은 활력을 불어넣어 줄 따뜻한 Lofi 음악입니다.",
        "pinned_comment": "기분 좋은 아침, 혹은 느긋한 오후입니다. 오늘 하루 나를 위해 해주고 싶은 작은 선물이 있다면 무엇인가요? ☕"
    },
    {
        "day": 4,
        "name": "Forest Log Cabin",
        "music_prompt": "A warm and peaceful lo-fi track with acoustic guitar strums, the comforting sound of a crackling fireplace, and cozy winter wind outside.",
        "image_prompt": "A cozy wooden log cabin interior, a stone fireplace with a bright crackling fire, comfortable armchairs, a sleeping cat on the rug, a window showing a snowy pine forest, 16:9 aspect ratio.",
        "sub_text": "Cabin Fireplace Lofi 🔥",
        "title": "복잡한 세상과 단절된 숲속 오두막 화로 앞 🔥 | 극도의 아늑함, 불안감 해소",
        "description": "In the deep snowy forest, gently melt your frozen heart relying on the sound of a crackling campfire and warm acoustic guitar melodies.\\n-\\n눈 내리는 깊은 숲속, 모닥불 타는 소리와 따뜻한 어쿠스틱 기타 선율에 의지해 얼어붙은 마음을 사르르 녹여보세요.",
        "pinned_comment": "세상과 잠시 단절된 느낌이 들 때가 있죠. 가장 돌아가고 싶은 따뜻한 기억 한 조각을 이곳에 꺼내놓아 보세요. 🔥"
    },
    {
        "day": 5,
        "name": "Vintage Train Ride",
        "music_prompt": "A dreamy, spacey lo-fi synthwave track with a gentle train track clacking sound, soft pads, and a nostalgic wandering melody.",
        "image_prompt": "Inside a vintage train passenger carriage at night, looking out of the window at city lights reflecting in the rain, a small glowing neon sign saying 'Greyit' in the cabin, nostalgic lofi anime style, 16:9 aspect ratio.",
        "sub_text": "Night Train Journey 🌌",
        "title": "창밖으로 스쳐 가는 야경과 후회들을 털어내는 밤기차 🌌 | 노스탤지어 감성 Lofi",
        "description": "Leaning against the window of a night train with no destination, this dreamy music is perfect for brushing off your lingering regrets along with the dark night view.\\n-\\n목적지 없는 밤기차 창가에 기대어, 어두운 야경과 함께 마음속의 미련들을 훌훌 털어내기 좋은 몽환적인 감성의 음악입니다.",
        "pinned_comment": "우리는 어디로 달려가고 있는 걸까요? 이 기차가 당신을 가장 가고 싶은 곳으로 데려다준다면, 어디로 가고 싶나요? 🌌"
    },
    {
        "day": 6,
        "name": "Peaceful Morning Calm",
        "music_prompt": "A peaceful and tranquil lo-fi track with soft acoustic guitar, gentle piano melodies, and the faint sound of morning birds in a quiet traditional temple.",
        "image_prompt": "A quiet and peaceful traditional Korean temple in the early morning, soft mist rolling over the mountains, warm sunrise lighting, a cute fluffy cat sitting on the stone stairs, aesthetic lofi artwork, 16:9 aspect ratio.",
        "sub_text": "Morning Calm Lofi 🕊️",
        "title": "마음이 무너질 때 위로가 되어주는 아침 산사의 고요함 🕊️ | 번아웃, 명상 Lofi",
        "description": "Leave the complex world for a moment and lay down your burdens in the tranquility of a morning mountain temple. This beat contains peace and a moment of silence for the fallen heroes.\\n-\\n복잡한 세상을 잠시 떠나 아침 산사의 고요함 속에 마음의 짐을 내려놓으세요. 호국보훈의 달, 순국선열을 향한 묵념과 평화를 담은 비트입니다.",
        "pinned_comment": "가끔은 다 내려놓고 쉬어가도 괜찮습니다. 지금 당신의 마음을 가장 무겁게 짓누르는 걱정은 무엇인가요? 🕊️ (당신의 지친 마음이 언제든 쉬어갈 수 있도록, 구독과 좋아요, 알림 설정으로 함께해 주세요.)"
    },
    {
        "day": 7,
        "name": "Silent Memorial Park",
        "music_prompt": "A solemn and melancholic lo-fi track with slow emotional string swells, warm vinyl crackles, and a respectful quiet atmosphere.",
        "image_prompt": "A peaceful memorial park with lush green trees, sunlight filtering through the leaves, a quiet wooden bench, a glowing neon sign saying 'Greyit' softly hidden in the grass, aesthetic lofi style, 16:9 aspect ratio.",
        "sub_text": "Silent Memorial Lofi 🌿",
        "title": "누군가를 그리워하며 걷는 평화로운 공원 🌿 | 숭고한 휴식, 눈물샘 자극",
        "description": "A warm and melancholic lofi piano melody that soothes the empty heart longing for someone out of reach.\\n-\\n닿을 수 없는 사람을 그리워하는 헛헛한 마음을 달래주는 따뜻하고 먹먹한 감성의 Lofi 피아노 선율입니다.",
        "pinned_comment": "문득 누군가가 사무치게 그리워지는 날이 있습니다. 오늘, 가장 먼저 떠오른 사람은 누구인가요? 🌿 (이 따뜻한 위로가 계속될 수 있도록, 구독과 좋아요, 알림 설정으로 Greyit TV와 함께해 주세요.)"
    },
    {
        "day": 8,
        "name": "Historical Heritage",
        "music_prompt": "A unique lo-fi hip hop fusion track featuring traditional Asian instruments like gayageum, subtle lo-fi drum beats, and a peaceful historical vibe.",
        "image_prompt": "An aesthetic view of a traditional Korean Hanok courtyard on a peaceful sunny afternoon, old stone walls, a sleeping cat on the wooden floor, beautiful historical architecture, lofi anime style, 16:9 aspect ratio.",
        "sub_text": "Historical Lofi Vibe 🏯",
        "title": "고궁 돌담길을 거닐며 느끼는 여유로움 🏯 | 한국적 Lofi 퓨전, 마음 정화",
        "description": "The peace of sitting on the wooden floor of an old Hanok bathed in the afternoon sun. An aesthetic oriental lofi mixing gayageum melodies with dreamy beats.\\n-\\n옛 한옥 마루에 앉아 오후의 햇살을 받는 듯한 평화로움. 가야금 선율과 몽환적인 비트가 섞인 감각적인 동양풍 Lofi입니다.",
        "pinned_comment": "숨가쁘게 돌아가는 현대 사회 속에서, 당신이 가장 평화로움을 느끼는 나만의 안식처는 어디인가요? 🏯 (Greyit TV가 당신만의 안식처가 될 수 있도록, 구독과 좋아요, 알림 설정으로 함께해 주세요.)"
    },
    {
        "day": 9,
        "name": "Eternal Starry Night",
        "music_prompt": "A dreamy, atmospheric lo-fi track with spacious ambient synths, slow rhythmic beats, and emotional piano melodies reflecting on eternal memories.",
        "image_prompt": "A quiet grassy hill at night under a breathtaking starry sky, a gentle breeze, a small glowing neon sign saying 'Greyit' in the foreground, nostalgic and eternal mood, 16:9 aspect ratio.",
        "sub_text": "Eternal Night Lofi ✨",
        "title": "당신의 모든 슬픔을 안아줄 끝없는 밤하늘 ✨ | 우울증 완화, 숙면 테라피",
        "description": "Under the pouring starlight, let all the scars and sorrows accumulated today flow into the universe. You are not alone.\\n-\\n쏟아지는 별빛 아래, 오늘 하루 쌓였던 모든 상처와 슬픔을 우주로 흘려보내세요. 당신은 혼자가 아닙니다.",
        "pinned_comment": "끝없이 펼쳐진 별빛 아래에 서 있다면, 지금 스스로에게 어떤 위로의 말을 건네고 싶으신가요? ✨ (더 많은 위로와 평안을 전해드릴 수 있도록, 구독과 좋아요, 알림 설정으로 Greyit TV와 함께해 주세요.)"
    }
]'''

with open("generate_daily_playlists.py", "r", encoding="utf-8") as f:
    content = f.read()

start_idx = content.find("THEMES = [")
end_idx = content.find("]\n\ndef get_ffmpeg_encoder", start_idx)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_themes + content[end_idx+1:]
    with open("generate_daily_playlists.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated THEMES")
else:
    print("Could not find THEMES block")
