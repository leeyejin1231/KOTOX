import pandas as pd
from irrCAC.raw import CAC

ano1 = pd.read_csv("./data/annotator_1.csv")
ano2 = pd.read_csv("./data/annotator_2.csv")
ano3 = pd.read_csv("./data/annotator_3.csv")

data = pd.DataFrame({
    'rater1': ano1['label'].tolist(),
    'rater2': ano2['label'].tolist(),
    'rater3': ano3['label'].tolist()
})

# Gwet's AC1 calculation
cac = CAC(data, categories=[0,1])
result = cac.gwet()


print("Gwet’s AC1:", round(result['est']['coefficient_value'], 4))
print("95% CI:", (result['est']['confidence_interval']))
print("Interpretation:", result['est']['p_value'])