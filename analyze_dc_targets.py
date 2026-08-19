import pandas as pd
import json
from collections import defaultdict

# TargetScan 데이터 읽기
def read_targetscan_file(filepath):
    """TargetScan txt 파일 읽기"""
    df = pd.read_csv(filepath, sep='\t', low_memory=False)
    return df

# DC top 10 miRNA
DC_CELL_MIRNAS = [
    'hsa-miR-21-5p',
    'hsa-miR-22-3p',
    'hsa-miR-191-5p',
    'hsa-miR-146b-5p',
    'hsa-miR-378a-3p',
    'hsa-miR-142-5p',
    'hsa-let-7a-5p',
    'hsa-let-7f-5p',
    'hsa-miR-26a-5p',
    'hsa-miR-92a-3p'
]

def analyze_binding_patterns(df, mirnas):
    """각 miRNA의 binding pattern 분석"""
    results = {}
    
    # 숫자 → 이름 매핑
    site_type_map = {
        1: '8mer',
        2: '7m8',
        3: '7a1'
    }
    
    for mirna in mirnas:
        print(f"분석 중: {mirna}")
        
        mirna_data = df[df['miRNA'] == mirna]
        
        if len(mirna_data) == 0:
            print(f"  ⚠️ {mirna} 데이터 없음")
            results[mirna] = {...}
            continue
        
        # 숫자 카운트
        site_types = mirna_data['Site Type'].value_counts()
        total = len(mirna_data)
        
        count_1 = int(site_types.get(1, 0))  # ← 변경
        count_2 = int(site_types.get(2, 0))  # ← 변경
        count_3 = int(site_types.get(3, 0))  # ← 변경
        
        results[mirna] = {
            'total_targets': total,
            '8mer': count_1,
            '7m8': count_2,
            '7a1': count_3,
            'percentages': {
                '8mer': round(count_1 / total * 100, 2) if total > 0 else 0,
                '7m8': round(count_2 / total * 100, 2) if total > 0 else 0,
                '7a1': round(count_3 / total * 100, 2) if total > 0 else 0
            }
        }
        
        count_8mer = site_types.get(1, 0)
        count_7m8 = site_types.get(2, 0)
        count_7a1 = site_types.get(3, 0)
        
        print(f"  ✓ 총 {total}개 targets")
        print(f"    - 8mer: {count_8mer} ({results[mirna]['percentages']['8mer']}%)")
        print(f"    - 7m8: {count_7m8} ({results[mirna]['percentages']['7m8']}%)")
        print(f"    - 7a1: {count_7a1} ({results[mirna]['percentages']['7a1']}%)")
    
    return results

def main():
    print("=" * 60)
    print("DC miRNA Binding Pattern 분석")
    print("=" * 60)
    
    # 파일 읽기
    filepath = 'mirna_data/Predicted_Targets_Context_Scores.default_predictions.txt'
    print(f"\n파일 로드 중: {filepath}")
    df = read_targetscan_file(filepath)
    print(f"✓ 로드 완료! 총 {len(df):,}개 rows")
    
    # 분석
    print(f"\n분석 중: {len(DC_CELL_MIRNAS)}개 miRNA")
    print("-" * 60)
    results = analyze_binding_patterns(df, DC_CELL_MIRNAS)
    
    # 결과 저장
    output_file = 'mirna_data/DC_binding_patterns.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("-" * 60)
    print(f"\n✓ 결과 저장: {output_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
