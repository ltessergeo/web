import pandas as pd
from pyscript import document


# Define your sample and initial composition data
sample = "DLT01"
dataset = pd.DataFrame({
    'SiO2': [60.41], 'TiO2': [0.93], 'Al2O3': [20.1], 'Fe2O3': [0], 'FeO': [5.68],
    'MnO': [0.08], 'MgO': [2.3], 'CaO': [1.06], 'Na2O': [1.53], 'K2O': [4.17], 'P2O5': [0.15], 'H2O': [0]
})

# Set the values of Fe3+/Fe2+ ratio, water mol%, and apatite presence
Fe3prop = 0.1
watermol = 10
apt = "yes"

# Define molecular weights of oxides
Moloxide = pd.DataFrame({
    'SiO2': [60.09], 'TiO2': [79.9], 'Al2O3': [101.94], 'Fe2O3': [159.69], 'FeO': [71.85],
    'MnO': [70.94], 'MgO': [40.3], 'CaO': [56.08], 'Na2O': [61.98], 'K2O': [94.2], 'P2O5': [141.94], 'H2O': [18.02]
})

# Calculate oxide proportions
oxidepp = dataset / Moloxide

# Calculate corrected Fe2O3 values
Fecorr = oxidepp.copy()
Fecorr['Fe2O3'] = Fe3prop * (oxidepp['Fe2O3'] + 0.5 * oxidepp['FeO'])

# Correct P2O5 values for apatite presence
Aptcorr = Fecorr.copy()
if apt == "yes":
    Aptcorr['CaO'] -= 10 / 3 * Fecorr['P2O5']

# Sum of columns excluding P2O5 and H2O
Aptcorr = Aptcorr.drop(columns=['P2O5', 'H2O'])
Aptcorr['SUM'] = Aptcorr.sum(axis=1)

# Calculate molecular percentages
MolPerc = Aptcorr.div(Aptcorr['SUM'], axis=0) * 100

# Calculate MolF by dividing each column by adjusted extra O2 and multiplying by 100
MolF = MolPerc.div(MolPerc['SUM'] + (2 * MolPerc['Fe2O3']), axis=0) * 100
MolF.rename(columns={'Fe2O3': 'O2'}, inplace=True)
MolF = MolF.drop(columns=['SUM'])

# Adjust for water presence
TC = MolF * (1 - watermol / 100)

# Calculate Oxigens and Cations dataframes
Oxigens = pd.DataFrame({
    'Si': TC['SiO2'] * 2, 'Ti': TC['TiO2'] * 2, 'Al': TC['Al2O3'] * 3, 'Fe': TC['FeO'], 'Mn': TC['MnO'],
    'Mg': TC['MgO'], 'Ca': TC['CaO'], 'Na': TC['Na2O'], 'K': TC['K2O'], 'H': [watermol], 'O': TC['O2']
})

CationsO2 = pd.DataFrame({
    'SI': TC['SiO2'], 'TI': TC['TiO2'], 'AL': TC['Al2O3'] * 2, 'FE': TC['FeO'], 'MN': TC['MnO'],
    'MG': TC['MgO'], 'CA': TC['CaO'], 'NA': TC['Na2O'], 'K': TC['K2O'] * 2, 'H': [watermol * 2], 'O': TC['O2']
})

CationsF3 = pd.DataFrame({
    'SI': TC['SiO2'], 'TI': TC['TiO2'], 'AL': TC['Al2O3'] * 2, 'FE': TC['FeO'], 'F3': TC['O2'] * 2, 'MN': TC['MnO'],
    'MG': TC['MgO'], 'CA': TC['CaO'], 'NA': TC['Na2O'], 'K': TC['K2O'] * 2, 'H': [watermol * 2]
})

# Prepare output strings
ds62 = " ".join([f"{col}({CationsO2[col].iloc[0]:.3f})" for col in CationsO2.columns])
ds55 = " ".join([f"{col}({CationsF3[col].iloc[0]:.3f})" for col in CationsF3.columns])

print(f"0   {ds62} O(?)    * {sample} Fe3/Fe2 = {Fe3prop} | H2O= {watermol} [ds62]")
print(f"0   {ds55} O(?)    * {sample} Fe3/Fe2 = {Fe3prop} | H2O= {watermol} [ds55]")
