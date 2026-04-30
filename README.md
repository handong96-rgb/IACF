# NTIS 국가R&D 통합공고 대시보드

NTIS에서 **접수중** 공고를 자동 수집하여 인터랙티브 대시보드로 시각화합니다.

## 구조

```
├── scraper/
│   ├── ntis_scraper.py      # 스크래퍼
│   └── requirements.txt
├── data/
│   └── announcements.json   # 수집 데이터 (자동 갱신)
├── index.html               # 대시보드 (GitHub Pages)
└── .github/workflows/
    └── scrape.yml           # 자동화 (하루 4회)
```

## 로컬 실행

```bash
pip install -r scraper/requirements.txt
python scraper/ntis_scraper.py
# 이후 index.html을 브라우저로 열기
```

## GitHub Pages 설정

1. GitHub에 저장소 생성 후 업로드
2. Settings → Pages → Branch: main, Folder: / (root)
3. `index.html`의 `DATA_URL`을 GitHub Raw URL로 변경:
   ```js
   const DATA_URL = 'https://raw.githubusercontent.com/[사용자명]/[저장소명]/main/data/announcements.json';
   ```
4. Actions 탭에서 워크플로우가 활성화되어 있는지 확인

## 자동 갱신

GitHub Actions가 **KST 09:00, 15:00, 21:00, 03:00** 에 자동으로 수집합니다.
