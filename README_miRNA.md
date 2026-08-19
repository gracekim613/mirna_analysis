# miRNATissueAtlas 2025 - 데이터 수집 및 분석 가이드

## 📋 개요

miRNATissueAtlas 2025에서 세포타입별 top miRNA를 자동으로 다운로드하고,  
나중에 TargetScan과 연동하기 위한 준비 코드입니다.

- **대상 세포타입**: Muscle (limb_muscle), B cell (lymphocyte_B), DC cell (Dendritic_cells)
- **데이터**: 각 세포타입의 상위 10개 miRNA (발현량 기준)
- **저장 형식**: CSV, JSON

---

## 🚀 사용 방법

### 1단계: 데이터 다운로드

```bash
python mirna_atlas_downloader.py
```

**실행 결과:**
- `mirna_data/` 디렉토리 생성
- 각 세포타입별 CSV 파일: `muscle_top10_mirnas.csv`, `b_cell_top10_mirnas.csv`, `dc_cell_top10_mirnas.csv`
- 통합 JSON 파일: `master_mirna_atlas.json`

**샘플 출력:**
```
✅ Successfully fetched 10 miRNAs
💾 Saved to CSV: ./mirna_data/muscle_top10_mirnas.csv
💾 Saved to JSON: ./mirna_data/muscle_top10_mirnas.json

📊 Top 5 miRNAs for muscle:
          acc  avg_expression
0  hsa-miR-1     1234.56
1  hsa-miR-133a   1100.23
2  hsa-miR-206     987.45
...
```

---

### 2단계: 데이터 로드 및 분석

#### 옵션 A: 특정 세포타입만 로드
```python
from mirna_atlas_loader import load_mirna_by_cell_type

muscle_mirnas = load_mirna_by_cell_type('muscle')
print(muscle_mirnas[['acc', 'avg_expression']])
# Output:
#            acc  avg_expression
# 0    hsa-miR-1          1234.56
# 1  hsa-miR-133a          1100.23
# ...
```

#### 옵션 B: 모든 세포타입 한 번에 로드
```python
from mirna_atlas_loader import load_master_mirna_list

master = load_master_mirna_list()
# {
#   'muscle': {
#     'mirna_names': ['hsa-miR-1', 'hsa-miR-133a', ...],
#     'expressions': [1234.56, 1100.23, ...],
#     'std_devs': [...]
#   },
#   'b_cell': {...},
#   'dc_cell': {...}
# }
```

#### 옵션 C: 세포타입별 특이적 miRNA 찾기
```python
from mirna_atlas_loader import get_cell_type_specific_mirnas

muscle_specific = get_cell_type_specific_mirnas('muscle')
print(muscle_specific)
# {
#   'specific': ['hsa-miR-1', 'hsa-miR-206', ...],
#   'shared': ['hsa-miR-100', ...],
#   'total': 10
# }
```

---

### 3단계: TargetScan 연동 준비

#### 전체 미RNA 리스트 추출
```python
from mirna_atlas_loader import export_for_targetscan

# TXT 형식 (한 줄에 하나의 miRNA)
export_for_targetscan(output_format='txt')
# → targetscan/mirna_list_for_targetscan.txt

# CSV 형식 (세포타입 정보 포함)
export_for_targetscan(output_format='csv')
# → targetscan/mirna_list_with_cell_types.csv
```

**TXT 파일 예시:**
```
hsa-miR-1
hsa-miR-133a
hsa-miR-206
hsa-let-7a
hsa-miR-26a
...
```

**CSV 파일 예시:**
```
mirna_name,cell_type,is_specific
hsa-miR-1,muscle,True
hsa-miR-1,b_cell,False
hsa-miR-1,dc_cell,False
hsa-miR-133a,muscle,True
...
```

---

### 4단계: 데이터 요약 보기

