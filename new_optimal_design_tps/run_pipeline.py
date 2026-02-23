from subprocess import run


def main():
    run(
        [
            "python3",
            "new_optimal_design_tps/generate_zone_database.py",
            "--phase-step",
            "0.01",
            "--v2-step",
            "1.0",
        ],
        check=True,
    )
    run(
        [
            "python3",
            "new_optimal_design_tps/build_optimized_dataset.py",
            "--power-min",
            "0",
            "--power-max",
            "3500",
            "--power-step",
            "10",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
