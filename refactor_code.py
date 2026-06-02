import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

def refactor_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 문자열 치환
    replacements = [
        ("weekly_playlists", "daily_playlists"),
        ("pregenerate_weekly_playlists", "generate_daily_playlists"),
        ("upload_weekly", "upload_daily_videos"),
        ("weekly_playlist_week", "daily_playlist_day"),
        ("shorts_week", "shorts_day"),
        ("\"week\":", "\"day\":"),
        ("theme['week']", "theme['day']"),
        ("theme[\"week\"]", "theme[\"day\"]"),
        ("week_num", "day_num"),
        ("5주 분량", "5일 분량"),
        ("5주 치", "5일 치"),
        ("주간 플레이리스트", "일간 플레이리스트"),
        ("weekly_", "daily_"),
        ("shorts_week", "shorts_day")
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Refactored: {filepath}")

def main():
    files_to_refactor = [
        "generate_daily_playlists.py",
        "upload_daily_videos.py",
        "fix_daily_shorts.py",
        "replace_daily_shorts.py",
        "make_shorts.py",
        "sync_to_phone.py"
    ]
    
    for f in files_to_refactor:
        refactor_file(f)

if __name__ == "__main__":
    main()