```python
from mirna_atlas_loader import summary

summary()
# ============================================================
# 📊 miRNA 데이터 요약
# ============================================================
# 
# MUSCLE
#   ├─ Total miRNAs: 10
#   ├─ Top 3: hsa-miR-1, hsa-miR-133a, hsa-miR-206
#   ├─ Cell-type specific: 7
#   │  └─ hsa-miR-1, hsa-miR-206, hsa-miR-208
#   └─ Shared with others: 3
# 
# B_CELL
#   ├─ Total miRNAs: 10
#   ├─ Top 3: hsa-miR-21-5p, hsa-miR-146a, hsa-miR-155
#   ├─ Cell-type specific: 5
#   └─ Shared with others: 5
# 
# ...
# ============================================================
# 🎯 Total unique miRNAs across all cell types: 28
# ============================================================
```

---

## 📁 파일 구조

```
.
├── mirna_atlas_downloader.py    # 데이터 다운로드 스크립트
├── mirna_atlas_loader.py         # 데이터 로드 및 분석 유틸리티
├── README_miRNA.md               # 이 파일
└── mirna_data/                   # 데이터 저장 디렉토리
    ├── muscle_top10_mirnas.csv
    ├── muscle_top10_mirnas.json
    ├── b_cell_top10_mirnas.csv
    ├── b_cell_top10_mirnas.json
    ├── dc_cell_top10_mirnas.csv
    ├── dc_cell_top10_mirnas.json
    ├── master_mirna_atlas.json
    └── targetscan/
        ├── mirna_list_for_targetscan.txt
        └── mirna_list_with_cell_types.csv
```

---

## 🔄 TargetScan 연동 (다음 단계)

1. **TargetScan 다운로드**: http://www.targetscan.org/
2. **miRNA 리스트 입력**: `targetscan/mirna_list_for_targetscan.txt` 사용
3. **3'UTR 서열 입력**: GEMORNA에서 생성한 3'UTR 서열
4. **Target site 결과 분석**: 8mer/7mer-m8/7mer-A1 개수 카운팅

### 예상되는 workflow:
```python
# 1단계: 저장된 miRNA 로드
from mirna_atlas_loader import get_mirna_names

all_mirnas = get_mirna_names(cell_type=None)  # 전체
muscle_mirnas = get_mirna_names(cell_type='muscle')

# 2단계: 각 세포타입별로 분석 (나중에)
def analyze_3utr_with_targetscan(utr_sequence, cell_type='muscle'):
    mirnas = get_mirna_names(cell_type)
    # TargetScan API 또는 로컬 tool 사용
    # target_sites = run_targetscan(utr_sequence, mirnas)
    return target_sites
```

---

## 💡 주요 함수 정리

| 함수 | 기능 |
|------|------|
| `load_mirna_by_cell_type()` | 특정 세포타입의 miRNA 로드 |
| `load_master_mirna_list()` | 모든 세포타입의 miRNA 로드 |
| `get_mirna_names()` | miRNA 이름 리스트만 추출 |
| `get_cell_type_specific_mirnas()` | 세포타입별 특이적 miRNA 찾기 |
| `export_for_targetscan()` | TargetScan용 리스트 내보내기 |
| `summary()` | 전체 데이터 요약 출력 |

---

## ⚠️ 주의사항

1. **첫 실행**: `mirna_atlas_downloader.py`를 먼저 실행해야 합니다
2. **인터넷 연결**: miRNATissueAtlas 서버에서 데이터를 가져오므로 필요합니다
3. **데이터 갱신**: 마지막 다운로드 시간은 JSON 파일의 `timestamp` 필드에 기록됩니다

---

## 📞 문제 해결

**Q: "Data file not found" 에러가 나와요**  
A: `mirna_atlas_downloader.py`를 먼저 실행하세요

**Q: 서버에서 데이터를 못 가져와요**  
A: 인터넷 연결을 확인하고, 다시 시도하세요

**Q: TargetScan을 어떻게 설치하나요?**  
A: http://www.targetscan.org/ 참고 (다음 단계에서 자세히 설명 예정)

---

## 📝 업데이트 기록

- 2026-08-05: 초기 버전 작성 (limb_muscle, lymphocyte_B, Dendritic_cells)
