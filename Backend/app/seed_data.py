import uuid

from .core.database import SessionLocal
from .models import Category, Product, ProductSpecification

CATEGORY_NAMES = [
    "Điện thoại",
    "Laptop",
    "Tai nghe",
    "Đồng hồ thông minh",
    "Phụ kiện",
]

PRODUCTS = [
    {
        "name": "Samsung Galaxy S24 Ultra",
        "description": "Flagship smartphone with 200MP camera, vapor chamber cooling, and 5G performance.",
        "price": 24990000.0,
        "stock": 30,
        "category_name": "Điện thoại",
        "brand": "Samsung",
        "sku": "SAM-GS24U-256",
        "product_type": "phone",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1705908045920-64346bf9a36f?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "iPhone 15 Pro Max",
        "description": "Premium Apple smartphone with titanium frame, A17 Pro chip, and advanced camera system.",
        "price": 31990000.0,
        "stock": 18,
        "category_name": "Điện thoại",
        "brand": "Apple",
        "sku": "APL-IP15PM-256",
        "product_type": "phone",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1571031663400-2d973f86d703?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "ASUS ROG Zephyrus G16",
        "description": "Ultra-thin gaming laptop with RTX 4070, 240Hz QHD display and advanced cooling.",
        "price": 42990000.0,
        "stock": 14,
        "category_name": "Laptop",
        "brand": "ASUS",
        "sku": "ASU-ZG16-RTX4070",
        "product_type": "laptop",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "MacBook Pro 16-inch M3",
        "description": "Apple notebook with M3 chip, Liquid Retina XDR display, and long battery life.",
        "price": 63990000.0,
        "stock": 10,
        "category_name": "Laptop",
        "brand": "Apple",
        "sku": "APL-MBP16-M3",
        "product_type": "laptop",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Industry-leading noise cancelling headphones with immersive sound and 30-hour battery.",
        "price": 8490000.0,
        "stock": 40,
        "category_name": "Tai nghe",
        "brand": "Sony",
        "sku": "SON-WH1000XM5",
        "product_type": "audio",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1511376777868-611b54f68947?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "Bose QuietComfort Ultra",
        "description": "Wireless over-ear headset with next-gen noise cancellation and premium comfort.",
        "price": 10990000.0,
        "stock": 28,
        "category_name": "Tai nghe",
        "brand": "Bose",
        "sku": "BOSE-QC-ULTRA",
        "product_type": "audio",
        "featured": False,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1516707570267-0f74c2b6d938?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "Apple Watch Series 9",
        "description": "Smartwatch with fast S9 chip, fall detection, and powerful health tracking.",
        "price": 12990000.0,
        "stock": 22,
        "category_name": "Đồng hồ thông minh",
        "brand": "Apple",
        "sku": "APL-AW-S9",
        "product_type": "watch",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "Samsung Galaxy Watch 6",
        "description": "Fitness smartwatch with AMOLED display, ECG, and long battery life.",
        "price": 8990000.0,
        "stock": 26,
        "category_name": "Đồng hồ thông minh",
        "brand": "Samsung",
        "sku": "SAM-GW6",
        "product_type": "watch",
        "featured": False,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1539886179690-7f3a7e75fb69?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "Logitech G502 Lightspeed Wireless",
        "description": "High-performance gaming mouse with 25K sensor, dual-mode wireless, and tunable weights.",
        "price": 3490000.0,
        "stock": 60,
        "category_name": "Phụ kiện",
        "brand": "Logitech",
        "sku": "LOG-G502-WL",
        "product_type": "accessory",
        "featured": False,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1615874959470-29b05bd16a70?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "name": "Razer BlackWidow V4 Pro",
        "description": "Mechanical keyboard with optical switches, RGB lighting, and dedicated macro keys.",
        "price": 5290000.0,
        "stock": 35,
        "category_name": "Phụ kiện",
        "brand": "Razer",
        "sku": "RAZ-BW-V4P",
        "product_type": "accessory",
        "featured": True,
        "status": "active",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
    },
]

