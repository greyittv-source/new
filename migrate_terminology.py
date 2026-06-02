import os
import json
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

def migrate():
    base_dir_old = "weekly_playlists"
    base_dir_new = "daily_playlists"
    
    # 1. 최상위 폴더 이름 변경
    if os.path.exists(base_dir_old):
        os.rename(base_dir_old, base_dir_new)
        print(f"✅ 폴더명 변경: {base_dir_old} -> {base_dir_new}")
    
    if not os.path.exists(base_dir_new):
        print("대상 폴더가 없습니다.")
        return
        
    # 2. 내부 폴더 및 파일 이름 변경
    for i in range(1, 10):
        # weekX 폴더 찾기
        old_dirs = glob.glob(os.path.join(base_dir_new, f"week{i}_*"))
        for old_dir in old_dirs:
            dir_name = os.path.basename(old_dir)
            new_dir_name = dir_name.replace(f"week{i}", f"day{i}")
            new_dir = os.path.join(base_dir_new, new_dir_name)
            os.rename(old_dir, new_dir)
            print(f"✅ 하위 폴더명 변경: {dir_name} -> {new_dir_name}")
            
            # 내부 영상 파일들 이름 변경
            old_long = os.path.join(new_dir, f"weekly_playlist_week{i}.mp4")
            new_long = os.path.join(new_dir, f"daily_playlist_day{i}.mp4")
            if os.path.exists(old_long):
                os.rename(old_long, new_long)
                
            old_short = os.path.join(new_dir, f"shorts_week{i}.mp4")
            new_short = os.path.join(new_dir, f"shorts_day{i}.mp4")
            if os.path.exists(old_short):
                os.rename(old_short, new_short)
                
    # 3. 메타데이터 JSON 변경
    old_meta = os.path.join(base_dir_new, "weekly_playlists_metadata.json")
    new_meta = os.path.join(base_dir_new, "daily_playlists_metadata.json")
    
    if os.path.exists(old_meta):
        os.rename(old_meta, new_meta)
        
    if os.path.exists(new_meta):
        with open(new_meta, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for item in data:
            if "week" in item:
                item["day"] = item.pop("week")
            if "video_file" in item:
                item["video_file"] = item["video_file"].replace("weekly_", "daily_").replace("week", "day")
                
        with open(new_meta, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ 메타데이터 JSON 마이그레이션 완료")

if __name__ == "__main__":
    migrate()
