import subprocess
import os

ffmpeg_bin = "C:/Users/greyi/AppData/Local/Python/pythoncore-3.14-64/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
if not os.path.exists(ffmpeg_bin):
    ffmpeg_bin = "ffmpeg"

audio_file = "c:/Users/greyi/biz/greyittv/음악채널/dummy_audio.mp3"

if not os.path.exists(audio_file):
    print("더미 오디오 생성 중...")
    subprocess.run([
        ffmpeg_bin, "-y", "-f", "lavfi", "-i", "sine=frequency=1000:duration=5", audio_file
    ], check=True)

filter_complex = (
    "color=c=black:s=1280x720:d=5[bg]; "
    "[0:a]showfreqs=s=64x100:mode=bar:ascale=log:fscale=log:colors=white@0.8[freqs]; "
    "[freqs]scale=800x100:flags=neighbor[scaled]; "
    "[scaled]split[top][bottom_raw]; "
    "[bottom_raw]vflip[bottom]; "
    "[top][bottom]vstack[sym_raw]; "
    "[sym_raw]drawgrid=w=12:h=200:t=4:c=black,colorkey=black:0.1:0.0[wave]; "
    "[bg][wave]overlay=(W-w)/2:(H-h)/2[outv]"
)

cmd = [
    ffmpeg_bin, "-y",
    "-i", audio_file,
    "-filter_complex", filter_complex,
    "-map", "[outv]",
    "-map", "0:a",
    "-c:v", "libx264",
    "-t", "5",
    "test_wave_sym.mp4"
]

print("FFmpeg 실행 중...")
subprocess.run(cmd, check=True)
print("완료! test_wave_sym.mp4 확인")
