"""Execute the entire local analysis and regenerate publication figures.

Usage from the project folder: python run_analysis.py
"""
from pathlib import Path
from src.analysis import main_analysis
from src.visuals import generate_all_figures
ROOT=Path(__file__).resolve().parent
results=main_analysis(ROOT/'car_data.csv',ROOT/'reports')
generate_all_figures(results,ROOT/'assets')
print('Champion:',results['summary']['champion'])
print('Five-fold CV ranking:\n',results['table'].to_string(index=False))
print('Final held-out metrics:\n',results['summary']['final_test'])
print('Stress-test metrics:\n',results['summary']['unseen_model_stress']['metrics'])
print('Generated assets:',len(list((ROOT/'assets').glob('*.png'))))
