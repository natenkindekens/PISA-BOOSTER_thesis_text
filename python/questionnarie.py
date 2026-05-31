import pandas as pd

# 45 rows, columns Q1..Q7, values 1-4
df = pd.read_csv("data/Questionnaire.csv")

# Reverse-code the negative items inside each scale
for q in ["Q2", "Q4"]:
    df[q] = 5 - df[q]

def cronbach_alpha(items):
    k = items.shape[1]
    item_var  = items.var(ddof=1).sum()
    total_var = items.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_var / total_var)

engagement        = df[["Q1", "Q2", "Q5"]]   # 3 items
user_friendliness = df[["Q3", "Q4"]]         # 2 items

print("Engagement:",        round(cronbach_alpha(engagement), 2))
print("User friendliness:", round(cronbach_alpha(user_friendliness), 2))