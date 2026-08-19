import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

st.set_page_config(page_title="miRNA 검색 도구", layout="wide")
st.title("🧬 Immune System miRNA 검색 도구")
st.markdown("miRNATissueAtlas 2025에서 면역계 세포의 top 10 miRNA를 검색합니다")

# 정확한 세포 이름 리스트
IMMUNE_CELLS = [
    'H9',
    'Basophils',
    'Cd19',
    'Cd34',
    'Cd4',
    'Dendritic_cells',
    'Lymphocyte',
    'Lymphocyte_B',
    'Lymphocyte_T',
    'Macrophage',
    'Mononuclear_cells',
    'Natural_killer'
]

CELL_MAPPING = {
    'H9': 'h9/immune_system',
    'Basophils': 'basophils/immune_system',
    'Cd19': 'cd19/immune_system',
    'Cd34': 'cd34/immune_system',
    'Cd4': 'cd4/immune_system',
    'Dendritic_cells': 'dendritic_cells/immune_system',
    'Lymphocyte': 'lymphocyte/immune_system',
    'Lymphocyte_B': 'lymphocyte_B/immune_system',
    'Lymphocyte_T': 'lymphocyte_T/immune_system',
    'Macrophage': 'macrophage/immune_system',
    'Mononuclear_cells': 'mononuclear_cells/immune_system',
    'Natural_killer': 'natural_killer/immune_system'
}

def fetch_mirna_data(cell_name, top_n=10):
    """특정 세포의 miRNA 데이터 추출"""
    actual_name = CELL_MAPPING[cell_name]
    url = f"https://web.ccb.uni-saarland.de/mirnatissueatlas_2025/tissues/hsa/Atlas_2025_tissue/rpmm/mirna/{actual_name}/"
    
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
          
        # 페이지 완전 로드 대기
        WebDriverWait(driver, 20).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(3)  # 추가 대기

        # 테이블 찾기
        try:
            table = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'example'))
            )
        except:
            return None, f"테이블을 찾을 수 없습니다: {cell_name}"
        
        # 헤더 클릭해서 정렬
        try:
            header = table.find_element(By.XPATH, "//th[contains(text(), 'avg_expression')]")
            header.click()
            time.sleep(1)
            header.click()
            time.sleep(2)
        except:
            pass
        
        # 데이터 추출
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        
        data = []
        for row in rows[:top_n]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 3:
                try:
                    avg_expr = float(cells[1].text.replace(',', ''))
                    std_expr = float(cells[2].text.replace(',', ''))
                    cv = (std_expr / avg_expr * 100) if avg_expr > 0 else 0
                    
                    data.append({
                        'miRNA': cells[0].text,
                        '발현량': avg_expr,
                        '표준편차': std_expr,
                        'CV(%)': round(cv, 2)
                    })
                except:
                    pass
        
        driver.quit()
        
        if not data:
            return None, f"데이터를 찾을 수 없습니다: {cell_name}"
        
        return pd.DataFrame(data), "성공"
    
    except Exception as e:
        return None, f"오류 ({cell_name}): {str(e)}"

# UI
st.markdown("### 세포 선택")

col1, col2 = st.columns([2, 1])

with col1:
    cell_name = st.selectbox(
        "세포 선택:",
        IMMUNE_CELLS,
        help="Immune system의 세포를 선택하세요"
    )

with col2:
    top_n = st.number_input("상위 개수", min_value=5, max_value=50, value=10)

# 검색 버튼
if st.button("🔍 검색", use_container_width=True):
    with st.spinner(f"'{cell_name}' 데이터를 가져오는 중..."):
        df, msg = fetch_mirna_data(cell_name, top_n)
    
    if df is not None and len(df) > 0:
        st.success(f"✅ {cell_name} - {len(df)}개 miRNA 발견!")
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("최고 발현량", f"{df['발현량'].max():.2f}")
        with col2:
            st.metric("평균 발현량", f"{df['발현량'].mean():.2f}")
        with col3:
            st.metric("최저 발현량", f"{df['발현량'].min():.2f}")
        
        # 다운로드
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"{cell_name}_top{len(df)}_mirnas.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.error(f"❌ {msg}")

st.markdown("---")
st.markdown(f"""
### 🧬 이용 가능한 세포 ({len(IMMUNE_CELLS)}개):
{', '.join(IMMUNE_CELLS)}

### 📊 데이터 출처:
[miRNATissueAtlas 2025](https://web.ccb.uni-saarland.de/mirnatissueatlas_2025/)
""")
