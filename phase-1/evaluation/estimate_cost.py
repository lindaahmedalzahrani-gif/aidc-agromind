import argparse


# Measurements from the Phase 1 benchmark
PEAK_GPU_POWER_W = 283.84
THROUGHPUT_REQ_PER_SEC = 53.42


def main():
    parser = argparse.ArgumentParser(
        description="Estimate AgroMind GPU electricity cost."
    )

    parser.add_argument(
        "--tariff",
        type=float,
        required=True,
        help="Electricity tariff in SAR per kWh"
    )

    args = parser.parse_args()

    power_kw = PEAK_GPU_POWER_W / 1000

    # Electricity cost if GPU operated at measured peak power
    cost_per_hour = power_kw * args.tariff

    # Time required for 1,000 requests at measured throughput
    seconds_per_1000 = 1000 / THROUGHPUT_REQ_PER_SEC
    hours_per_1000 = seconds_per_1000 / 3600

    energy_per_1000_kwh = power_kw * hours_per_1000
    cost_per_1000 = energy_per_1000_kwh * args.tariff

    energy_per_million_kwh = energy_per_1000_kwh * 1000
    cost_per_million = cost_per_1000 * 1000

    print("========================================")
    print("AgroMind GPU Electricity Cost Estimate")
    print("========================================")

    print(f"Peak measured GPU power: {PEAK_GPU_POWER_W:.2f} W")
    print(
        f"Measured throughput: "
        f"{THROUGHPUT_REQ_PER_SEC:.2f} requests/sec"
    )

    print(f"\nElectricity tariff: {args.tariff:.4f} SAR/kWh")

    print(f"\nGPU electricity cost/hour: {cost_per_hour:.6f} SAR")

    print("\nAt measured concurrency-16 throughput:")

    print(
        f"Time for 1,000 requests: "
        f"{seconds_per_1000:.2f} seconds"
    )

    print(
        f"GPU energy per 1,000 requests: "
        f"{energy_per_1000_kwh:.6f} kWh"
    )

    print(
        f"GPU electricity cost per 1,000 requests: "
        f"{cost_per_1000:.6f} SAR"
    )

    print(
        f"GPU energy per 1,000,000 requests: "
        f"{energy_per_million_kwh:.3f} kWh"
    )

    print(
        f"GPU electricity cost per 1,000,000 requests: "
        f"{cost_per_million:.4f} SAR"
    )

    print("\nIMPORTANT:")
    print(
        "This is a GPU-only electricity estimate. "
        "It excludes CPU, RAM, storage, networking, cooling, "
        "server purchase/depreciation, maintenance, and idle time."
    )


if __name__ == "__main__":
    main()
