# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 14:28:54 2024

@author: Jan Hendrik Schmidt
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler

base_dir = 'E:/tmpDATA/GPCR_array/'  # Work

df = pd.read_excel(base_dir + "GPCR array data.xlsx")

# %% reading and tidying of scRNAseq data

df_selection = df[df["Sample_type"] == "sample"]

df_rna_seq = pd.read_excel(base_dir + "RNA_seq_cleaned.xlsx")

fraction_Tiklova = []
fraction_LaManno = []
fraction_Saunders = []
fraction_Kramer = []
fraction_Hook = []

for i in df_selection["Gene Symbol"]:
    if i in df_rna_seq["Gene_Name"].values:
        fraction_Tiklova.append(df_rna_seq["Tiklova_fraction"][df_rna_seq["Gene_Name"].index[df_rna_seq["Gene_Name"].eq(i)]].values[0])
        fraction_LaManno.append(df_rna_seq["LaManno_fraction"][df_rna_seq["Gene_Name"].index[df_rna_seq["Gene_Name"].eq(i)]].values[0])
        fraction_Saunders.append(df_rna_seq["Saunders_fraction"][df_rna_seq["Gene_Name"].index[df_rna_seq["Gene_Name"].eq(i)]].values[0])
        fraction_Kramer.append(df_rna_seq["Kramer_fraction"][df_rna_seq["Gene_Name"].index[df_rna_seq["Gene_Name"].eq(i)]].values[0])
        fraction_Hook.append(df_rna_seq["Hook_fraction"][df_rna_seq["Gene_Name"].index[df_rna_seq["Gene_Name"].eq(i)]].values[0])
    else:
        fraction_Tiklova.append(0)
        fraction_LaManno.append(0)
        fraction_Saunders.append(0)
        fraction_Kramer.append(0)
        fraction_Hook.append(0)        

df_selection["Tiklova_fraction"] = fraction_Tiklova
df_selection["LaManno_fraction"] = fraction_LaManno
df_selection["Saunders_fraction"] = fraction_Saunders
df_selection["Kramer_fraction"] = fraction_Kramer
df_selection["Hook_fraction"] = fraction_Hook

scaler = StandardScaler()
df_selection["Mean RE EGFP+_z-score"] = scaler.fit_transform(df_selection[["Mean RE EGFP+"]])

correlation_columns = ['Mean RE EGFP+_z-score','Tiklova_fraction','LaManno_fraction', 'Saunders_fraction', 'Kramer_fraction', 'Hook_fraction']

# Compute Pearson correlation matrix between selected columns
correlation_matrix = df_selection[correlation_columns].corr()

df_selection_positives = df_selection[df_selection["Mean RE EGFP+"]-df_selection["Mean RE StD. EGFP+"] > 0]

rna_seq_datasets = ['Tiklova_fraction', 'LaManno_fraction', 'Saunders_fraction', 'Kramer_fraction', 'Hook_fraction']

number_of_receptors_detected = []
percentage_receptors_detected = []
for dataset in rna_seq_datasets:
    receptor_with_expression = []
    for receptor in df_selection_positives[dataset]:
        if receptor > 0.03:
            receptor_with_expression.append("yes")
            
    number_of_receptors_detected.append(len(receptor_with_expression))
    percentage_receptors_detected.append(len(receptor_with_expression)/len(df_selection_positives[dataset])*100)
