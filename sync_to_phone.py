import os
import sys
import shutil
import glob

sys.stdout.reconfigure(encoding='utf-8')

def sync_shorts_to_onedrive():
    print("🚀 [스마트폰 자동 전송] OneDrive 동기화를 시작합니다.")
    
    # 1. 원드라이브 경로 설정
    # 윈도우 환경에 맞춰 사용자 홈 디렉터리 내의 OneDrive 폴더를 찾습니다.
    home_dir = os.path.expanduser("~")
    onedrive_dir = os.path.join(home_dir, "OneDrive")
    
    if not os.path.exists(onedrive_dir):
        print("❌ OneDrive 폴더를 찾을 수 없습니다. 원드라이브가 설치되어 있는지 확인해주세요.")
        return
        
    # GreyitTV 전용 폴더 생성
    target_dir = os.path.join(onedrive_dir, "GreyitTV_Shorts")
    os.makedirs(target_dir, exist_ok=True)
    print(f"📂 대상 폴더 확인 완료: {target_dir}")
    
    # 2. 쇼츠 영상 및 텍스트 파일 검색 및 복사
    base_dir = "daily_playlists"
    
    # Day 폴더 내의 shorts 영상과 sns 텍스트 파일을 모두 찾습니다.
    files_to_sync = []
    files_to_sync.extend(glob.glob(os.path.join(base_dir, "Day*", "shorts_day*.mp4")))
    files_to_sync.extend(glob.glob(os.path.join(base_dir, "Day*", "sns_description_day*.txt")))
    
    if not files_to_sync:
        print("❌ 전송할 쇼츠 영상이나 텍스트 파일을 찾을 수 없습니다.")
        return
        
    copied_count = 0
    for file_path in files_to_sync:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(target_dir, filename)
        
        print(f"🔄 복사 중: {filename} -> 스마트폰(OneDrive)")
        try:
            shutil.copy2(file_path, dest_path)
            copied_count += 1
            print(f"✅ {filename} 전송 완료!")
        except Exception as e:
            print(f"❌ {filename} 복사 실패: {e}")
            
    print(f"\n🎉 총 {copied_count}개의 파일(영상 및 텍스트)이 성공적으로 스마트폰(OneDrive)으로 전송(동기화)되었습니다!")
    print("👉 스마트폰의 OneDrive 앱을 열어 [GreyitTV_Shorts] 폴더를 확인해 보세요.")

if __name__ == "__main__":
    sync_shorts_to_onedrive()
