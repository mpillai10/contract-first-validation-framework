import pandas as pd
import json
import re

# Load contract
with open("Customer_Contract.json", "r") as f:
    contract = json.load(f)

# Load data
df = pd.read_csv("Custome_Data.csv")
errors = []
