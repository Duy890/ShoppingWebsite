"""
seed_benchmarks.py
==================
Seeds three tables that the gaming_engine needs but seed_data.py never fills:
  - gpu_benchmarks
  - cpu_benchmarks
  - game_requirements

Also patches ProductSpecification rows for laptops that have wrong/generic
CPU and GPU values from the generic SPECIFICATIONS template.

Run once after seed_database():
    python -m app.seed_benchmarks
Or import and call seed_benchmarks() from your startup script.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from app.core.database import SessionLocal
from app import models


# ---------------------------------------------------------------------------
# GPU benchmark scores (relative, PassMark-style scale)
# Higher = faster. Integrated GPUs score < 2000, discrete start ~4000+
# ---------------------------------------------------------------------------
GPU_BENCHMARKS = [
    # Integrated / ARM
    {"name": "Qualcomm Adreno X1",       "aliases": "adreno x1, snapdragon x elite gpu, snapdragon x gpu", "score": 1800},
    {"name": "Intel Iris Xe Graphics",   "aliases": "iris xe, intel xe, uhd graphics",                     "score": 1400},
    {"name": "Intel Arc 8-core",          "aliases": "intel arc integrated, arc 8",                         "score": 1900},
    {"name": "Apple M4 GPU 10-core",      "aliases": "m4 gpu, apple m4 10-core gpu",                       "score": 3200},
    {"name": "Apple M4 Pro GPU 20-core",  "aliases": "m4 pro gpu",                                         "score": 5000},
    {"name": "Apple M4 Max GPU 40-core",  "aliases": "m4 max gpu",                                         "score": 9000},
    # Discrete NVIDIA
    {"name": "NVIDIA GeForce RTX 4050",   "aliases": "rtx 4050, rtx4050",                                  "score": 9500},
    {"name": "NVIDIA GeForce RTX 4060",   "aliases": "rtx 4060, rtx4060",                                  "score": 12000},
    {"name": "NVIDIA GeForce RTX 4070",   "aliases": "rtx 4070, rtx4070",                                  "score": 15000},
    {"name": "NVIDIA GeForce RTX 4080",   "aliases": "rtx 4080, rtx4080",                                  "score": 19000},
    {"name": "NVIDIA GeForce RTX 4090",   "aliases": "rtx 4090, rtx4090",                                  "score": 24000},
    {"name": "NVIDIA GeForce RTX 3060",   "aliases": "rtx 3060, rtx3060",                                  "score": 8000},
    {"name": "NVIDIA GeForce RTX 3070",   "aliases": "rtx 3070, rtx3070",                                  "score": 11000},
    {"name": "NVIDIA GeForce RTX 3080",   "aliases": "rtx 3080, rtx3080",                                  "score": 15500},
    # Discrete AMD
    {"name": "AMD Radeon RX 7600M",       "aliases": "rx 7600m, radeon rx 7600m",                          "score": 8500},
    {"name": "AMD Radeon RX 7700S",       "aliases": "rx 7700s",                                            "score": 10000},
]

# ---------------------------------------------------------------------------
# CPU benchmark scores
# ---------------------------------------------------------------------------
CPU_BENCHMARKS = [
    # ARM
    {"name": "Qualcomm Snapdragon X Elite", "aliases": "snapdragon x elite, snapdragon x1e",               "score": 14000},
    {"name": "Qualcomm Snapdragon X Plus",  "aliases": "snapdragon x plus",                                 "score": 11000},
    # Apple Silicon
    {"name": "Apple M4",                    "aliases": "m4 chip, apple m4 base",                            "score": 15000},
    {"name": "Apple M4 Pro",                "aliases": "m4 pro chip",                                       "score": 22000},
    {"name": "Apple M4 Max",                "aliases": "m4 max chip",                                       "score": 28000},
    # Intel Core Ultra (Meteor Lake / Arrow Lake)
    {"name": "Intel Core Ultra 9 185H",     "aliases": "core ultra 9 185h, ultra 9 185h",                  "score": 19000},
    {"name": "Intel Core Ultra 7 165H",     "aliases": "core ultra 7 165h, ultra 7 165h",                  "score": 15500},
    {"name": "Intel Core Ultra 5 125H",     "aliases": "core ultra 5 125h, ultra 5 125h",                  "score": 12000},
    # AMD Ryzen
    {"name": "AMD Ryzen 9 8945HX",          "aliases": "ryzen 9 8945hx, r9 8945hx",                        "score": 21000},
    {"name": "AMD Ryzen 7 8845HS",          "aliases": "ryzen 7 8845hs, r7 8845hs",                        "score": 17000},
    {"name": "AMD Ryzen 5 8645HS",          "aliases": "ryzen 5 8645hs, r5 8645hs",                        "score": 13000},
]

# ---------------------------------------------------------------------------
# Game requirements
# gpu_score / cpu_score thresholds correspond to the entries above
# ---------------------------------------------------------------------------
GAME_REQUIREMENTS = [
    {
        "game_name": "Valorant",
        "aliases": "valorant",
        "min_gpu_score": 1400, "recommended_gpu_score": 3200, "ultra_gpu_score": 9500,
        "min_cpu_score": 5000, "recommended_cpu_score": 11000, "ultra_cpu_score": 17000,
        "min_ram_gb": 4, "recommended_ram_gb": 8, "ultra_ram_gb": 16,
    },
    {
        "game_name": "League of Legends",
        "aliases": "lol, league",
        "min_gpu_score": 1200, "recommended_gpu_score": 1800, "ultra_gpu_score": 8000,
        "min_cpu_score": 4000, "recommended_cpu_score": 9000, "ultra_cpu_score": 15000,
        "min_ram_gb": 4, "recommended_ram_gb": 8, "ultra_ram_gb": 16,
    },
    {
        "game_name": "Counter-Strike 2",
        "aliases": "cs2, counter strike 2, cs 2",
        "min_gpu_score": 1800, "recommended_gpu_score": 8000, "ultra_gpu_score": 15000,
        "min_cpu_score": 8000, "recommended_cpu_score": 14000, "ultra_cpu_score": 21000,
        "min_ram_gb": 8, "recommended_ram_gb": 12, "ultra_ram_gb": 16,
    },
    {
        "game_name": "Fortnite",
        "aliases": "fortnite",
        "min_gpu_score": 1800, "recommended_gpu_score": 9500, "ultra_gpu_score": 15000,
        "min_cpu_score": 7000, "recommended_cpu_score": 12000, "ultra_cpu_score": 19000,
        "min_ram_gb": 8, "recommended_ram_gb": 16, "ultra_ram_gb": 16,
    },
    {
        "game_name": "Minecraft",
        "aliases": "minecraft",
        "min_gpu_score": 1200, "recommended_gpu_score": 1800, "ultra_gpu_score": 8000,
        "min_cpu_score": 4000, "recommended_cpu_score": 9000, "ultra_cpu_score": 14000,
        "min_ram_gb": 4, "recommended_ram_gb": 8, "ultra_ram_gb": 16,
    },
    {
        "game_name": "PUBG",
        "aliases": "pubg, playerunknown",
        "min_gpu_score": 3200, "recommended_gpu_score": 9500, "ultra_gpu_score": 15000,
        "min_cpu_score": 9000, "recommended_cpu_score": 14000, "ultra_cpu_score": 19000,
        "min_ram_gb": 8, "recommended_ram_gb": 16, "ultra_ram_gb": 32,
    },
    {
        "game_name": "GTA V",
        "aliases": "gta v, gta 5, grand theft auto",
        "min_gpu_score": 3200, "recommended_gpu_score": 9500, "ultra_gpu_score": 15000,
        "min_cpu_score": 9000, "recommended_cpu_score": 14000, "ultra_cpu_score": 19000,
        "min_ram_gb": 8, "recommended_ram_gb": 16, "ultra_ram_gb": 32,
    },
    {
        "game_name": "Cyberpunk 2077",
        "aliases": "cyberpunk",
        "min_gpu_score": 9500, "recommended_gpu_score": 15000, "ultra_gpu_score": 19000,
        "min_cpu_score": 12000, "recommended_cpu_score": 17000, "ultra_cpu_score": 22000,
        "min_ram_gb": 16, "recommended_ram_gb": 16, "ultra_ram_gb": 32,
    },
    {
        "game_name": "Elden Ring",
        "aliases": "elden ring",
        "min_gpu_score": 8000, "recommended_gpu_score": 12000, "ultra_gpu_score": 19000,
        "min_cpu_score": 10000, "recommended_cpu_score": 15000, "ultra_cpu_score": 21000,
        "min_ram_gb": 12, "recommended_ram_gb": 16, "ultra_ram_gb": 32,
    },
    {
        "game_name": "Dota 2",
        "aliases": "dota 2, dota2",
        "min_gpu_score": 1200, "recommended_gpu_score": 3200, "ultra_gpu_score": 9500,
        "min_cpu_score": 5000, "recommended_cpu_score": 10000, "ultra_cpu_score": 15000,
        "min_ram_gb": 4, "recommended_ram_gb": 8, "ultra_ram_gb": 16,
    },
    {
        "game_name": "Genshin Impact",
        "aliases": "genshin impact, genshin",
        "min_gpu_score": 1400, "recommended_gpu_score": 3200, "ultra_gpu_score": 9500,
        "min_cpu_score": 5000, "recommended_cpu_score": 11000, "ultra_cpu_score": 17000,
        "min_ram_gb": 8, "recommended_ram_gb": 16, "ultra_ram_gb": 16,
    },
    {
        "game_name": "Call of Duty",
        "aliases": "call of duty, cod, warzone",
        "min_gpu_score": 3200, "recommended_gpu_score": 9500, "ultra_gpu_score": 15000,
        "min_cpu_score": 9000, "recommended_cpu_score": 14000, "ultra_cpu_score": 21000,
        "min_ram_gb": 8, "recommended_ram_gb": 16, "ultra_ram_gb": 32,
    },
    {
        "game_name": "AAA Games",
        "aliases": "aaa, aaa games",
        "min_gpu_score": 9500, "recommended_gpu_score": 12000, "ultra_gpu_score": 19000,
        "min_cpu_score": 12000, "recommended_cpu_score": 17000, "ultra_cpu_score": 22000,
        "min_ram_gb": 16, "recommended_ram_gb": 16, "ultra_ram_gb": 32,
    },
]

# ---------------------------------------------------------------------------
# Per-product spec overrides
# Fixes the generic SPECIFICATIONS template which gives every laptop the same
# "Apple M4 Max / Intel Core Ultra 9" and "Tích hợp / RTX 4070" values.
#
# Format: { SKU: { spec_key_substring: correct_value } }
# Any existing spec whose key contains the substring gets its value replaced.
# ---------------------------------------------------------------------------
PRODUCT_SPEC_OVERRIDES: dict[str, dict[str, str]] = {
    # ---- Microsoft Surface Laptop 7 ----
    "LAP-MSL7": {
        "cpu":  "Qualcomm Snapdragon X Elite X1E-80-100 (12-core, up to 3.4GHz)",
        "chip": "Qualcomm Snapdragon X Elite X1E-80-100",
        "gpu":  "Qualcomm Adreno X1 GPU (tích hợp)",
        "ram":  "16GB LPDDR5x",
    },
    # ---- ASUS ROG Strix G18 ----
    "LAP-ROGG18": {
        "cpu":  "Intel Core i9-14900HX (24-core, up to 5.8GHz)",
        "chip": "Intel Core i9-14900HX",
        "gpu":  "NVIDIA GeForce RTX 4090 16GB GDDR6",
        "ram":  "32GB DDR5 5600MHz",
    },
    # ---- ASUS ROG Zephyrus G16 ----
    "LAP-ROGG16": {
        "cpu":  "AMD Ryzen 9 8945HX (8-core, up to 5.2GHz)",
        "chip": "AMD Ryzen 9 8945HX",
        "gpu":  "NVIDIA GeForce RTX 4090 16GB GDDR6",
        "ram":  "32GB DDR5",
    },
    # ---- Lenovo Legion Pro 7i ----
    "LAP-LEG7": {
        "cpu":  "Intel Core i9-14900HX (24-core, up to 5.8GHz)",
        "chip": "Intel Core i9-14900HX",
        "gpu":  "NVIDIA GeForce RTX 4080 12GB GDDR6",
        "ram":  "32GB DDR5 5600MHz",
    },
    # ---- MacBook Pro 16 ----
    "LAP-MBP16": {
        "cpu":  "Apple M4 Max (16-core CPU)",
        "chip": "Apple M4 Max",
        "gpu":  "Apple M4 Max GPU 40-core",
        "ram":  "48GB Unified Memory",
    },
    # ---- MacBook Pro 14 ----
    "LAP-MBP14": {
        "cpu":  "Apple M4 Pro (14-core CPU)",
        "chip": "Apple M4 Pro",
        "gpu":  "Apple M4 Pro GPU 20-core",
        "ram":  "24GB Unified Memory",
    },
    # ---- MacBook Air 15 ----
    "LAP-MBA15": {
        "cpu":  "Apple M4 (10-core CPU)",
        "chip": "Apple M4",
        "gpu":  "Apple M4 GPU 10-core",
        "ram":  "16GB Unified Memory",
    },
}


# ---------------------------------------------------------------------------
# Seeder
# ---------------------------------------------------------------------------

def seed_benchmarks() -> None:
    session = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("  BENCHMARK & GAME REQUIREMENT SEED")
        print("=" * 60)

        # --- GPU Benchmarks ---
        print("\n--- GPU Benchmarks ---")
        for row in GPU_BENCHMARKS:
            existing = session.query(models.GpuBenchmark).filter(
                models.GpuBenchmark.name == row["name"]
            ).first()
            if existing:
                existing.aliases = row["aliases"]
                existing.score = row["score"]
                print(f"  [UPDATE] {row['name']} → score {row['score']}")
            else:
                session.add(models.GpuBenchmark(
                    id=str(uuid.uuid4()),
                    name=row["name"],
                    aliases=row["aliases"],
                    score=row["score"],
                    created_at=datetime.utcnow(),
                ))
                print(f"  [CREATE] {row['name']} → score {row['score']}")
        session.commit()

        # --- CPU Benchmarks ---
        print("\n--- CPU Benchmarks ---")
        for row in CPU_BENCHMARKS:
            existing = session.query(models.CpuBenchmark).filter(
                models.CpuBenchmark.name == row["name"]
            ).first()
            if existing:
                existing.aliases = row["aliases"]
                existing.score = row["score"]
                print(f"  [UPDATE] {row['name']} → score {row['score']}")
            else:
                session.add(models.CpuBenchmark(
                    id=str(uuid.uuid4()),
                    name=row["name"],
                    aliases=row["aliases"],
                    score=row["score"],
                    created_at=datetime.utcnow(),
                ))
                print(f"  [CREATE] {row['name']} → score {row['score']}")
        session.commit()

        # --- Game Requirements ---
        print("\n--- Game Requirements ---")
        for row in GAME_REQUIREMENTS:
            existing = session.query(models.GameRequirement).filter(
                models.GameRequirement.game_name == row["game_name"]
            ).first()
            if existing:
                for k, v in row.items():
                    setattr(existing, k, v)
                print(f"  [UPDATE] {row['game_name']}")
            else:
                session.add(models.GameRequirement(
                    id=str(uuid.uuid4()),
                    created_at=datetime.utcnow(),
                    **row,
                ))
                print(f"  [CREATE] {row['game_name']}")
        session.commit()

        # --- Per-product spec overrides ---
        print("\n--- Product Spec Overrides ---")
        for sku, overrides in PRODUCT_SPEC_OVERRIDES.items():
            product = session.query(models.Product).filter(
                models.Product.sku == sku
            ).first()
            if not product:
                print(f"  [SKIP] SKU not found: {sku}")
                continue

            specs = session.query(models.ProductSpecification).filter(
                models.ProductSpecification.product_id == product.id
            ).all()

            for spec in specs:
                key_lower = (spec.spec_key or "").lower()
                for target_key, new_value in overrides.items():
                    if target_key in key_lower:
                        old = spec.spec_value
                        spec.spec_value = new_value
                        print(f"  [FIX] {sku} / {spec.spec_key}: '{old}' → '{new_value}'")
                        break

        session.commit()
        print("\n" + "=" * 60)
        print("  Benchmark seed completed!")
        print("=" * 60)

    except Exception as exc:
        session.rollback()
        print(f"\n[ERROR] Benchmark seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_benchmarks()
