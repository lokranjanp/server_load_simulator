import pandas as pd
import numpy as np

# Load raw server log CSV
df = pd.read_csv("server_metrics.csv")  # assuming it has: load_avg, cpu_percent, memory_percent

# Define a custom scoring function (can tweak weights)
def generate_score(row):
    return 100 - ((np.random.randint(3,5))/10 * row['load_avg'] + (np.random.randint(1, 4))/10 * row['cpu_percent'] + (np.random.randint(15, 25))/100 * row['memory_percent'])

# Apply it
df['actual_score'] = df.apply(generate_score, axis=1)

# Save it
df.to_csv("scored_server_logs.csv", index=False)

print("✅ Scores generated and saved to 'scored_server_logs.csv'")
