from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from pathlib import Path

OUTPUT_DIR = Path('./mirna_data')
OUTPUT_DIR.mkdir(exist_ok=True)

def fetch_with_selenium(tissue_path, tissue_name, top_n=10):
    """Selenium으로 miRNA 데이터 추출 (정렬 포함)"""
    url = f"https://web.ccb.uni-saarland.de/mirnatissueatlas_2025/tissues/hsa/Atlas_2025_tissue/rpmm/mirna/{tissue_path}/"
    
    print(f"Opening {tissue_name}: {url}")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        driver.get(url)

        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'example'))
            )
            print(f"✅ Page loaded and table found for {tissue_name}")
        except:
            print(f"⚠️ Table not found within 10 seconds for {tissue_name}")
            return None
    
        try:
            header = table.find_element(By.XPATH, "//th[contains(text(), 'avg_expression')]")
            header.click()
            time.sleep(1)
            header.click()
            time.sleep(2)  # 정렬될 때까지 대기
            print(f"📊 Sorted by avg_expression for {tissue_name}")
        except:
            print(f"⚠️ Could not click header for {tissue_name}, using default order")
    
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        
        data = []
        for i, row in enumerate(rows[:top_n]):
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 3:
                try:
                    data.append({
                        'acc': cells[0].text,
                        'avg_expression': float(cells[1].text.replace(',', '')),
                        'stddev_expression': float(cells[2].text.replace(',', ''))
                    })
                except ValueError:
                    continue
        
        df = pd.DataFrame(data)
        print(f"✅ Extracted {len(df)} miRNAs for {tissue_name}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error for {tissue_name}: {e}")
        return None
    
    finally:
        driver.quit()

def main():
    print("=" * 60)
    print("🧬 miRNATissueAtlas 2025 - Selenium 방식")
    print("=" * 60)
    
    tissues = {
        'muscle': 'limb_muscle/limb_muscle',
        'b_cell': 'lymphocyte_B/immune_system',
        'dc_cell': 'dendritic_cells/immune_system'
    }
    
    all_data = {}
    
    for tissue_name, tissue_path in tissues.items():
        print(f"\n{'='*60}")
        print(f"📊 Processing: {tissue_name.upper()}")
        print(f"{'='*60}")
        
        df = fetch_with_selenium(tissue_path, tissue_name, top_n=10)
        
        if df is not None:
            all_data[tissue_name] = df
            
    # B cell
    df = pd.read_csv('mirna_data/b_cell_top10_mirnas.csv')
    df['CV(%)'] = (df['stddev_expression'] / df['avg_expression'] * 100).round(2)
    df.to_csv('mirna_data/b_cell_top10_mirnas.csv', index=False)
    print("✓ B cell CV 추가됨!")
    
    # DC cell
    df = pd.read_csv('mirna_data/dc_cell_top10_mirnas.csv')
    df['CV(%)'] = (df['stddev_expression'] / df['avg_expression'] * 100).round(2)
    df.to_csv('mirna_data/dc_cell_top10_mirnas.csv', index=False)
    print("✓ DC cell CV 추가됨!")
    
    # Muscle
    df = pd.read_csv('mirna_data/muscle_top10_mirnas.csv')
    df['CV(%)'] = (df['stddev_expression'] / df['avg_expression'] * 100).round(2)
    df.to_csv('mirna_data/muscle_top10_mirnas.csv', index=False)
    print("✓ Muscle CV 추가됨!")
            
    # 상위 5개 출력
    print(f"\n📋 Top 5 miRNAs for {tissue_name}:")
    print(df[['acc', 'avg_expression']].head().to_string(index=False))
    
    print(f"\n{'='*60}")
    print("✨ 모든 데이터 추출 완료!")
    print(f"📁 저장 위치: {OUTPUT_DIR.absolute()}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
