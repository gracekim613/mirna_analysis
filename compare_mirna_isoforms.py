import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# TargetScan 데이터 읽기
df = pd.read_csv('mirna_data/Predicted_Targets_Context_Scores.default_predictions.txt', 
                  sep='\t', low_memory=False)

# 세 가지 경우 분석
def analyze_mirna(mirna_data):
    """binding pattern 분석"""
    if len(mirna_data) == 0:
        return {'8mer': 0, '7m8': 0, '7a1': 0, 'total': 0}
    
    site_types = mirna_data['Site Type'].value_counts()
    total = len(mirna_data)
    
    count_1 = int(site_types.get(1, 0))
    count_2 = int(site_types.get(2, 0))
    count_3 = int(site_types.get(3, 0))
    
    return {
        '8mer': round(count_1 / total * 100, 2),
        '7m8': round(count_2 / total * 100, 2),
        '7a1': round(count_3 / total * 100, 2),
        'total': total
    }

# 데이터 추출
data_all = df[df['miRNA'].str.contains('hsa-miR-133a-3p', na=False)]
data_1 = df[df['miRNA'] == 'hsa-miR-133a-3p.1']
data_2 = df[df['miRNA'] == 'hsa-miR-133a-3p.2']

# 분석
result_all = analyze_mirna(data_all)
result_1 = analyze_mirna(data_1)
result_2 = analyze_mirna(data_2)

print(f"133a 전체: {result_all['total']}개")
print(f"133a-3p.1: {result_1['total']}개")
print(f"133a-3p.2: {result_2['total']}개")

# 그래프 그리기
fig, ax = plt.subplots(figsize=(10, 6))

categories = ['hsa-miR-133a\n(all)', 'hsa-miR-133a-3p.1', 'hsa-miR-133a-3p.2']
x = np.arange(len(categories))
width = 0.25

results = [result_all, result_1, result_2]
percentages_8mer = [r['8mer'] for r in results]
percentages_7m8 = [r['7m8'] for r in results]
percentages_7a1 = [r['7a1'] for r in results]

# Stacked bar chart
ax.bar(x, percentages_8mer, width, label='8mer', color='paleturquoise')
ax.bar(x, percentages_7m8, width, bottom=percentages_8mer, label='7m8', color='skyblue')
ax.bar(x, percentages_7a1, width, 
       bottom=np.array(percentages_8mer) + np.array(percentages_7m8), 
       label='7a1', color='lightskyblue')

ax.set_ylabel('Percentage (%)', fontsize=12)
ax.set_title('hsa-miR-133a Binding Pattern Comparison\n(전체 vs .1 vs .2)', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('mirna_data/hsa-miR-133a_comparison.png', dpi=300)
plt.show

print("✓ 저장: mirna_data/hsa-miR-133a_comparison.png")
