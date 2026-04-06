import pandas as pd
from datetime import datetime

def save_to_csv(results, output_file="output/results.csv"):
    df = pd.DataFrame(results)
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Výsledky uloženy do {output_file}")
