import os
from make_shorts import make_shorts

def run_test():
    image_path = os.path.join("daily_playlists", "week1_cozy_rain_cafe", "background.png")
    audio_path = os.path.join("daily_playlists", "week1_cozy_rain_cafe", "track_1.mp3")
    output_path = "test_shorts.mp4"
    
    print(f"이미지 확인: {os.path.exists(image_path)}")
    print(f"오디오 확인: {os.path.exists(audio_path)}")
    
    if os.path.exists(image_path) and os.path.exists(audio_path):
        make_shorts(
            image_path=image_path,
            audio_path=audio_path,
            output_path=output_path,
            title="테스트",
            description="테스트입니다.",
            tags="#test",
            is_debug=False
        )
        print("✅ 테스트 쇼츠 영상 생성 완료: test_shorts.mp4")

if __name__ == "__main__":
    run_test()
