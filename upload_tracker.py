"""
📋 Upload Tracker — Agent Luna의 전 플랫폼 업로드 기록 추적 시스템
===================================================================
모든 업로드(YouTube, TikTok, Naver Clip 등)의 성공/실패 이력을 
upload_history.json에 자동으로 기록합니다.

사용법:
    from upload_tracker import log_upload, get_history, is_duplicate

    # 업로드 성공 시 기록
    log_upload(
        platform="youtube",
        content_type="longform",      # "longform" | "shorts"
        title="비 오는 날 카페 Lofi",
        file_path="daily_playlists/Day1_.../daily_playlist_day1.mp4",
        status="success",             # "success" | "failed"
        video_id="mD667lqVC8w",       # 플랫폼에서 반환한 ID (선택)
        url="https://...",            # 결과 URL (선택)
        error_message=None            # 실패 시 에러 메시지
    )

    # 중복 업로드 방지 확인
    if is_duplicate("youtube", "비 오는 날 카페 Lofi", "longform"):
        print("이미 업로드됨!")
"""

import os
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "upload_history.json")


def _load_history():
    """JSON 파일에서 업로드 기록을 불러옵니다."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_history(records):
    """업로드 기록을 JSON 파일에 저장합니다."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def log_upload(
    platform,
    content_type,
    title,
    file_path,
    status,
    video_id=None,
    url=None,
    error_message=None,
    extra=None
):
    """
    업로드 결과를 기록합니다.

    Args:
        platform: "youtube" | "tiktok" | "naver_clip" | "instagram"
        content_type: "longform" | "shorts" | "clip" | "reel"
        title: 콘텐츠 제목
        file_path: 업로드한 로컬 파일 경로
        status: "success" | "failed"
        video_id: 플랫폼이 반환한 비디오 ID (성공 시)
        url: 플랫폼 내 콘텐츠 URL (성공 시)
        error_message: 에러 메시지 (실패 시)
        extra: 추가 메타데이터 딕셔너리 (선택)
    """
    records = _load_history()

    record = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "content_type": content_type,
        "title": title,
        "file_path": file_path,
        "status": status,
    }

    if video_id:
        record["video_id"] = video_id
    if url:
        record["url"] = url
    if error_message:
        record["error_message"] = error_message
    if extra:
        record["extra"] = extra

    records.append(record)
    _save_history(records)

    emoji = "✅" if status == "success" else "❌"
    print(f"📋 [업로드 추적기] {emoji} [{platform.upper()}] {content_type} — \"{title}\" → {status}")


def is_duplicate(platform, title, content_type=None):
    """
    동일한 플랫폼 + 제목 + 콘텐츠 타입 조합으로 성공한 업로드가 이미 있는지 확인합니다.

    Returns:
        True: 이미 성공적으로 업로드된 기록이 있음 (중복)
        False: 해당 기록 없음 (업로드 가능)
    """
    records = _load_history()
    for r in records:
        if (r["platform"] == platform
                and r["title"].strip() == title.strip()
                and r["status"] == "success"):
            if content_type and r.get("content_type") != content_type:
                continue
            return True
    return False


def get_history(platform=None, status=None, limit=20):
    """
    업로드 기록을 필터링하여 반환합니다.

    Args:
        platform: 특정 플랫폼만 필터 (선택)
        status: "success" 또는 "failed"만 필터 (선택)
        limit: 최대 반환 건수 (기본 20건, 최신 순)

    Returns:
        list of dict
    """
    records = _load_history()

    if platform:
        records = [r for r in records if r["platform"] == platform]
    if status:
        records = [r for r in records if r["status"] == status]

    # 최신 순 정렬
    records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return records[:limit]


def get_failed_uploads():
    """실패한 업로드만 반환합니다 (재시도 대상)."""
    return get_history(status="failed", limit=100)


def print_summary():
    """전체 업로드 기록 요약을 출력합니다."""
    records = _load_history()
    if not records:
        print("📋 [업로드 추적기] 아직 기록된 업로드가 없습니다.")
        return

    platforms = {}
    for r in records:
        key = r["platform"]
        if key not in platforms:
            platforms[key] = {"success": 0, "failed": 0}
        if r["status"] == "success":
            platforms[key]["success"] += 1
        else:
            platforms[key]["failed"] += 1

    print("\n" + "=" * 50)
    print("📋 [업로드 추적기] 전체 업로드 현황 요약")
    print("=" * 50)
    total_s, total_f = 0, 0
    for p, counts in platforms.items():
        s, f = counts["success"], counts["failed"]
        total_s += s
        total_f += f
        emoji = "🟢" if f == 0 else "🟡"
        print(f"  {emoji} {p.upper():15s} | 성공: {s}건 | 실패: {f}건")
    print("-" * 50)
    print(f"  📊 합계: 성공 {total_s}건, 실패 {total_f}건 (총 {total_s + total_f}건)")
    print("=" * 50)


if __name__ == "__main__":
    print_summary()
