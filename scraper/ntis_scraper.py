import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from datetime import datetime
import os

# 설정 값
BASE_URL = "https://www.ntis.go.kr/rndgate/eg/un/ra/mng.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.ntis.go.kr/rndgate/eg/un/ra/mng.do",
}

def get_detail_info(session, url):
    """상세 페이지에서 추가 정보(기관명, 시간, 문의처 등)를 추출"""
    try:
        resp = session.get(url, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "lxml")
        
        info = {
            "form": "-", "agency": "-", "deadline_time": "-", 
            "contact": "-", "type": "-", "amount": "-", "biz_name": "-"
        }

        summary_divs = soup.find_all("div", class_=re.compile(r"summary\d+"))
        for div in summary_divs:
            for li in div.find_all("li"):
                span = li.find("span")
                if not span: continue
                
                label = span.get_text(strip=True).replace(":", "").replace(" ", "")
                val = li.get_text(strip=True).replace(span.get_text(strip=True), "").strip()

                if "공고형태" in label: info["form"] = val
                elif "공고기관명" in label: info["agency"] = val
                elif "접수마감시간" in label: info["deadline_time"] = val
                elif "문의처" in label: info["contact"] = val
                elif "공고유형" in label: info["type"] = val
                elif "공고금액" in label: info["amount"] = val
                elif "사업명" in label: info["biz_name"] = val
        return info
    except:
        return None

def scrape_ntis():
    # 1. 스크립트 위치(scraper 폴더)를 기준으로 상위 폴더의 'data' 폴더를 상대 경로로 지정
    script_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 파일의 폴더 위치 (.../scraper)
    parent_dir = os.path.dirname(script_dir)                # 상위 폴더 위치 (.../NTIS 자료 수합)
    folder_path = os.path.join(parent_dir, "data")          # 최종 대상 폴더 (.../NTIS 자료 수합/data)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"'{folder_path}' 폴더를 생성했습니다.")

    session = requests.Session()
    session.headers.update(HEADERS)

    # '접수중(B)' 필터와 '100개씩 보기' 설정
    payload = {
        "pageIndex": "1",
        "recordCountPerPage": "100",
        "pageUnit": "100",
        "searchStatusList": "B",
        "flag": "rndList"
    }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] NTIS 수집 시작 (data 폴더 저장)...")
    
    try:
        response = session.post(BASE_URL, data=payload)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")
        
        table = soup.find("table", class_="basic_list")
        if not table:
            print("데이터 테이블을 찾을 수 없습니다.")
            return

        rows = table.find_all("tr")[1:]
        all_results = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 8: continue

            a_tag = row.find("a", href=re.compile(r"roRndUid"))
            if not a_tag: continue

            title = a_tag.get_text(strip=True)
            link = "https://www.ntis.go.kr" + a_tag['href']
            
            ministry = cols[4].get_text(strip=True)
            raw_deadline = cols[6].get_text(strip=True).replace(".", "-")
            dday_text = cols[7].get_text(strip=True).replace(" ", "")

            print(f" >> 상세 수집 중: {title[:25]}...")
            detail = get_detail_info(session, link)
            
            if detail:
                all_results.append({
                    "title": title,
                    "url": link,
                    "ministry": ministry,
                    "agency": detail["agency"],
                    "form": detail["form"],
                    "type": detail["type"],
                    "deadline": f"{raw_deadline} [{dday_text}]",
                    "deadline_time": detail["deadline_time"],
                    "contact": detail["contact"],
                    "amount": detail["amount"],
                    "business_name": detail["biz_name"]
                })
            time.sleep(random.uniform(0.4, 0.8))

        # 2. data 폴더 내에 announcements.json으로 저장 ("w" 모드라 값이 있으면 덮어씌움)
        file_path = os.path.join(folder_path, "announcements.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
        
        print(f"\n✅ 완료: {file_path}에 총 {len(all_results)}건 저장됨.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    scrape_ntis()