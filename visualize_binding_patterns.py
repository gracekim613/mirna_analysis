import json
import matplotlib.pyplot as plt
import numpy as np

# JSON 파일 읽기
with open('mirna_data/dc_binding_patterns.json') as f:
    dc_cell = json.load(f)

# 데이터 준비
mirnas = list(dc_cell.keys())
percentages_8mer = [dc_cell[m]['percentages']['8mer'] for m in mirnas]
percentages_7m8 = [dc_cell[m]['percentages']['7m8'] for m in mirnas]
percentages_7a1 = [dc_cell[m]['percentages']['7a1'] for m in mirnas]

# Stacked Bar Chart
fig, ax = plt.subplots(figsize=(14, 6))

x = np.arange(len(mirnas))
width = 0.6

ax.bar(x, percentages_8mer, width, label='8mer', color='powderblue')
ax.bar(x, percentages_7m8, width, bottom=percentages_8mer, label='7m8', color='lightblue')
ax.bar(x, percentages_7a1, width, 
       bottom=np.array(percentages_8mer) + np.array(percentages_7m8), 
       label='7a1', color='skyblue')

ax.set_ylabel('Percentage (%)', fontsize=12)
ax.set_title('DC Cell miRNA Binding Pattern Distribution', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(mirnas, rotation=45, ha='right')
ax.legend()
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('mirna_data/dc_cell_binding_pattern_stacked.png', dpi=300)
plt.show()

print("✓ 저장: mirna_data/dc_cell_binding_pattern_stacked.png")
