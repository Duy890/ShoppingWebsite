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


def run_seed(db: Session) -> None:
    """Ham duy nhat duoc goi tu ben ngoai."""
    create_spec_templates(db)
    # Benchmark data được quản lý tập trung trong seed_data.py
