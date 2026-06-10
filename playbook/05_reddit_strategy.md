# 🚀 Playbook 05: 레딧(Reddit) 커뮤니티 진출 전략 가이드

레딧(Reddit)은 전 세계 Lofi 및 Chillhop 리스너들이 모여있는 가장 큰 커뮤니티 중 하나입니다. 하지만 레딧 사용자들은 **'광고성 링크 도배'**를 극도로 싫어하므로, 정교한 **소프트 프로모션(Soft Promotion)** 전략이 필수적입니다.

## 🎯 1. 타겟 서브레딧 (Subreddits)
다음 커뮤니티들을 타겟으로 삼아 매일 순환하며 영상을 업로드합니다.
- `r/LofiHipHop` (가장 큰 규모, Lofi 영상 자체에 관대함)
- `r/StudyMusic` (공부용 플레이리스트 수요가 높음)
- `r/chillhop` (비트/칠아웃 위주)
- `r/aiArt` (AI로 생성한 이미지/영상인 점을 어필할 때 유용)

## 💡 2. 자동화 봇 작동 원리 (`reddit_bot.py`)
매일 메인 엔진(`generate_daily_playlists.py`)이 데일리 쇼츠(1분 이하)를 생성하면, 루나 봇이 즉시 다음 작업을 수행합니다.

1. **Native Video 업로드:** 유튜브 링크를 올리는 대신, 만들어진 **mp4 파일 자체**를 레딧에 직접 업로드합니다. (유저들은 레딧 앱 안에서 영상이 바로 재생되는 것을 선호합니다.)
2. **어그로성 제목:** "Made some rainy lofi to code to (비 오는 날 코딩하려고 로파이 음악을 만들어봤어)" 처럼 1인칭 시점의 자연스러운 제목을 사용합니다.
3. **첫 번째 낚시줄 댓글:** 봇이 영상을 올리자마자 1빠로 댓글을 답니다. `"If anyone wants the full 1-hour version, here it is: [유튜브 링크]"`

## 🔑 3. 대표님 사전 준비 사항 (.env 세팅)
레딧 봇이 작동하려면 대표님의 레딧 계정 API 키가 필요합니다.
1. 레딧 계정 로그인 후 `https://www.reddit.com/prefs/apps` 에 접속
2. `Create App` 클릭 -> `script` 선택
3. 발급된 키들을 `음악채널` 폴더 안의 `.env` 파일에 다음과 같이 저장합니다.
```env
REDDIT_CLIENT_ID=여기에_14자리_클라이언트_아이디
REDDIT_CLIENT_SECRET=여기에_27자리_시크릿_키
REDDIT_USERNAME=대표님_레딧_아이디
REDDIT_PASSWORD=대표님_레딧_비밀번호
```

> [!WARNING]
> `.env` 파일은 절대 깃허브나 외부에 노출되어서는 안 됩니다! (`.gitignore`에 의해 안전하게 보호받고 있습니다.)
