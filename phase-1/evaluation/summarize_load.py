import pandas as pd

FILE = "evaluation/load_results_phase1_final.csv"

df = pd.read_csv(FILE)

print("========================================")
print("AgroMind Final Load Benchmark Summary")
print("========================================")

for concurrency in sorted(df["concurrency"].unique()):
    part = df[df["concurrency"] == concurrency]

    successful = part[part["success"] == True]

    total_time = part["total_level_time_seconds"].iloc[0]

    throughput = len(successful) / total_time

    mean_latency = successful["latency_seconds"].mean()
    p50 = successful["latency_seconds"].quantile(0.50)
    p95 = successful["latency_seconds"].quantile(0.95)

    print(f"\nConcurrency: {concurrency}")
    print(f"Successful: {len(successful)}/{len(part)}")
    print(f"Throughput: {throughput:.2f} requests/sec")
    print(f"Mean latency: {mean_latency:.3f} sec")
    print(f"p50 latency: {p50:.3f} sec")
    print(f"p95 latency: {p95:.3f} sec")
