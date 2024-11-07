import openpyxl
import json

wb=openpyxl.load_workbook("../config/example_scenario_1.xlsx")
sheet = wb['Hex Table']

json_data = {}

for col in sheet.iter_rows(values_only=True):
    if col[0] != 'Node':
        json_data[col[0]] = {'Terrain': col[1], 'AI Confidence': col[2], 'Human Confidence': col[3], 'Mine': col[4]}
with open('../config/example_scenario_1.json', 'w') as file:
    json.dump(json_data, file)