SPECIFICATIONS = {
    "phone": [
        ("Màn hình", "Kích thước màn hình", "6.8 inches"),
        ("Màn hình", "Độ phân giải", "3088 x 1440"),
        ("Camera", "Camera sau chính", "200 MP"),
        ("Camera", "Camera trước", "12 MP"),
        ("Chipset", "Bộ vi xử lý", "Qualcomm Snapdragon 8 Gen 3"),
        ("Pin", "Dung lượng pin", "5000 mAh"),
        ("Pin", "Sạc nhanh", "65W Wired"),
        ("Hệ điều hành", "OS", "Android 14"),
        ("Bộ nhớ", "RAM", "12 GB"),
        ("Bộ nhớ", "Bộ nhớ trong", "256 GB"),
        ("Kết nối", "Bluetooth", "5.3"),
        ("Kết nối", "5G", "Supported"),
    ],
    "laptop": [
        ("Hiệu năng", "CPU", "Intel Core i9-13900H"),
        ("Hiệu năng", "GPU", "NVIDIA GeForce RTX 4070"),
        ("Hiệu năng", "RAM", "32 GB DDR5"),
        ("Lưu trữ", "SSD", "1 TB PCIe NVMe"),
        ("Màn hình", "Kích thước màn hình", "16 inches"),
        ("Màn hình", "Độ phân giải", "2560 x 1600"),
        ("Màn hình", "Tần số quét", "240 Hz"),
        ("Pin", "Dung lượng pin", "90 Wh"),
        ("Thiết kế", "Trọng lượng", "1.9 kg"),
        ("Kết nối", "Cổng USB-C", "2 x Thunderbolt 4"),
        ("Kết nối", "HDMI", "1 x HDMI 2.1"),
    ],
    "audio": [
        ("Âm thanh", "ANC", "Active Noise Cancelling"),
        ("Âm thanh", "Driver", "40 mm"),
        ("Pin", "Thời lượng pin", "30 hours"),
        ("Kết nối", "Bluetooth", "5.2"),
        ("Kết nối", "Codec", "LHDC / aptX Adaptive"),
        ("Thiết kế", "Trọng lượng", "250 g"),
        ("Tính năng", "Microphone", "Multi-mic"),
        ("Tính năng", "Chế độ không gian", "Immersive Sound"),
        ("Kết nối", "Wireless", "Yes"),
        ("Tính năng", "Hệ thống điều khiển", "Touch Controls"),
    ],
    "watch": [
        ("Màn hình", "Kích thước màn hình", "1.9 inches AMOLED"),
        ("Màn hình", "Độ phân giải", "410 x 502"),
        ("Sức khỏe", "Đo nhịp tim", "Continuous"),
        ("Sức khỏe", "ECG", "Supported"),
        ("Sức khỏe", "Theo dõi giấc ngủ", "Yes"),
        ("Pin", "Dung lượng pin", "18 hours"),
        ("Kết nối", "Bluetooth", "5.3"),
        ("Kết nối", "GPS", "Built-in"),
        ("Tính năng", "Chống nước", "50m"),
        ("Tính năng", "Tương thích", "iOS & Android"),
    ],
    "accessory": [
        ("Bàn phím", "Loại switch", "Optical Mechanical"),
        ("Bàn phím", "Nút macro", "5 programmable"),
        ("Chuột", "DPI", "25000"),
        ("Chuột", "Tốc độ polling", "1000 Hz"),
        ("Kết nối", "Connectivity", "Wireless / USB-C"),
        ("Kết nối", "Bluetooth", "Supported"),
        ("Tính năng", "Lighting", "RGB"),
        ("Tính năng", "Compatibility", "Windows / macOS"),
        ("Tính năng", "Battery", "120 hours"),
        ("Thiết kế", "Weight", "114 g"),
    ],
}


def get_or_create_category(session, name: str) -> Category:
    existing = session.query(Category).filter(Category.name == name).first()
    if existing:
        return existing

    category = Category(name=name, description=f"Danh mục {name} cho thiết bị điện tử.")
    session.add(category)
    session.flush()
    print(f"[CREATED] Category: {name}")
    return category


def create_product(session, product_data: dict, category_map: dict[str, Category]):
    sku = product_data["sku"]
    existing = session.query(Product).filter(Product.sku == sku).first()
    if existing:
        print(f"[SKIPPED] SKU exists: {sku}")
        return None

    category = category_map.get(product_data["category_name"])
    if category is None:
        raise ValueError(f"Unknown category for product: {product_data['name']}")

    product = Product(
        id=str(uuid.uuid4()),
        name=product_data["name"],
        description=product_data["description"],
        price=product_data["price"],
        stock=product_data["stock"],
        category_id=category.id,
        brand=product_data["brand"],
        sku=sku,
        product_type=product_data["product_type"],
        featured=product_data["featured"],
        status=product_data["status"],
        image_url=product_data["image_url"],
        embedding=None,
        rating=0.0,
        review_count=0,
        view_count=0,
    )
    session.add(product)
    session.flush()
    print(f"[CREATED] Product: {product.name}")
    return product


def create_product_specifications(session, product: Product):
    template_list = SPECIFICATIONS.get(product.product_type, [])
    if not template_list:
        return

    specs_created = 0
    for index, (group_name, spec_key, spec_value) in enumerate(template_list, start=1):
        spec = ProductSpecification(
            product_id=product.id,
            group_name=group_name,
            spec_key=spec_key,
            spec_value=spec_value,
            display_order=index,
        )
        session.add(spec)
        specs_created += 1

    session.flush()
    print(f"[CREATED] Specs: {product.name} ({specs_created} items)")


def seed_database():
    session = SessionLocal()
    try:
        print("Starting seed process...")

        category_map = {}
        for name in CATEGORY_NAMES:
            category = get_or_create_category(session, name)
            category_map[name] = category

        session.commit()

        for product_data in PRODUCTS:
            product = create_product(session, product_data, category_map)
            if product is None:
                continue
            create_product_specifications(session, product)
            session.commit()

        print("Seed process completed successfully.")
    except Exception as exc:
        session.rollback()
        print(f"[ERROR] Seed process failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
