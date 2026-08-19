# visualize_binding_patterns.py
import json
import matplotlib.pyplot as plt

# JSON 파일 읽기
with open('mirna_data/b_cell_binding_patterns.json') as f:
    b_cell = json.load(f)

# 차트 그리기
mirnas = list(b_cell.keys())
percentages_8mer = [b_cell[m]['percentages']['8mer'] for m in mirnas]

plt.figure(figsize=(12, 6))
plt.bar(mirnas, percentages_8mer)
plt.xlabel('miRNA')
plt.ylabel('8mer %')
plt.title('B Cell miRNA Binding Pattern - 8mer')
plt.xticks(rotation=45)
plt.savefig('mirna_data/b_cell_binding_chart.png')
plt.show()
