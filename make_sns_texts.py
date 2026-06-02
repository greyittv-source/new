import os
from generate_daily_playlists import THEMES

output_dir = "daily_playlists/week1_cozy_rain_cafe"
os.makedirs(output_dir, exist_ok=True)

for theme in THEMES:
    day = theme["day"]
    sns_text_path = os.path.join(output_dir, f"sns_description_day{day}.txt")
    sns_content = f"{theme['description']}\n\n💡 Follow and save for daily healing vibes ✨\n(더 많은 힐링 음악을 원하신다면 팔로우와 저장을 꾹 눌러주세요 🎧)\n\n⚠️ The music and images in this video were fully generated using AI technology.\n(본 영상의 음악과 이미지는 모두 AI 기술을 활용하여 창작되었습니다.)\n\n#Shorts #Lofi #StudyMusic #ChillVibes #GreyitTV"
    
    with open(sns_text_path, "w", encoding="utf-8") as f:
        f.write(sns_content)

print("✅ 성공적으로 모든 Day의 SNS 복붙용 텍스트 파일을 생성했습니다!")
