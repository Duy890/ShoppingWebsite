from sqlalchemy.orm import Session

from .models import (
    Category,
    Product,
    SpecTemplate,
    GpuBenchmark,
    CpuBenchmark,
    GameRequirement,
)


def get_or_create_category(db: Session, name: str, description: str | None = None):
    category = db.query(Category).filter(Category.name == name).first()
    if category:
        return category
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_or_create_product(db: Session, product_data: dict):
    product = db.query(Product).filter(Product.name == product_data["name"]).first()
    if product:
        for key, value in product_data.items():
            setattr(product, key, value)
        db.commit()
        return product
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_or_create_spec_template(
    db: Session,
    product_type: str,
    group_name: str,
    spec_key: str,
    default_order: int,
):
    template = (
        db.query(SpecTemplate)
        .filter(
            SpecTemplate.product_type == product_type,
            SpecTemplate.group_name == group_name,
            SpecTemplate.spec_key == spec_key,
        )
        .first()
    )
    if template:
        return template
    template = SpecTemplate(
        product_type=product_type,
        group_name=group_name,
        spec_key=spec_key,
        default_order=default_order,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def create_spec_templates(db: Session):
    templates = {
        "phone": [
            ("Màn hình", "Kích thước màn hình"),
            ("Màn hình", "Công nghệ màn hình"),
            ("Màn hình", "Độ phân giải"),
            ("Camera", "Camera sau"),
            ("Camera", "Camera trước"),
            ("Hiệu năng", "Chip xử lý"),
            ("Hiệu năng", "RAM"),
            ("Lưu trữ", "Bộ nhớ trong"),
            ("Pin và sạc", "Dung lượng pin"),
            ("Pin và sạc", "Công nghệ sạc"),
        ],
        "laptop": [
            ("Màn hình", "Kích thước màn hình"),
            ("Màn hình", "Độ phân giải"),
            ("Hiệu năng", "CPU"),
            ("Hiệu năng", "GPU"),
            ("Hiệu năng", "RAM"),
            ("Lưu trữ", "Ổ cứng"),
            ("Kết nối", "Cổng kết nối"),
            ("Pin và sạc", "Thời lượng pin"),
            ("Thiết kế", "Trọng lượng"),
        ],
        "audio": [
            ("Âm thanh", "Driver"),
            ("Âm thanh", "Chống ồn"),
            ("Kết nối", "Chuẩn Bluetooth"),
            ("Pin và sạc", "Thời lượng pin"),
            ("Thiết kế", "Trọng lượng"),
        ],
    }
    for product_type, rows in templates.items():
        for index, (group_name, spec_key) in enumerate(rows):
            get_or_create_spec_template(db, product_type, group_name, spec_key, index)


def get_or_create_gpu_benchmark(db: Session, name: str, score: int, aliases: str | None = None):
    benchmark = db.query(GpuBenchmark).filter(GpuBenchmark.name == name).first()
    if benchmark:
        benchmark.score = score
        benchmark.aliases = aliases
        db.commit()
        return benchmark
    benchmark = GpuBenchmark(name=name, score=score, aliases=aliases)
    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)
    return benchmark


def get_or_create_cpu_benchmark(db: Session, name: str, score: int, aliases: str | None = None):
    benchmark = db.query(CpuBenchmark).filter(CpuBenchmark.name == name).first()
    if benchmark:
        benchmark.score = score
        benchmark.aliases = aliases
        db.commit()
        return benchmark
    benchmark = CpuBenchmark(name=name, score=score, aliases=aliases)
    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)
    return benchmark


def get_or_create_game_requirement(db: Session, game_data: dict):
    requirement = db.query(GameRequirement).filter(GameRequirement.game_name == game_data["game_name"]).first()
    if requirement:
        for key, value in game_data.items():
            setattr(requirement, key, value)
        db.commit()
        return requirement
    requirement = GameRequirement(**game_data)
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement


def create_gaming_benchmark_data(db: Session):
    gpu_rows = [
        ("NVIDIA GeForce RTX 4050", 11500, "rtx 4050,geforce rtx 4050"),
        ("NVIDIA GeForce RTX 4060", 14500, "rtx 4060,geforce rtx 4060"),
        ("NVIDIA GeForce RTX 4070", 18500, "rtx 4070,geforce rtx 4070"),
        ("NVIDIA GeForce RTX 4080", 26000, "rtx 4080,geforce rtx 4080"),
        ("NVIDIA GeForce RTX 4090", 33000, "rtx 4090,geforce rtx 4090"),
        ("NVIDIA GeForce GTX 1650", 7000, "gtx 1650,geforce gtx 1650"),
        ("AMD Radeon RX 6600", 13500, "radeon rx 6600,rx 6600"),
        ("Apple M3 Max GPU", 22000, "m3 max gpu,apple m3 max gpu"),
    ]
    for name, score, aliases in gpu_rows:
        get_or_create_gpu_benchmark(db, name, score, aliases)

    cpu_rows = [
        ("Intel Core i5-12450H", 12500, "core i5 12450h,intel i5 12450h"),
        ("Intel Core i7-13700H", 18500, "core i7 13700h,intel i7 13700h"),
        ("Intel Core i9-13900H", 21500, "core i9 13900h,intel i9 13900h"),
        ("AMD Ryzen 5 5600H", 13500, "ryzen 5 5600h"),
        ("AMD Ryzen 7 7840HS", 19500, "ryzen 7 7840hs"),
        ("Apple M3 Max", 22000, "m3 max,apple m3 max"),
    ]
    for name, score, aliases in cpu_rows:
        get_or_create_cpu_benchmark(db, name, score, aliases)

    game_rows = [
        {
            "game_name": "Cyberpunk 2077",
            "aliases": "cyberpunk,cyberpunk 2077",
            "min_gpu_score": 7000,
            "recommended_gpu_score": 11500,
            "ultra_gpu_score": 22000,
            "min_cpu_score": 9000,
            "recommended_cpu_score": 12500,
            "ultra_cpu_score": 18500,
            "min_ram_gb": 8,
            "recommended_ram_gb": 16,
            "ultra_ram_gb": 16,
        },
        {
            "game_name": "AAA Games",
            "aliases": "aaa,aaa games,modern aaa games",
            "min_gpu_score": 9000,
            "recommended_gpu_score": 14500,
            "ultra_gpu_score": 26000,
            "min_cpu_score": 10000,
            "recommended_cpu_score": 15000,
            "ultra_cpu_score": 20000,
            "min_ram_gb": 16,
            "recommended_ram_gb": 16,
            "ultra_ram_gb": 32,
        },
        {
            "game_name": "Valorant",
            "aliases": "valorant",
            "min_gpu_score": 3000,
            "recommended_gpu_score": 6000,
            "ultra_gpu_score": 9000,
            "min_cpu_score": 4000,
            "recommended_cpu_score": 8000,
            "ultra_cpu_score": 11000,
            "min_ram_gb": 4,
            "recommended_ram_gb": 8,
            "ultra_ram_gb": 16,
        },
    ]
    for game_data in game_rows:
        get_or_create_game_requirement(db, game_data)


def run_seed(db: Session) -> None:
    """Ham duy nhat duoc goi tu ben ngoai."""
    create_spec_templates(db)
    create_gaming_benchmark_data(db)
