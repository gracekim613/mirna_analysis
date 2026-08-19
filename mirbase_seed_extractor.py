# mirbase_seed_extractor.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_sequence_from_mirbase(mirna_name):
    """
    miRBase에서 miRNA sequence 자동 추출
    예: hsa-miR-21-5p → UAGCUUAUCAGACUGAUGUUGACU
    """

def get_sequence_from_mirbase(mirna_name):
    options = Options()
    options.add_argument('--headless')  # GUI 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # miRBase 홈페이지
        url = "https://www.mirbase.org/"
        driver.get(url)
        time.sleep(2)
        
        # Search 창 찾기
        search_box = driver.find_element(By.NAME, "terms")
        search_box.clear()
        search_box.send_keys(mirna_name)
        
        # 검색 버튼 클릭
        search_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        search_btn.click()
        
        time.sleep(3)
        
        # Sequence 추출 (첫 번째 결과의 mature sequence)
        try:
            seq_element = driver.find_element(By.XPATH, "//td[contains(text(), 'UAGC') or contains(text(), 'GCUG')]")
            sequence = seq_element.text.strip()
            
            # "8 - UAGCUU... - 31" 형식에서 sequence만 추출
            if ' - ' in sequence:
                parts = sequence.split(' - ')
                if len(parts) >= 2:
                    return parts[1]
            return sequence
        except:
            print(f"Warning: {mirna_name}의 sequence를 찾을 수 없습니다")
            return None
    
    finally:
        driver.quit()

def extract_seeds(full_sequence):
    """
    miRNA sequence에서 3가지 seed 추출
    """
    if not full_sequence or len(full_sequence) < 8:
        return None
    
    return {
        "8mer": full_sequence[1:8],      # 위치 2-8
        "7m8": full_sequence[1:8],       # 위치 2-8
        "7a1": full_sequence[0:7]        # 위치 1-7 (A at pos1)
    }

# 메인
if __name__ == "__main__":
    b_cell_mirnas = [
        'hsa-miR-21-5p',
        'hsa-miR-17-5p',
        'hsa-miR-451a',
        'hsa-miR-29c-3p',
        'hsa-miR-24-3p',
        'hsa-miR-145-5p',
        'hsa-miR-93-5p',
        'hsa-miR-26a-5p',
        'hsa-miR-191-5p',
        'hsa-miR-19b-3p'
    ]
    
    mirna_database = {
        "B_lymphocyte": {}
    }
    
    print("miRBase에서 sequence 추출 중...")
    for mirna in b_cell_mirnas:
        print(f"추출 중: {mirna}")
        seq = get_sequence_from_mirbase(mirna)
        
        if seq:
            seeds = extract_seeds(seq)
            mirna_database["B_lymphocyte"][mirna] = seeds
            print(f"  ✓ {mirna}: {seeds}")
        else:
            print(f"  ✗ {mirna}: 실패")
        
        time.sleep(1)  # 서버 부하 방지
    
    # 결과 저장
    import json
    with open('mirna_database.json', 'w') as f:
        json.dump(mirna_database, f, indent=2)
    
    print("\n✓ 완료! mirna_database.json에 저장됨")
