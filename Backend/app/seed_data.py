import uuid

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from .core.database import SessionLocal
from .models import Category, Product, ProductVariant, ProductSpecification, RelatedProduct

# ---------------------------------------------------------------------------
# Category hierarchy
# ---------------------------------------------------------------------------
CATEGORY_TREE = [
    {
        "name": "Điện thoại",
        "slug": "dien-thoai",
        "children": [
            {"name": "Apple iPhone", "slug": "apple-iphone"},
            {"name": "Samsung Galaxy", "slug": "samsung-galaxy"},
            {"name": "Xiaomi", "slug": "xiaomi"},
            {"name": "OPPO", "slug": "oppo"},
            {"name": "Vivo", "slug": "dien-thoai-vivo"},
        ],
    },
    {
        "name": "Laptop",
        "slug": "laptop",
        "children": [
            {"name": "Apple MacBook", "slug": "apple-macbook"},
            {"name": "ASUS", "slug": "asus"},
            {"name": "Dell", "slug": "dell"},
            {"name": "Lenovo", "slug": "laptop-lenovo"},
            {"name": "HP", "slug": "hp"},
            {"name": "Acer", "slug": "acer"},
            {"name": "MSI", "slug": "msi"},
            {"name": "LG", "slug": "lg"},
            {"name": "Microsoft Surface", "slug": "microsoft-surface"},
        ],
    },
    {
        "name": "Máy tính bảng",
        "slug": "tablet",
        "children": [
            {"name": "iPad", "slug": "ipad"},
            {"name": "Samsung Galaxy Tab", "slug": "samsung-tablet"},
            {"name": "Xiaomi Pad", "slug": "xiaomi-tablet"},
        ],
    },
    {
        "name": "Âm thanh",
        "slug": "am-thanh",
        "children": [
            {"name": "Tai nghe Bluetooth", "slug": "tai-nghe-bluetooth"},
            {"name": "Tai nghe có dây", "slug": "tai-nghe-co-day"},
            {"name": "Loa", "slug": "loa"},
        ],
    },
    {
        "name": "Đồng hồ",
        "slug": "dong-ho",
        "children": [
            {"name": "Apple Watch", "slug": "apple-watch"},
            {"name": "Samsung Galaxy Watch", "slug": "samsung-galaxy-watch"},
            {"name": "Xiaomi", "slug": "xiaomi-watch"},
            {"name": "Huawei", "slug": "huawei-watch"},
            {"name": "Garmin", "slug": "garmin"},
        ],
    },
    {
        "name": "Phụ kiện",
        "slug": "phu-kien",
        "children": [
            {
                "name": "Phụ kiện di động",
                "slug": "phu-kien-di-dong",
                "children": [
                    {"name": "Ốp lưng & Bao da", "slug": "op-lung-bao-da"},
                    {"name": "Dán màn hình", "slug": "dan-man-hinh"},
                    {"name": "Cáp sạc & Sạc", "slug": "sac-cap"},
                    {"name": "Pin dự phòng", "slug": "pin-du-phong"},
                    {"name": "Sim 4G/5G", "slug": "sim-4g-5g"},
                ]
            },
            {
                "name": "Phụ kiện laptop",
                "slug": "phu-kien-laptop",
                "children": [
                    {"name": "Chuột", "slug": "chuot"},
                    {"name": "Bàn phím", "slug": "ban-phim"},
                    {"name": "Webcam", "slug": "webcam"},
                    {"name": "Hub chuyển đổi", "slug": "hub-chuyen-doi"},
                ]
            },
            {
                "name": "Thiết bị mạng",
                "slug": "thiet-bi-mang",
                "children": [
                    {"name": "Router WiFi", "slug": "router-wifi"},
                    {"name": "USB WiFi", "slug": "usb-wifi"},
                    {"name": "Switch", "slug": "switch"},
                ]
            },
            {
                "name": "Thiết bị lưu trữ",
                "slug": "thiet-bi-luu-tru",
                "children": [
                    {"name": "SSD", "slug": "ssd"},
                    {"name": "HDD", "slug": "hdd"},
                    {"name": "USB", "slug": "usb-storage"},
                    {"name": "Thẻ nhớ", "slug": "the-nho"},
                ]
            }
        ],
    },
    {
        "name": "Gaming",
        "slug": "gaming",
        "children": [
            {"name": "Laptop Gaming", "slug": "laptop-gaming"},
            {"name": "PC Gaming", "slug": "pc-gaming"},
            {"name": "Phụ kiện Gaming", "slug": "phu-kien-gaming"},
        ],
    }
]

# ---------------------------------------------------------------------------
# Product seed data
# ---------------------------------------------------------------------------

PRODUCTS = [
    # -- Phones: Apple iPhone --
    {
        "name": "iPhone 16 Pro Max",
        "slug": "iphone-16-pro-max",
        "brand": "Apple",
        "sku": "PHN-IP16PM",
        "product_type": "phone",
        "featured": True,
        "category_slug": "apple-iphone",
        "description": "Flagship iPhone với chip A18 Pro, màn hình 6.9 inch Super Retina XDR OLED, camera 48MP Fusion và telephoto 5x, pin dung lượng lớn nhất.",
        "image_url": "https://images.unsplash.com/photo-1592899677977-9c10a5884a5c?w=800&q=80",
        "variants": [
            {"color_name": "Natural Titanium", "color_code": "#8B8B8B", "storage": "256GB", "ram": "8GB", "sku": "PHN-IP16PM-256-NT", "price": 34990000, "stock": 50, "is_default": True},
            {"color_name": "Desert Titanium", "color_code": "#C4A882", "storage": "512GB", "ram": "8GB", "sku": "PHN-IP16PM-512-DT", "price": 39990000, "stock": 35},
            {"color_name": "White Titanium", "color_code": "#F5F5F5", "storage": "1TB", "ram": "8GB", "sku": "PHN-IP16PM-1TB-WT", "price": 45990000, "stock": 20},
        ],
    },
    {
        "name": "iPhone 16 Pro",
        "slug": "iphone-16-pro",
        "brand": "Apple",
        "sku": "PHN-IP16P",
        "product_type": "phone",
        "featured": True,
        "category_slug": "apple-iphone",
        "description": "iPhone 16 Pro với chip A18 Pro, màn hình 6.3 inch OLED, camera 48MP Fusion và nút Camera Control.",
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a7352e5c1c1?w=800&q=80",
        "variants": [
            {"color_name": "Natural Titanium", "color_code": "#8B8B8B", "storage": "128GB", "ram": "8GB", "sku": "PHN-IP16P-128-NT", "price": 28990000, "stock": 60, "is_default": True},
            {"color_name": "Black Titanium", "color_code": "#2D2D2D", "storage": "256GB", "ram": "8GB", "sku": "PHN-IP16P-256-BT", "price": 31990000, "stock": 45},
            {"color_name": "Desert Titanium", "color_code": "#C4A882", "storage": "512GB", "ram": "8GB", "sku": "PHN-IP16P-512-DT", "price": 37990000, "stock": 25},
        ],
    },
    {
        "name": "iPhone 16",
        "slug": "iphone-16",
        "brand": "Apple",
        "sku": "PHN-IP16",
        "product_type": "phone",
        "featured": True,
        "category_slug": "apple-iphone",
        "description": "iPhone 16 với chip A18, màn hình 6.1 inch OLED, camera kép 48MP, nút Action và Camera Control.",
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a7352e5c1c1?w=800&q=80",
        "variants": [
            {"color_name": "Ultramarine", "color_code": "#4B7BE5", "storage": "128GB", "ram": "8GB", "sku": "PHN-IP16-128-UM", "price": 22990000, "stock": 80, "is_default": True},
            {"color_name": "Teal", "color_code": "#008080", "storage": "256GB", "ram": "8GB", "sku": "PHN-IP16-256-TL", "price": 25990000, "stock": 55},
            {"color_name": "Pink", "color_code": "#FFB6C1", "storage": "512GB", "ram": "8GB", "sku": "PHN-IP16-512-PK", "price": 30990000, "stock": 30},
        ],
    },
    {
        "name": "iPhone 16 Plus",
        "slug": "iphone-16-plus",
        "brand": "Apple",
        "sku": "PHN-IP16PL",
        "product_type": "phone",
        "featured": False,
        "category_slug": "apple-iphone",
        "description": "iPhone 16 Plus màn hình 6.7 inch OLED, chip A18, camera 48MP, pin dung lượng lớn.",
        "image_url": "https://images.unsplash.com/photo-1592759685321-1f9d4c0ea658?w=800&q=80",
        "variants": [
            {"color_name": "Ultramarine", "color_code": "#4B7BE5", "storage": "128GB", "ram": "8GB", "sku": "PHN-IP16PL-128-UM", "price": 25990000, "stock": 40, "is_default": True},
            {"color_name": "Teal", "color_code": "#008080", "storage": "256GB", "ram": "8GB", "sku": "PHN-IP16PL-256-TL", "price": 28990000, "stock": 25},
        ],
    },
    {
        "name": "iPhone 15",
        "slug": "iphone-15",
        "brand": "Apple",
        "sku": "PHN-IP15",
        "product_type": "phone",
        "featured": False,
        "category_slug": "apple-iphone",
        "description": "iPhone 15 với chip A16 Bionic, màn hình 6.1 inch OLED, camera 48MP, Dynamic Island.",
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a7352e5c1c1?w=800&q=80",
        "variants": [
            {"color_name": "Blue", "color_code": "#4169E1", "storage": "128GB", "ram": "6GB", "sku": "PHN-IP15-128-BL", "price": 17990000, "stock": 70, "is_default": True},
            {"color_name": "Pink", "color_code": "#FFC0CB", "storage": "256GB", "ram": "6GB", "sku": "PHN-IP15-256-PK", "price": 20990000, "stock": 45},
            {"color_name": "Green", "color_code": "#228B22", "storage": "128GB", "ram": "6GB", "sku": "PHN-IP15-128-GN", "price": 17990000, "stock": 30},
        ],
    },
    {
        "name": "iPhone SE 4",
        "slug": "iphone-se-4",
        "brand": "Apple",
        "sku": "PHN-IPSE4",
        "product_type": "phone",
        "featured": False,
        "category_slug": "apple-iphone",
        "description": "iPhone SE 4 với chip A18, màn hình OLED 6.1 inch, Face ID, camera 48MB, giá phải chăng.",
        "image_url": "https://images.unsplash.com/photo-1592759685321-1f9d4c0ea658?w=800&q=80",
        "variants": [
            {"color_name": "Midnight", "color_code": "#1C1C1E", "storage": "128GB", "ram": "8GB", "sku": "PHN-IPSE4-128-MD", "price": 13990000, "stock": 100, "is_default": True},
            {"color_name": "Starlight", "color_code": "#F0E6D3", "storage": "256GB", "ram": "8GB", "sku": "PHN-IPSE4-256-ST", "price": 15990000, "stock": 65},
        ],
    },
    # -- Phones: Samsung Galaxy --
    {
        "name": "Samsung Galaxy S25 Ultra",
        "slug": "samsung-galaxy-s25-ultra",
        "brand": "Samsung",
        "sku": "PHN-S25U",
        "product_type": "phone",
        "featured": True,
        "category_slug": "samsung-galaxy",
        "description": "Galaxy S25 Ultra với Snapdragon 8 Elite, màn hình Dynamic AMOLED 6.9 inch, camera 200MP, bút S-Pen tích hợp.",
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80",
        "variants": [
            {"color_name": "Titanium Gray", "color_code": "#808080", "storage": "256GB", "ram": "12GB", "sku": "PHN-S25U-256-TG", "price": 32990000, "stock": 45, "is_default": True},
            {"color_name": "Titanium Silver", "color_code": "#C0C0C0", "storage": "512GB", "ram": "12GB", "sku": "PHN-S25U-512-TS", "price": 35990000, "stock": 30},
            {"color_name": "Titanium Black", "color_code": "#1A1A1A", "storage": "1TB", "ram": "12GB", "sku": "PHN-S25U-1TB-TB", "price": 41990000, "stock": 15},
        ],
    },
    {
        "name": "Samsung Galaxy S25+",
        "slug": "samsung-galaxy-s25-plus",
        "brand": "Samsung",
        "sku": "PHN-S25P",
        "product_type": "phone",
        "featured": False,
        "category_slug": "samsung-galaxy",
        "description": "Galaxy S25+ với Snapdragon 8 Elite, màn hình 6.7 inch QHD+, camera 50MB.",
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80",
        "variants": [
            {"color_name": "Silver", "color_code": "#E8E8E8", "storage": "256GB", "ram": "12GB", "sku": "PHN-S25P-256-SV", "price": 24990000, "stock": 55, "is_default": True},
            {"color_name": "Navy", "color_code": "#000080", "storage": "512GB", "ram": "12GB", "sku": "PHN-S25P-512-NV", "price": 27990000, "stock": 35},
        ],
    },
    {
        "name": "Samsung Galaxy S25",
        "slug": "samsung-galaxy-s25",
        "brand": "Samsung",
        "sku": "PHN-S25",
        "product_type": "phone",
        "featured": True,
        "category_slug": "samsung-galaxy",
        "description": "Galaxy S25 với Snapdragon 8 Elite, màn hình 6.2 inch FHD+ 120Hz, camera 50MB.",
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80",
        "variants": [
            {"color_name": "Silver", "color_code": "#E8E8E8", "storage": "128GB", "ram": "8GB", "sku": "PHN-S25-128-SV", "price": 19990000, "stock": 80, "is_default": True},
            {"color_name": "Navy", "color_code": "#000080", "storage": "256GB", "ram": "8GB", "sku": "PHN-S25-256-NV", "price": 22990000, "stock": 50},
            {"color_name": "Mint", "color_code": "#98FF98", "storage": "256GB", "ram": "8GB", "sku": "PHN-S25-256-MT", "price": 22990000, "stock": 40},
        ],
    },
    {
        "name": "Samsung Galaxy A56",
        "slug": "samsung-galaxy-a56",
        "brand": "Samsung",
        "sku": "PHN-A56",
        "product_type": "phone",
        "featured": False,
        "category_slug": "samsung-galaxy",
        "description": "Galaxy A56 với Exynos 1580, màn hình Super AMOLED 6.5 inch 120Hz, camera 50MP OIS.",
        "image_url": "https://images.unsplash.com/photo-1601782098483-7a1a1b1b1b1b?w=800&q=80",
        "variants": [
            {"color_name": "Awesome Pink", "color_code": "#FF69B4", "storage": "128GB", "ram": "8GB", "sku": "PHN-A56-128-AP", "price": 12490000, "stock": 90, "is_default": True},
            {"color_name": "Awesome Lilac", "color_code": "#C8A2C8", "storage": "256GB", "ram": "8GB", "sku": "PHN-A56-256-AL", "price": 14490000, "stock": 60},
        ],
    },
    {
        "name": "Samsung Galaxy Z Fold7",
        "slug": "samsung-galaxy-z-fold7",
        "brand": "Samsung",
        "sku": "PHN-ZF7",
        "product_type": "phone",
        "featured": True,
        "category_slug": "samsung-galaxy",
        "description": "Galaxy Z Fold7 với màn hình gập 7.6 inch Dynamic AMOLED, Snapdragon 8 Elite, camera 200MP.",
        "image_url": "https://images.unsplash.com/photo-1601782098483-7a1a1b1b1b1b?w=800&q=80",
        "variants": [
            {"color_name": "Silver", "color_code": "#C0C0C0", "storage": "256GB", "ram": "12GB", "sku": "PHN-ZF7-256-SV", "price": 43990000, "stock": 20, "is_default": True},
            {"color_name": "Black", "color_code": "#000000", "storage": "512GB", "ram": "12GB", "sku": "PHN-ZF7-512-BK", "price": 46990000, "stock": 15},
        ],
    },
    {
        "name": "Samsung Galaxy Z Flip7",
        "slug": "samsung-galaxy-z-flip7",
        "brand": "Samsung",
        "sku": "PHN-ZF7F",
        "product_type": "phone",
        "featured": False,
        "category_slug": "samsung-galaxy",
        "description": "Galaxy Z Flip7 với màn hình gập 6.7 inch Flex Window, chip Snapdragon 8 Elite.",
        "image_url": "https://images.unsplash.com/photo-1601782098483-7a1a1b1b1b1b?w=800&q=80",
        "variants": [
            {"color_name": "Blue", "color_code": "#4169E1", "storage": "256GB", "ram": "8GB", "sku": "PHN-ZF7F-256-BL", "price": 26990000, "stock": 30, "is_default": True},
            {"color_name": "Mint", "color_code": "#98FF98", "storage": "256GB", "ram": "8GB", "sku": "PHN-ZF7F-256-MT", "price": 26990000, "stock": 25},
            {"color_name": "Silver", "color_code": "#C0C0C0", "storage": "512GB", "ram": "8GB", "sku": "PHN-ZF7F-512-SV", "price": 29990000, "stock": 15},
        ],
    },
    # -- Phones: Xiaomi --
    {
        "name": "Xiaomi 15 Pro",
        "slug": "xiaomi-15-pro",
        "brand": "Xiaomi",
        "sku": "PHN-X15P",
        "product_type": "phone",
        "featured": True,
        "category_slug": "xiaomi",
        "description": "Xiaomi 15 Pro với Snapdragon 8 Elite, màn hình AMOLED 6.73 inch LTPO, camera Leica 50MP, pin 6100mAh.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "storage": "256GB", "ram": "12GB", "sku": "PHN-X15P-256-BK", "price": 22990000, "stock": 40, "is_default": True},
            {"color_name": "White", "color_code": "#F5F5F5", "storage": "512GB", "ram": "12GB", "sku": "PHN-X15P-512-WH", "price": 25990000, "stock": 25},
            {"color_name": "Green", "color_code": "#228B22", "storage": "512GB", "ram": "16GB", "sku": "PHN-X15P-512-GN", "price": 27990000, "stock": 15},
        ],
    },
    {
        "name": "Redmi Note 14 Pro+",
        "slug": "redmi-note-14-pro-plus",
        "brand": "Xiaomi",
        "sku": "PHN-RN14P",
        "product_type": "phone",
        "featured": False,
        "category_slug": "xiaomi",
        "description": "Redmi Note 14 Pro+ với MediaTek Dimensity 7350, màn hình AMOLED 6.67 inch 120Hz, camera 200MB.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "variants": [
            {"color_name": "Midnight Black", "color_code": "#1A1A1A", "storage": "256GB", "ram": "8GB", "sku": "PHN-RN14P-256-MB", "price": 9490000, "stock": 70, "is_default": True},
            {"color_name": "Aurora Purple", "color_code": "#9B59B6", "storage": "256GB", "ram": "12GB", "sku": "PHN-RN14P-256-AP", "price": 10490000, "stock": 45},
        ],
    },
    {
        "name": "POCO X7 Pro",
        "slug": "poco-x7-pro",
        "brand": "Xiaomi",
        "sku": "PHN-PX7P",
        "product_type": "phone",
        "featured": False,
        "category_slug": "xiaomi",
        "description": "POCO X7 Pro với MediaTek Dimensity 8400 Ultra, màn hình AMOLED 6.67 inch 120Hz, pin 6000mAh.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "variants": [
            {"color_name": "Yellow", "color_code": "#FFD700", "storage": "256GB", "ram": "8GB", "sku": "PHN-PX7P-256-YL", "price": 8990000, "stock": 85, "is_default": True},
            {"color_name": "Black", "color_code": "#000000", "storage": "256GB", "ram": "8GB", "sku": "PHN-PX7P-256-BK", "price": 8990000, "stock": 65},
            {"color_name": "Gray", "color_code": "#808080", "storage": "512GB", "ram": "12GB", "sku": "PHN-PX7P-512-GY", "price": 10990000, "stock": 40},
        ],
    },
    # -- Phones: OPPO --
    {
        "name": "OPPO Find X8 Pro",
        "slug": "oppo-find-x8-pro",
        "brand": "OPPO",
        "sku": "PHN-OFXP",
        "product_type": "phone",
        "featured": True,
        "category_slug": "oppo",
        "description": "OPPO Find X8 Pro với MediaTek Dimensity 9400, màn hình AMOLED 6.78 inch, camera Hasselblad 50MP.",
        "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "storage": "256GB", "ram": "12GB", "sku": "PHN-OFXP-256-BK", "price": 21990000, "stock": 35, "is_default": True},
            {"color_name": "White", "color_code": "#F8F8F8", "storage": "512GB", "ram": "16GB", "sku": "PHN-OFXP-512-WH", "price": 25990000, "stock": 20},
        ],
    },
    # -- Phones: Vivo --
    {
        "name": "Vivo X200 Pro",
        "slug": "vivo-x200-pro",
        "brand": "Vivo",
        "sku": "PHN-VX200",
        "product_type": "phone",
        "featured": False,
        "category_slug": "dien-thoai-vivo",
        "description": "Vivo X200 Pro với MediaTek Dimensity 9400, màn hình AMOLED 6.78 inch LTPO, camera ZEISS 50MP, pin 6000mAh.",
        "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&q=80",
        "variants": [
            {"color_name": "Blue", "color_code": "#1E90FF", "storage": "256GB", "ram": "12GB", "sku": "PHN-VX200-256-BL", "price": 19990000, "stock": 30, "is_default": True},
            {"color_name": "Gray", "color_code": "#696969", "storage": "512GB", "ram": "16GB", "sku": "PHN-VX200-512-GY", "price": 23990000, "stock": 20},
            {"color_name": "White", "color_code": "#F0F0F0", "storage": "256GB", "ram": "12GB", "sku": "PHN-VX200-256-WH", "price": 19990000, "stock": 25},
        ],
    },
    # -- Laptops: Apple MacBook --
    {
        "name": "MacBook Pro 16 M4 Max",
        "slug": "macbook-pro-16-m4-max",
        "brand": "Apple",
        "sku": "LAP-MBP16",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "apple-macbook",
        "description": "MacBook Pro 16 inch với chip M4 Max, màn hình Liquid Retina XDR, RAM 48GB, SSD 1TB, pin 22 giờ.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "48GB/1TB", "color_name": "Space Black", "color_code": "#2D2D2D", "storage": "1TB", "ram": "48GB", "sku": "LAP-MBP16-48-1TB-SB", "price": 74990000, "stock": 20, "is_default": True},
            {"version_name": "64GB/2TB", "color_name": "Silver", "color_code": "#E8E8E8", "storage": "2TB", "ram": "64GB", "sku": "LAP-MBP16-64-2TB-SV", "price": 89990000, "stock": 10},
        ],
    },
    {
        "name": "MacBook Pro 14 M4 Pro",
        "slug": "macbook-pro-14-m4-pro",
        "brand": "Apple",
        "sku": "LAP-MBP14",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "apple-macbook",
        "description": "MacBook Pro 14 inch với chip M4 Pro, màn hình Liquid Retina XDR, 3 cổng Thunderbolt 5.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "24GB/512GB", "color_name": "Space Black", "color_code": "#2D2D2D", "storage": "512GB", "ram": "24GB", "sku": "LAP-MBP14-24-512-SB", "price": 49990000, "stock": 30, "is_default": True},
            {"version_name": "24GB/1TB", "color_name": "Silver", "color_code": "#E8E8E8", "storage": "1TB", "ram": "24GB", "sku": "LAP-MBP14-24-1TB-SV", "price": 54990000, "stock": 25},
            {"version_name": "48GB/1TB", "color_name": "Space Black", "color_code": "#2D2D2D", "storage": "1TB", "ram": "48GB", "sku": "LAP-MBP14-48-1TB-SB", "price": 64990000, "stock": 15},
        ],
    },
    {
        "name": "MacBook Air 15 M4",
        "slug": "macbook-air-15-m4",
        "brand": "Apple",
        "sku": "LAP-MBA15",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "apple-macbook",
        "description": "MacBook Air 15 inch với chip M4, màn hình Liquid Retina, siêu mỏng nhẹ, pin 18 giờ.",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
        "variants": [
            {"version_name": "16GB/256GB", "color_name": "Midnight", "color_code": "#1C1C1E", "storage": "256GB", "ram": "16GB", "sku": "LAP-MBA15-16-256-MD", "price": 32990000, "stock": 50, "is_default": True},
            {"version_name": "24GB/512GB", "color_name": "Starlight", "color_code": "#F0E6D3", "storage": "512GB", "ram": "24GB", "sku": "LAP-MBA15-24-512-ST", "price": 37990000, "stock": 35},
            {"version_name": "16GB/512GB", "color_name": "Silver", "color_code": "#E8E8E8", "storage": "512GB", "ram": "16GB", "sku": "LAP-MBA15-16-512-SV", "price": 34990000, "stock": 40},
        ],
    },
    # -- Laptops: ASUS --
    {
        "name": "ASUS ROG Zephyrus G16",
        "slug": "asus-rog-zephyrus-g16",
        "brand": "ASUS",
        "sku": "LAP-ROGG16",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "asus",
        "description": "ROG Zephyrus G16 với Intel Core Ultra 9, RTX 4070, màn hình OLED 2.5K 240Hz, RAM 32GB.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "32GB/1TB", "color_name": "Eclipse Gray", "color_code": "#4A4A4A", "storage": "1TB", "ram": "32GB", "sku": "LAP-ROGG16-32-1TB-EG", "price": 45990000, "stock": 25, "is_default": True},
            {"version_name": "32GB/2TB", "color_name": "White", "color_code": "#F0F0F0", "storage": "2TB", "ram": "32GB", "sku": "LAP-ROGG16-32-2TB-WH", "price": 49990000, "stock": 15},
        ],
    },
    # -- Laptops: Dell --
    {
        "name": "Dell XPS 16",
        "slug": "dell-xps-16",
        "brand": "Dell",
        "sku": "LAP-XPS16",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "dell",
        "description": "Dell XPS 16 với Intel Core Ultra 9, màn hình OLED 4K觸, RAM 32GB, SSD 1TB, thiết kế sang trọng.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "32GB/1TB", "color_name": "Platinum", "color_code": "#E5E4E2", "storage": "1TB", "ram": "32GB", "sku": "LAP-XPS16-32-1TB-PL", "price": 42990000, "stock": 20, "is_default": True},
            {"version_name": "64GB/2TB", "color_name": "Graphite", "color_code": "#414141", "storage": "2TB", "ram": "64GB", "sku": "LAP-XPS16-64-2TB-GR", "price": 52990000, "stock": 10},
        ],
    },
    # -- Laptops: Lenovo --
    {
        "name": "Lenovo Legion Pro 7i",
        "slug": "lenovo-legion-pro-7i",
        "brand": "Lenovo",
        "sku": "LAP-LEG7",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "laptop-lenovo",
        "description": "Legion Pro 7i với Intel Core i9-14900HX, RTX 4080, màn hình 16 inch IPS 240Hz, RAM 32GB DDR5.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "32GB/1TB", "color_name": "Black", "color_code": "#1A1A1A", "storage": "1TB", "ram": "32GB", "sku": "LAP-LEG7-32-1TB-BK", "price": 55990000, "stock": 15, "is_default": True},
            {"version_name": "64GB/2TB", "color_name": "Black", "color_code": "#1A1A1A", "storage": "2TB", "ram": "64GB", "sku": "LAP-LEG7-64-2TB-BK", "price": 65990000, "stock": 8},
        ],
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon Gen 13",
        "slug": "lenovo-thinkpad-x1-carbon-gen-13",
        "brand": "Lenovo",
        "sku": "LAP-TPX1C",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "laptop-lenovo",
        "description": "ThinkPad X1 Carbon với Intel Core Ultra 7, màn hình 14 inch OLED 2.8K, RAM 32GB, siêu nhẹ 1.08kg.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "16GB/512GB", "color_name": "Black", "color_code": "#1C1C1E", "storage": "512GB", "ram": "16GB", "sku": "LAP-TPX1C-16-512-BK", "price": 38990000, "stock": 25, "is_default": True},
            {"version_name": "32GB/1TB", "color_name": "Black", "color_code": "#1C1C1E", "storage": "1TB", "ram": "32GB", "sku": "LAP-TPX1C-32-1TB-BK", "price": 45990000, "stock": 15},
        ],
    },
    # -- Audio --
    {
        "name": "Sony WH-1000XM6",
        "slug": "sony-wh-1000xm6",
        "brand": "Sony",
        "sku": "AUD-WHXM6",
        "product_type": "audio",
        "featured": True,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe chống ồn chủ động hàng đầu với công nghệ ANC Adaptive, cảm biến âm thanh mới, pin 40 giờ.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "AUD-WHXM6-BK", "price": 8990000, "stock": 60, "is_default": True},
            {"color_name": "Silver", "color_code": "#C0C0C0", "sku": "AUD-WHXM6-SV", "price": 8990000, "stock": 40},
            {"color_name": "Midnight Blue", "color_code": "#191970", "sku": "AUD-WHXM6-MB", "price": 9490000, "stock": 25},
        ],
    },
    {
        "name": "Apple AirPods Pro 3",
        "slug": "apple-airpods-pro-3",
        "brand": "Apple",
        "sku": "AUD-APP3",
        "product_type": "audio",
        "featured": True,
        "category_slug": "tai-nghe-bluetooth",
        "description": "AirPods Pro 3 với chip H3, chống ồn chủ động 2x, âm thanh thích ứng, pin 8 giờ mỗi lần sạc.",
        "image_url": "https://images.unsplash.com/photo-1606841837239-c5a1a4245b91?w=800&q=80",
        "variants": [
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "AUD-APP3-WH", "price": 8490000, "stock": 100, "is_default": True},
            {"color_name": "USB-C MagSafe", "color_code": "#FFFFFF", "sku": "AUD-APP3-WH-MG", "price": 8990000, "stock": 80},
        ],
    },
    {
        "name": "Apple AirPods Max 2",
        "slug": "apple-airpods-max-2",
        "brand": "Apple",
        "sku": "AUD-APM2",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "AirPods Max 2 với chip H3, chống ồn chủ động, âm thanh không gian spatial, vỏ nhôm cao cấp.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Midnight", "color_code": "#1C1C1E", "sku": "AUD-APM2-MD", "price": 13990000, "stock": 30, "is_default": True},
            {"color_name": "Starlight", "color_code": "#F0E6D3", "sku": "AUD-APM2-ST", "price": 13990000, "stock": 25},
            {"color_name": "Blue", "color_code": "#4169E1", "sku": "AUD-APM2-BL", "price": 13990000, "stock": 20},
            {"color_name": "Purple", "color_code": "#800080", "sku": "AUD-APM2-PU", "price": 13990000, "stock": 15},
        ],
    },
    {
        "name": "Samsung Galaxy Buds3 Pro",
        "slug": "samsung-galaxy-buds3-pro",
        "brand": "Samsung",
        "sku": "AUD-GB3P",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Galaxy Buds3 Pro với âm thanh Hi-Fi, chống ồn thích ứng 2 chiều, thiết kế đeo thoải mái.",
        "image_url": "https://images.unsplash.com/photo-1606841837239-c5a1a4245b91?w=800&q=80",
        "variants": [
            {"color_name": "Silver", "color_code": "#C0C0C0", "sku": "AUD-GB3P-SV", "price": 5990000, "stock": 55, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "AUD-GB3P-WH", "price": 5990000, "stock": 45},
        ],
    },
    {
        "name": "Bose QuietComfort Ultra",
        "slug": "bose-quietcomfort-ultra",
        "brand": "Bose",
        "sku": "AUD-BQCU",
        "product_type": "audio",
        "featured": True,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe Bose QuietComfort Ultra với công nghệ chống ồn hàng đầu, âm thanh Immersive, pin 32 giờ.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "AUD-BQCU-BK", "price": 10990000, "stock": 35, "is_default": True},
            {"color_name": "White Smoke", "color_code": "#F5F5F5", "sku": "AUD-BQCU-WS", "price": 10990000, "stock": 30},
            {"color_name": "Midnight Blue", "color_code": "#191970", "sku": "AUD-BQCU-MB", "price": 11490000, "stock": 20},
        ],
    },
    {
        "name": "Sennheiser Momentum 4",
        "slug": "sennheiser-momentum-4",
        "brand": "Sennheiser",
        "sku": "AUD-SM4",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe Sennheiser Momentum 4 với âm thanh audiophile, chống ồn thích ứng, pin 60 giờ.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "AUD-SM4-BK", "price": 9990000, "stock": 25, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "AUD-SM4-WH", "price": 9990000, "stock": 20},
        ],
    },
    {
        "name": "Nothing Ear",
        "slug": "nothing-ear",
        "brand": "Nothing",
        "sku": "AUD-NE",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe Nothing Ear với thiết kế trong suốt đặc trưng, chống ồn thích ứng, âm thanh Hi-Res.",
        "image_url": "https://images.unsplash.com/photo-1606841837239-c5a1a4245b91?w=800&q=80",
        "variants": [
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "AUD-NE-WH", "price": 4990000, "stock": 50, "is_default": True},
            {"color_name": "Yellow", "color_code": "#FFD700", "sku": "AUD-NE-YL", "price": 4990000, "stock": 35},
        ],
    },
    {
        "name": "JBL Tune 770NC",
        "slug": "jbl-tune-770nc",
        "brand": "JBL",
        "sku": "AUD-JBL770",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe JBL Tune 770NC với chống ồn chủ động, âm thanh Pure Bass, pin 70 giờ.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "AUD-JBL770-BK", "price": 3490000, "stock": 90, "is_default": True},
            {"color_name": "Blue", "color_code": "#4169E1", "sku": "AUD-JBL770-BL", "price": 3490000, "stock": 50},
            {"color_name": "Rose", "color_code": "#FF007F", "sku": "AUD-JBL770-RO", "price": 3490000, "stock": 40},
        ],
    },
    # -- Watches: Apple --
    {
        "name": "Apple Watch Ultra 3",
        "slug": "apple-watch-ultra-3",
        "brand": "Apple",
        "sku": "WCH-AWU3",
        "product_type": "watch",
        "featured": True,
        "category_slug": "apple-watch",
        "description": "Apple Watch Ultra 3 với vỏ titanium 49mm, màn hình OLED 3000 nits, pin 36 giờ, GPS chính xác.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"version_name": "49mm Titanium", "color_name": "Natural Titanium", "color_code": "#8B8B8B", "sku": "WCH-AWU3-49-NT", "price": 26990000, "stock": 30, "is_default": True},
            {"version_name": "49mm Titanium", "color_name": "Black Titanium", "color_code": "#2D2D2D", "sku": "WCH-AWU3-49-BT", "price": 27990000, "stock": 20},
        ],
    },
    {
        "name": "Apple Watch Series 10",
        "slug": "apple-watch-series-10",
        "brand": "Apple",
        "sku": "WCH-AWS10",
        "product_type": "watch",
        "featured": True,
        "category_slug": "apple-watch",
        "description": "Apple Watch Series 10 với màn hình OLED lớn nhất, chip S10, phát hiện ngưng thở khi ngủ.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"version_name": "46mm", "color_name": "Jet Black", "color_code": "#0A0A0A", "sku": "WCH-AWS10-46-JB", "price": 14990000, "stock": 50, "is_default": True},
            {"version_name": "42mm", "color_name": "Silver", "color_code": "#E8E8E8", "sku": "WCH-AWS10-42-SV", "price": 12990000, "stock": 45},
            {"version_name": "46mm", "color_name": "Rose Gold", "color_code": "#B76E79", "sku": "WCH-AWS10-46-RG", "price": 15990000, "stock": 30},
        ],
    },
    {
        "name": "Apple Watch SE 3",
        "slug": "apple-watch-se-3",
        "brand": "Apple",
        "sku": "WCH-AWSE3",
        "product_type": "watch",
        "featured": False,
        "category_slug": "apple-watch",
        "description": "Apple Watch SE 3 với chip S10, cảm biến sức khỏe toàn diện, giá phải chăng.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"version_name": "44mm", "color_name": "Midnight", "color_code": "#1C1C1E", "sku": "WCH-AWSE3-44-MD", "price": 8990000, "stock": 80, "is_default": True},
            {"version_name": "40mm", "color_name": "Starlight", "color_code": "#F0E6D3", "sku": "WCH-AWSE3-40-ST", "price": 7990000, "stock": 70},
        ],
    },
    # -- Watches: Samsung --
    {
        "name": "Samsung Galaxy Watch 7",
        "slug": "samsung-galaxy-watch-7",
        "brand": "Samsung",
        "sku": "WCH-GW7",
        "product_type": "watch",
        "featured": False,
        "category_slug": "samsung-galaxy-watch",
        "description": "Galaxy Watch 7 với Exynos W1000, màn hình Super AMOLED, cảm biến BioActive 2, Wear OS.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"version_name": "44mm", "color_name": "Green", "color_code": "#228B22", "sku": "WCH-GW7-44-GN", "price": 9990000, "stock": 45, "is_default": True},
            {"version_name": "40mm", "color_name": "Cream", "color_code": "#FFFDD0", "sku": "WCH-GW7-40-CR", "price": 8990000, "stock": 40},
        ],
    },
    # -- Watches: Xiaomi --
    {
        "name": "Xiaomi Watch S4",
        "slug": "xiaomi-watch-s4",
        "brand": "Xiaomi",
        "sku": "WCH-XWS4",
        "product_type": "watch",
        "featured": False,
        "category_slug": "xiaomi-watch",
        "description": "Xiaomi Watch S4 với màn hình AMOLED 1.43 inch, theo dõi sức khỏe 24/7, pin 15 ngày.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "WCH-XWS4-BK", "price": 5990000, "stock": 60, "is_default": True},
            {"color_name": "Silver", "color_code": "#C0C0C0", "sku": "WCH-XWS4-SV", "price": 6490000, "stock": 40},
        ],
    },
    # -- Watches: Garmin --
    {
        "name": "Garmin Forerunner 265",
        "slug": "garmin-forerunner-265",
        "brand": "Garmin",
        "sku": "WCH-GF265",
        "product_type": "watch",
        "featured": False,
        "category_slug": "garmin",
        "description": "Garmin Forerunner 265 với màn hình AMOLED, GPS đa băng tần, chỉ số huấn luyện chuyên sâu.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"version_name": "46mm", "color_name": "Black", "color_code": "#000000", "sku": "WCH-GF265-46-BK", "price": 11990000, "stock": 30, "is_default": True},
            {"version_name": "42mm", "color_name": "White", "color_code": "#FFFFFF", "sku": "WCH-GF265-42-WH", "price": 10990000, "stock": 25},
        ],
    },
    {
        "name": "Garmin Fenix 8",
        "slug": "garmin-fenix-8",
        "brand": "Garmin",
        "sku": "WCH-GF8",
        "product_type": "watch",
        "featured": True,
        "category_slug": "garmin",
        "description": "Garmin Fenix 8 với vỏ titanium, màn hình AMOLED, bản đồ địa hình, đèn pin tích hợp, pin 29 ngày.",
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80",
        "variants": [
            {"version_name": "47mm", "color_name": "Black", "color_code": "#1A1A1A", "sku": "WCH-GF8-47-BK", "price": 29990000, "stock": 15, "is_default": True},
            {"version_name": "51mm", "color_name": "Titanium", "color_code": "#8B8B8B", "sku": "WCH-GF8-51-TI", "price": 35990000, "stock": 8},
        ],
    },
    # -- Accessories: Mice --
    {
        "name": "Logitech G Pro X Superlight 2",
        "slug": "logitech-g-pro-x-superlight-2",
        "brand": "Logitech",
        "sku": "ACC-GPX2",
        "product_type": "accessory",
        "featured": True,
        "category_slug": "chuot",
        "description": "Chuột gaming siêu nhẹ 60g với sensor HERO 2, Lightspeed wireless, 8 nút lập trình, pin 95 giờ.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0c29e5ef95?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "ACC-GPX2-BK", "price": 3490000, "stock": 80, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-GPX2-WH", "price": 3490000, "stock": 60},
            {"color_name": "Magenta", "color_code": "#FF00FF", "sku": "ACC-GPX2-MG", "price": 3690000, "stock": 30},
        ],
    },
    {
        "name": "Razer DeathAdder V3 Pro",
        "slug": "razer-deathadder-v3-pro",
        "brand": "Razer",
        "sku": "ACC-RDV3",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "chuot",
        "description": "Chuột gaming không dây với sensor Focus Pro 30K, siêu nhẹ 63g, pin 90 giờ.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0c29e5ef95?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "ACC-RDV3-BK", "price": 2990000, "stock": 65, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-RDV3-WH", "price": 2990000, "stock": 40},
        ],
    },
    # -- Accessories: Keyboards --
    {
        "name": "Razer BlackWidow V4 Pro",
        "slug": "razer-blackwidow-v4-pro",
        "brand": "Razer",
        "sku": "ACC-RBW4",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "ban-phim",
        "description": "Bàn phím gaming cơ với switch Razer Green, đèn RGB Chroma, vòng xoay đa năng, wrist rest.",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "ACC-RBW4-BK", "price": 5490000, "stock": 35, "is_default": True},
        ],
    },
    # -- Accessories: Cases --
    {
        "name": "Apple Silicone Case for iPhone 16 Pro Max",
        "slug": "apple-silicone-case-iphone-16-pro-max",
        "brand": "Apple",
        "sku": "ACC-ASC16",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "op-lung-bao-da",
        "description": "Ốp lưng silicone chính hãng Apple với MagSafe, cảm giác mềm mại, nhiều màu sắc.",
        "image_url": "https://images.unsplash.com/photo-1592759685321-1f9d4c0ea658?w=800&q=80",
        "variants": [
            {"color_name": "Atlantic Blue", "color_code": "#4169E1", "sku": "ACC-ASC16-AB", "price": 1490000, "stock": 100, "is_default": True},
            {"color_name": "Clay", "color_code": "#C4A882", "sku": "ACC-ASC16-CL", "price": 1490000, "stock": 80},
            {"color_name": "Stone Gray", "color_code": "#808080", "sku": "ACC-ASC16-SG", "price": 1490000, "stock": 65},
        ],
    },
    # -- Accessories: Chargers --
    {
        "name": "Anker PowerCore 26800mAh",
        "slug": "anker-powercore-26800mah",
        "brand": "Anker",
        "sku": "ACC-APC",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "Sạc dự phòng Anker PowerCore 26800mAh, 3 cổng USB, công nghệ PowerIQ, sạc nhanh.",
        "image_url": "https://images.unsplash.com/photo-1583394293214-28ded15ee548?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "ACC-APC-BK", "price": 1490000, "stock": 120, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-APC-WH", "price": 1490000, "stock": 90},
        ],
    },
    {
        "name": "UGREEN 100W GaN Charger",
        "slug": "ugreen-100w-gan-charger",
        "brand": "UGREEN",
        "sku": "ACC-UGAN",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "Sạc GaN 100W 4 cổng USB-C, tương thích MacBook Pro, iPhone, Samsung, sạc nhanh PD 3.0.",
        "image_url": "https://images.unsplash.com/photo-1583394293214-28ded15ee548?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1A1A1A", "sku": "ACC-UGAN-BK", "price": 990000, "stock": 150, "is_default": True},
            {"color_name": "White", "color_code": "#F5F5F5", "sku": "ACC-UGAN-WH", "price": 990000, "stock": 100},
        ],
    },
    # -- Accessories: Gaming Headsets --
    {
        "name": "HyperX Cloud III",
        "slug": "hyperx-cloud-iii",
        "brand": "HyperX",
        "sku": "ACC-HX3",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "phu-kien-gaming",
        "description": "Tai nghe gaming HyperX Cloud III với driver 53mm, đệm mút hoạt tính, khung nhôm, chống ồn.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#000000", "sku": "ACC-HX3-BK", "price": 2490000, "stock": 70, "is_default": True},
            {"color_name": "Red", "color_code": "#FF0000", "sku": "ACC-HX3-RD", "price": 2490000, "stock": 40},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-HX3-WH", "price": 2590000, "stock": 30},
        ],
    },
    {
        "name": "SteelSeries Arctis Nova Pro",
        "slug": "steelseries-arctis-nova-pro",
        "brand": "SteelSeries",
        "sku": "ACC-SANP",
        "product_type": "accessory",
        "featured": True,
        "category_slug": "phu-kien-gaming",
        "description": "Tai nghe gaming SteelSeries Arctis Nova Pro với âm thanh Hi-Res, ANC, GameDAC thế hệ 2.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1A1A1A", "sku": "ACC-SANP-BK", "price": 7490000, "stock": 25, "is_default": True},
            {"color_name": "White", "color_code": "#F0F0F0", "sku": "ACC-SANP-WH", "price": 7490000, "stock": 15},
        ],
    },
    # -- Laptops: Additional ASUS --
    {
        "name": "ASUS ROG Strix G18",
        "slug": "asus-rog-strix-g18",
        "brand": "ASUS",
        "sku": "LAP-ROGSG18",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "asus",
        "description": "Gaming laptop Intel Core i9-14900HX, RTX 4080, 18-inch 2.5K 240Hz, 32GB DDR5, 1TB SSD.",
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
        "variants": [
            {"version_name": "i9 / RTX 4080", "ram": "32GB", "storage": "1TB", "sku": "LAP-ROGSG18-I94", "price": 49990000, "stock": 8, "is_default": True},
            {"version_name": "i9 / RTX 4090", "ram": "64GB", "storage": "2TB", "sku": "LAP-ROGSG18-I99", "price": 65990000, "stock": 3},
        ],
    },
    {
        "name": "ASUS TUF Gaming A16",
        "slug": "asus-tuf-gaming-a16",
        "brand": "ASUS",
        "sku": "LAP-TUFA16",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "asus",
        "description": "Gaming laptop AMD Ryzen 7 8845HS, RX 7700S, 16-inch 165Hz, 16GB DDR5, 512GB SSD, military-grade durable.",
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
        "variants": [
            {"version_name": "R7 / RX 7700S", "ram": "16GB", "storage": "512GB", "sku": "LAP-TUFA16-R7", "price": 22990000, "stock": 22, "is_default": True},
            {"version_name": "R7 / RX 7700S", "ram": "32GB", "storage": "1TB", "sku": "LAP-TUFA16-R732", "price": 26990000, "stock": 12},
        ],
    },
    {
        "name": "ASUS ZenBook 14 OLED",
        "slug": "asus-zenbook-14-oled",
        "brand": "ASUS",
        "sku": "LAP-ZB14",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "asus",
        "description": "Ultrabook Intel Core Ultra 7 258V, 14-inch 3K OLED 120Hz, 16GB RAM, 512GB SSD, 65W USB-C.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 7 / 16GB", "ram": "16GB", "storage": "512GB", "sku": "LAP-ZB14-U7", "price": 24990000, "stock": 18, "is_default": True},
            {"version_name": "Ultra 7 / 32GB", "ram": "32GB", "storage": "1TB", "sku": "LAP-ZB14-U732", "price": 29990000, "stock": 10},
        ],
    },
    {
        "name": "ASUS Vivobook 16",
        "slug": "asus-vivobook-16",
        "brand": "ASUS",
        "sku": "LAP-VB16",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "asus",
        "description": "Laptop van ngay AMD Ryzen 5 7530U, 16-inch FHD IPS, 8GB RAM, 512GB SSD, pin 42Wh.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "R5 / 8GB", "ram": "8GB", "storage": "512GB", "sku": "LAP-VB16-R5", "price": 11990000, "stock": 35, "is_default": True},
            {"version_name": "R7 / 16GB", "ram": "16GB", "storage": "1TB", "sku": "LAP-VB16-R7", "price": 15990000, "stock": 20},
        ],
    },
    # -- Laptops: Additional Dell --
    {
        "name": "Dell XPS 14",
        "slug": "dell-xps-14",
        "brand": "Dell",
        "sku": "LAP-DXPS14",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "dell",
        "description": "Premium laptop Intel Core Ultra 7 258V, 14.5-inch 3.2K OLED, RTX 4050, 16GB LPDDR5X.",
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 7 / RTX 4050", "ram": "16GB", "storage": "512GB", "sku": "LAP-DXPS14-U7", "price": 32990000, "stock": 14, "is_default": True},
            {"version_name": "Ultra 7 / RTX 4050", "ram": "32GB", "storage": "1TB", "sku": "LAP-DXPS14-U732", "price": 37990000, "stock": 8},
        ],
    },
    {
        "name": "Dell Inspiron 16 Plus",
        "slug": "dell-inspiron-16-plus",
        "brand": "Dell",
        "sku": "LAP-DIN16P",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "dell",
        "description": "Laptop content creator Intel Core i7-13700H, 16-inch 2.5K IPS, RTX 3050, 16GB DDR5.",
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
        "variants": [
            {"version_name": "i7 / RTX 3050", "ram": "16GB", "storage": "512GB", "sku": "LAP-DIN16P-I7", "price": 19990000, "stock": 20, "is_default": True},
            {"version_name": "i7 / RTX 3050", "ram": "32GB", "storage": "1TB", "sku": "LAP-DIN16P-I732", "price": 23990000, "stock": 12},
        ],
    },
    {
        "name": "Dell Latitude 5550",
        "slug": "dell-latitude-5550",
        "brand": "Dell",
        "sku": "LAP-DLT5550",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "dell",
        "description": "Laptop doanh nhan Intel Core Ultra 5 226V, 15.6-inch FHD, 16GB RAM, 512GB SSD, bao mat enterprise.",
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 5 / 16GB", "ram": "16GB", "storage": "512GB", "sku": "LAP-DLT5550-U5", "price": 18990000, "stock": 16, "is_default": True},
            {"version_name": "Ultra 7 / 32GB", "ram": "32GB", "storage": "1TB", "sku": "LAP-DLT5550-U7", "price": 24990000, "stock": 8},
        ],
    },
    # -- Laptops: Additional Lenovo --
    {
        "name": "Lenovo IdeaPad Slim 5",
        "slug": "lenovo-ideapad-slim-5",
        "brand": "Lenovo",
        "sku": "LAP-IPS5",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "laptop-lenovo",
        "description": "Laptop pho thong AMD Ryzen 7 8845HS, 16-inch 2.5K IPS, 16GB RAM, 512GB SSD.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "R7 / 16GB", "ram": "16GB", "storage": "512GB", "sku": "LAP-IPS5-R7", "price": 14990000, "stock": 30, "is_default": True},
            {"version_name": "R7 / 32GB", "ram": "32GB", "storage": "1TB", "sku": "LAP-IPS5-R732", "price": 18990000, "stock": 15},
        ],
    },
    {
        "name": "Lenovo Yoga 9i",
        "slug": "lenovo-yoga-9i",
        "brand": "Lenovo",
        "sku": "LAP-YG9I",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "laptop-lenovo",
        "description": "Laptop 2-trong-1 Intel Core Ultra 7 258V, 14-inch 4K OLED touch, 16GB RAM, 1TB SSD, soundbar ban le.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 7 / 16GB", "ram": "16GB", "storage": "1TB", "sku": "LAP-YG9I-U7", "price": 29990000, "stock": 12, "is_default": True},
            {"version_name": "Ultra 7 / 32GB", "ram": "32GB", "storage": "1TB", "sku": "LAP-YG9I-U732", "price": 33990000, "stock": 6},
        ],
    },
    # -- Laptops: Additional HP --
    {
        "name": "HP Spectre x360 16",
        "slug": "hp-spectre-x360-16",
        "brand": "HP",
        "sku": "LAP-HPSPX360",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "hp",
        "description": "Laptop 2-trong-1 cao cap Intel Core Ultra 9 285H, 16-inch 3K OLED touch, RTX 4050, ban le 360 do.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 9 / RTX 4050", "ram": "32GB", "storage": "1TB", "sku": "LAP-HPSPX360-U9", "price": 38990000, "stock": 8, "is_default": True},
            {"version_name": "Ultra 7 / Arc", "ram": "16GB", "storage": "512GB", "sku": "LAP-HPSPX360-U7", "price": 28990000, "stock": 14},
        ],
    },
    {
        "name": "HP Pavilion 15",
        "slug": "hp-pavilion-15",
        "brand": "HP",
        "sku": "LAP-HPPV15",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "hp",
        "description": "Laptop gia dinh Intel Core i5-14450HX, 15.6-inch FHD IPS, 16GB DDR5, 512GB SSD.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "i5 / 16GB", "ram": "16GB", "storage": "512GB", "sku": "LAP-HPPV15-I5", "price": 13990000, "stock": 30, "is_default": True},
            {"version_name": "i7 / 16GB", "ram": "16GB", "storage": "1TB", "sku": "LAP-HPPV15-I7", "price": 17990000, "stock": 18},
        ],
    },
    # -- Laptops: Additional brands --
    {
        "name": "Acer Swift Go 14",
        "slug": "acer-swift-go-14",
        "brand": "Acer",
        "sku": "LAP-ASG14",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "acer",
        "description": "Ultrabook Intel Core Ultra 7 258V, 14-inch 2.8K OLED, 16GB RAM, 512GB SSD, AI experience.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 7 / 16GB", "ram": "16GB", "storage": "512GB", "sku": "LAP-ASG14-U7", "price": 19990000, "stock": 22, "is_default": True},
            {"version_name": "Ultra 7 / 32GB", "ram": "32GB", "storage": "1TB", "sku": "LAP-ASG14-U732", "price": 24990000, "stock": 10},
        ],
    },
    {
        "name": "LG Gram 16",
        "slug": "lg-gram-16",
        "brand": "LG",
        "sku": "LAP-LGGR16",
        "product_type": "laptop",
        "featured": False,
        "category_slug": "lg",
        "description": "Laptop sieu nhe 1.19kg Intel Core Ultra 7 258V, 16-inch WQXGA IPS, 80Wh pin, chuan MIL-STD-810H.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"version_name": "Ultra 7 / 16GB", "ram": "16GB", "storage": "512GB", "sku": "LAP-LGGR16-U7", "price": 27990000, "stock": 12, "is_default": True},
            {"version_name": "Ultra 7 / 32GB", "ram": "32GB", "storage": "1TB", "sku": "LAP-LGGR16-U732", "price": 32990000, "stock": 6},
        ],
    },
    {
        "name": "Microsoft Surface Laptop 7",
        "slug": "microsoft-surface-laptop-7",
        "brand": "Microsoft",
        "sku": "LAP-MSL7",
        "product_type": "laptop",
        "featured": True,
        "category_slug": "microsoft-surface",
        "description": "Copilot+ PC Snapdragon X Elite, 15-inch PixelSense Flow 120Hz touch, 16GB RAM, 512GB SSD, pin ca ngay.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "variants": [
            {"color_name": "Platinum", "color_code": "#E8E4DF", "ram": "16GB", "storage": "512GB", "sku": "LAP-MSL7-PL", "price": 28990000, "stock": 14, "is_default": True},
            {"color_name": "Black", "color_code": "#1C1C1E", "ram": "16GB", "storage": "512GB", "sku": "LAP-MSL7-BK", "price": 28990000, "stock": 10},
        ],
    },
    # -- Audio: Additional Bluetooth --
    {
        "name": "Sony WF-1000XM6",
        "slug": "sony-wf-1000xm6",
        "brand": "Sony",
        "sku": "AUD-WF1000XM6",
        "product_type": "audio",
        "featured": True,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe true wireless cao cap voi Integrated Processor V2, Hires Audio, chong on thich ung 24h pin.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-WF1000XM6-BK", "price": 6490000, "stock": 35, "is_default": True},
            {"color_name": "Platinum Silver", "color_code": "#D1D1D6", "sku": "AUD-WF1000XM6-SV", "price": 6490000, "stock": 22},
        ],
    },
    {
        "name": "Bose Ultra Open Earbuds",
        "slug": "bose-ultra-open-earbuds",
        "brand": "Bose",
        "sku": "AUD-BUOE",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe mo Bose Immersive Audio, 7.5h pin, thiet ke deo thoai mai, am thanh khong gian.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-BUOE-BK", "price": 8490000, "stock": 22, "is_default": True},
            {"color_name": "White Smoke", "color_code": "#E8E4DF", "sku": "AUD-BUOE-WS", "price": 8490000, "stock": 15},
        ],
    },
    {
        "name": "Xiaomi Buds 5 Pro",
        "slug": "xiaomi-buds-5-pro",
        "brand": "Xiaomi",
        "sku": "AUD-XB5P",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe TWS cao cap Snapdragon Sound aptX Lossless, ANC 52dB, pin 40h, sac khong day 10W.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Titanium Black", "color_code": "#2C2C2E", "sku": "AUD-XB5P-BK", "price": 3990000, "stock": 30, "is_default": True},
            {"color_name": "Ceramic White", "color_code": "#F5F5F0", "sku": "AUD-XB5P-WH", "price": 3990000, "stock": 22},
        ],
    },
    {
        "name": "Beats Studio Pro",
        "slug": "beats-studio-pro",
        "brand": "Beats",
        "sku": "AUD-BSP",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe over-ear voi chip Apple H1, USB-C lossless, ANC, Personalized Spatial Audio, 40h pin.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-BSP-BK", "price": 7990000, "stock": 18, "is_default": True},
            {"color_name": "Sandstone", "color_code": "#D4C4B0", "sku": "AUD-BSP-SS", "price": 7990000, "stock": 12},
        ],
    },
    {
        "name": "JBL Tune 770NC",
        "slug": "jbl-tune-770nc",
        "brand": "JBL",
        "sku": "AUD-T770NC",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe ANC gia re JBL Pure Bass, 70h pin, thiet ke nhe thoai mai, gap gon.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-T770NC-BK", "price": 2790000, "stock": 50, "is_default": True},
            {"color_name": "Blue", "color_code": "#4A7B9D", "sku": "AUD-T770NC-BL", "price": 2790000, "stock": 30},
        ],
    },
    {
        "name": "Marshall Major V",
        "slug": "marshall-major-v",
        "brand": "Marshall",
        "sku": "AUD-MAJ5",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe on-ear voi thiet ke iconic Marshall, 100h+ pin, Bluetooth 5.3, am thanh dynamic 40mm.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-MAJ5-BK", "price": 3290000, "stock": 28, "is_default": True},
            {"color_name": "Cream", "color_code": "#F5E6D3", "sku": "AUD-MAJ5-CR", "price": 3290000, "stock": 18},
        ],
    },
    {
        "name": "Soundcore Liberty 4 Pro",
        "slug": "soundcore-liberty-4-pro",
        "brand": "Anker",
        "sku": "AUD-LB4P",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe TWS voi ACAA 4.0 coaxial driver, Adaptive ANC 2.0, LDAC, 40h pin, sac khong day.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-LB4P-BK", "price": 3490000, "stock": 35, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "AUD-LB4P-WH", "price": 3490000, "stock": 25},
        ],
    },
    # -- Audio: Wired --
    {
        "name": "Sennheiser IE 600",
        "slug": "sennheiser-ie-600",
        "brand": "Sennheiser",
        "sku": "AUD-IE600",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-co-day",
        "description": "IEM audiophile vo zirconium, driver TrueResponse 7mm, cap MMCX, am thanh trung thuc cao.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Silver", "color_code": "#D1D1D6", "sku": "AUD-IE600-SV", "price": 12990000, "stock": 8, "is_default": True},
        ],
    },
    {
        "name": "Audio-Technica ATH-M50xBT2",
        "slug": "audio-technica-ath-m50xbt2",
        "brand": "Audio-Technica",
        "sku": "AUD-M50XBT2",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-co-day",
        "description": "Tai nghe studio chuyen nghiep 45mm driver, wireless Bluetooth 5.0, 50h pin, LDAC.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-M50XBT2-BK", "price": 4990000, "stock": 20, "is_default": True},
        ],
    },
    {
        "name": "Shure AONIC 50 Gen 2",
        "slug": "shure-aonic-50-gen-2",
        "brand": "Shure",
        "sku": "AUD-AON50G2",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-co-day",
        "description": "Tai nghe cao cap 50mm driver, Adjustable ANC, Bluetooth 5.0, 45h pin, am thanh studio.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-AON50G2-BK", "price": 8490000, "stock": 12, "is_default": True},
            {"color_name": "Brown", "color_code": "#8B6B4A", "sku": "AUD-AON50G2-BR", "price": 8490000, "stock": 8},
        ],
    },
    {
        "name": "Amazfit T-Rex 3",
        "slug": "amazfit-t-rex-3",
        "brand": "Amazfit",
        "sku": "WCH-ATR3",
        "product_type": "watch",
        "featured": False,
        "category_slug": "garmin",
        "description": "Dong ho GPS chong nuoc 200m, AMOLED 1.5-inch, 28 ngay pin, 150+ che do the thao, chuan quan su MIL-STD-810G.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Obsidian Black", "color_code": "#1C1C1E", "version_name": "48mm", "sku": "WCH-ATR3-BK48", "price": 6490000, "stock": 16, "is_default": True},
            {"color_name": "Sahara", "color_code": "#C4BBAF", "version_name": "48mm", "sku": "WCH-ATR3-SH48", "price": 6490000, "stock": 10},
        ],
    },
    {
        "name": "Fossil Gen 8",
        "slug": "fossil-gen-8",
        "brand": "Fossil",
        "sku": "WCH-FG8",
        "product_type": "watch",
        "featured": False,
        "category_slug": "xiaomi-watch",
        "description": "Smartwatch Wear OS 4, Snapdragon W5+ Gen 1, 1.28-inch AMOLED, NFC Google Pay, theo doi suc khoe 24/7.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "version_name": "44mm", "sku": "WCH-FG8-BK44", "price": 6990000, "stock": 14, "is_default": True},
            {"color_name": "Silver", "color_code": "#D1D1D6", "version_name": "44mm", "sku": "WCH-FG8-SV44", "price": 6990000, "stock": 10},
        ],
    },
    {
        "name": "Xiaomi Smart Band 9 Pro",
        "slug": "xiaomi-smart-band-9-pro",
        "brand": "Xiaomi",
        "sku": "WCH-XSB9P",
        "product_type": "watch",
        "featured": False,
        "category_slug": "xiaomi-watch",
        "description": "Vo tay thong minh 1.74-inch AMOLED 60Hz, GNSS, 21 ngay pin, theo doi suc khoe 24/7.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "WCH-XSB9P-BK", "price": 1690000, "stock": 50, "is_default": True},
            {"color_name": "Purple", "color_code": "#8B5E8D", "sku": "WCH-XSB9P-PU", "price": 1690000, "stock": 30},
        ],
    },
    # -- Watches: Garmin --
    {
        "name": "Garmin Venu 4",
        "slug": "garmin-venu-4",
        "brand": "Garmin",
        "sku": "WCH-GVN4",
        "product_type": "watch",
        "featured": False,
        "category_slug": "garmin",
        "description": "GPS smartwatch AMOLED, Body Battery, phat hien giac ngu, 14 ngay pin, theo doi the duc toan dien.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Slate", "color_code": "#5A5A5A", "version_name": "45mm", "sku": "WCH-GVN4-SL45", "price": 9490000, "stock": 14, "is_default": True},
            {"color_name": "Cream Gold", "color_code": "#E8D5A3", "version_name": "45mm", "sku": "WCH-GVN4-CG45", "price": 9490000, "stock": 10},
        ],
    },
    # -- Watches: Huawei --
    {
        "name": "Huawei Watch GT 5 Pro",
        "slug": "huawei-watch-gt-5-pro",
        "brand": "Huawei",
        "sku": "WCH-HWGT5P",
        "product_type": "watch",
        "featured": False,
        "category_slug": "huawei-watch",
        "description": "Dong ho thong minh 1.43-inch AMOLED, vo Titanium, ECG, 14 ngay pin, HarmonyOS.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Titanium", "color_code": "#D4CFC4", "version_name": "46mm", "sku": "WCH-HWGT5P-TI46", "price": 8990000, "stock": 15, "is_default": True},
            {"color_name": "Black", "color_code": "#1C1C1E", "version_name": "46mm", "sku": "WCH-HWGT5P-BK46", "price": 8990000, "stock": 18},
        ],
    },
    {
        "name": "Huawei Band 10",
        "slug": "huawei-band-10",
        "brand": "Huawei",
        "sku": "WCH-HWB10",
        "product_type": "watch",
        "featured": False,
        "category_slug": "huawei-watch",
        "description": "Vo tay thong minh 1.47-inch AMOLED, TruSeen 5.5, SpO2, 14 ngay pin, nhe 16g.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "WCH-HWB10-BK", "price": 990000, "stock": 60, "is_default": True},
            {"color_name": "Pink", "color_code": "#F5C6D0", "sku": "WCH-HWB10-PK", "price": 990000, "stock": 40},
        ],
    },
    # -- Accessories: Additional Mouse --
    {
        "name": "Logitech MX Master 3S",
        "slug": "logitech-mx-master-3s",
        "brand": "Logitech",
        "sku": "ACC-MXM3S",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "chuot",
        "description": "Chuot van phong 8K DPI, MagSpeed scroll, click im lang, USB-C, pin 70 ngay, Quiet Clicks.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "Graphite", "color_code": "#4A4A4A", "sku": "ACC-MXM3S-GR", "price": 2290000, "stock": 30, "is_default": True},
            {"color_name": "Pale Gray", "color_code": "#D1D1D6", "sku": "ACC-MXM3S-PG", "price": 2290000, "stock": 20},
        ],
    },
    # -- Accessories: Additional Keyboard --
    {
        "name": "Corsair K70 RGB Pro",
        "slug": "corsair-k70-rgb-pro",
        "brand": "Corsair",
        "sku": "ACC-K70P",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "ban-phim",
        "description": "Ban phim co Cherry MX Speed, khung nhom, RGB, 8K polling, N-key rollover, phim media chuyen dung.",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d3b0d3b1?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-K70P-BK", "price": 3990000, "stock": 22, "is_default": True},
        ],
    },
    {
        "name": "Logitech MX Mechanical",
        "slug": "logitech-mx-mechanical",
        "brand": "Logitech",
        "sku": "ACC-MXMECH",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "ban-phim",
        "description": "Ban phim co khong day Tactile Quiet, Smart Illumination, ket noi 3 thiet bi, USB-C.",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d3b0d3b1?w=800&q=80",
        "variants": [
            {"color_name": "Graphite", "color_code": "#4A4A4A", "version_name": "Full-size", "sku": "ACC-MXMECH-GR", "price": 3990000, "stock": 20, "is_default": True},
            {"color_name": "Pale Gray", "color_code": "#D1D1D6", "version_name": "Full-size", "sku": "ACC-MXMECH-PG", "price": 3990000, "stock": 12},
        ],
    },
    # -- Accessories: Additional Cases --
    {
        "name": "Spigen Ultra Hybrid MagSafe Galaxy S25 Ultra",
        "slug": "spigen-ultra-hybrid-s25-ultra",
        "brand": "Spigen",
        "sku": "ACC-SPIGEN-S25U",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "op-lung-bao-da",
        "description": "Op lung trong suot Air Cushion, MagSafe ring, chuan MIL-STD-810G, chong va dap quan su.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "Crystal Clear", "color_code": "rgba(255,255,255,0.35)", "sku": "ACC-SPIGEN-S25U-CC", "price": 390000, "stock": 80, "is_default": True},
            {"color_name": "Matte Black", "color_code": "#2C2C2E", "sku": "ACC-SPIGEN-S25U-MB", "price": 390000, "stock": 60},
        ],
    },
    # -- Accessories: Additional Chargers --
    {
        "name": "Apple 70W USB-C Power Adapter",
        "slug": "apple-70w-usb-c-adapter",
        "brand": "Apple",
        "sku": "ACC-APL70W",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "Sac USB-C 70W GaN cho MacBook Pro/Air, iPad Pro, iPhone 16, sac nhanh USB-C PD.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-APL70W-WH", "price": 1690000, "stock": 45, "is_default": True},
        ],
    },
    # -- Accessories: Additional Gaming Headsets --
    {
        "name": "Razer Kraken V4 Pro",
        "slug": "razer-kraken-v4-pro",
        "brand": "Razer",
        "sku": "ACC-KV4P",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "phu-kien-gaming",
        "description": "Tai nghe gaming khong day TriForce 50mm, THX Spatial Audio, haptic feedback, RGB Chroma.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-KV4P-BK", "price": 4790000, "stock": 20, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-KV4P-WH", "price": 4790000, "stock": 12},
        ],
    },
    {
        "name": "Logitech G733 Lightspeed",
        "slug": "logitech-g733-lightspeed",
        "brand": "Logitech",
        "sku": "ACC-G733",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "phu-kien-gaming",
        "description": "Tai nghe gaming RGB khong day PRO-G 40mm, Lightspeed, 29h pin, headband treo, Discord Certified.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-G733-WH", "price": 2990000, "stock": 25, "is_default": True},
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-G733-BK", "price": 2990000, "stock": 20},
        ],
    },
    # -- Phones: Additional (to reach 20) --
    {
        "name": "Xiaomi 14T",
        "slug": "xiaomi-14t",
        "brand": "Xiaomi",
        "sku": "PHN-X14T",
        "product_type": "phone",
        "featured": False,
        "category_slug": "xiaomi",
        "description": "Premium tam trung voi MediaTek Dimensity 8300, Leica 50MP camera, 6.67-inch AMOLED 144Hz.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "variants": [
            {"color_name": "Titanium Gray", "color_code": "#8E8E93", "storage": "256GB", "ram": "8GB", "sku": "PHN-X14T-TG256", "price": 11990000, "stock": 25, "is_default": True},
            {"color_name": "Titanium Blue", "color_code": "#6A8FA8", "storage": "256GB", "ram": "8GB", "sku": "PHN-X14T-TB256", "price": 11990000, "stock": 20},
        ],
    },
    {
        "name": "OPPO Reno13 Pro",
        "slug": "oppo-reno13-pro",
        "brand": "OPPO",
        "sku": "PHN-OR13P",
        "product_type": "phone",
        "featured": False,
        "category_slug": "oppo",
        "description": "Smartphone phong cach MediaTek Dimensity 8350, 50MP selfie, 6.7-inch AMOLED 120Hz, sac 80W SUPERVOOC.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "variants": [
            {"color_name": "Purple", "color_code": "#8B5E8D", "storage": "256GB", "ram": "12GB", "sku": "PHN-OR13P-PU256", "price": 12990000, "stock": 20, "is_default": True},
            {"color_name": "Silver", "color_code": "#D1D1D6", "storage": "256GB", "ram": "12GB", "sku": "PHN-OR13P-SV256", "price": 12990000, "stock": 18},
        ],
    },
    {
        "name": "Vivo V50",
        "slug": "vivo-v50",
        "brand": "Vivo",
        "sku": "PHN-VV50",
        "product_type": "phone",
        "featured": False,
        "category_slug": "dien-thoai-vivo",
        "description": "Dien thoai tam trung Snapdragon 7 Gen 3, ZEISS 50MP camera, 6.78-inch AMOLED 120Hz, pin 5500mAh.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "variants": [
            {"color_name": "Rose Gold", "color_code": "#D4A59A", "storage": "256GB", "ram": "8GB", "sku": "PHN-VV50-RG256", "price": 9990000, "stock": 22, "is_default": True},
            {"color_name": "Star Black", "color_code": "#1C1C1E", "storage": "256GB", "ram": "8GB", "sku": "PHN-VV50-SB256", "price": 9990000, "stock": 20},
        ],
    },
    # -- Watches: Additional (to reach 20) --
    {
        "name": "Google Pixel Watch 3",
        "slug": "google-pixel-watch-3",
        "brand": "Google",
        "sku": "WCH-PW3",
        "product_type": "watch",
        "featured": True,
        "category_slug": "apple-watch",
        "description": "Smartwatch Wear OS 5, Actua AMOLED 2000 nits, Fitbit tich hop, ECG, phat hien te nga, pin 24h+.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Polished Silver", "color_code": "#D1D1D6", "version_name": "45mm BT", "sku": "WCH-PW3-SV45", "price": 8990000, "stock": 15, "is_default": True},
            {"color_name": "Matte Black", "color_code": "#2C2C2E", "version_name": "45mm BT", "sku": "WCH-PW3-BK45", "price": 8990000, "stock": 18},
        ],
    },
    {
        "name": "OnePlus Watch 3",
        "slug": "oneplus-watch-3",
        "brand": "OnePlus",
        "sku": "WCH-OPW3",
        "product_type": "watch",
        "featured": False,
        "category_slug": "samsung-galaxy-watch",
        "description": "Dong ho thong minh 1.5-inch LTPO AMOLED, Wear OS, Snapdragon W5 Gen 1, pin 4 ngay, chong nuoc 5ATM.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Radiant Steel", "color_code": "#8E8E93", "version_name": "46mm", "sku": "WCH-OPW3-RS46", "price": 7990000, "stock": 12, "is_default": True},
            {"color_name": "Black", "color_code": "#1C1C1E", "version_name": "46mm", "sku": "WCH-OPW3-BK46", "price": 7990000, "stock": 15},
        ],
    },
    {
        "name": "Amazfit Balance",
        "slug": "amazfit-balance",
        "brand": "Amazfit",
        "sku": "WCH-AMBAL",
        "product_type": "watch",
        "featured": False,
        "category_slug": "xiaomi-watch",
        "description": "Smartwatch Zepp OS 4.0, 1.5-inch AMOLED, BioTracker PPG, GPS, 14 ngay pin, the duc AI.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Midnight Black", "color_code": "#1C1C1E", "version_name": "46mm", "sku": "WCH-AMBAL-BK46", "price": 5490000, "stock": 20, "is_default": True},
            {"color_name": "Sunset Gray", "color_code": "#A0998A", "version_name": "46mm", "sku": "WCH-AMBAL-SG46", "price": 5490000, "stock": 14},
        ],
    },
    {
        "name": "Withings ScanWatch 2",
        "slug": "withings-scanwatch-2",
        "brand": "Withings",
        "sku": "WCH-SW2",
        "product_type": "watch",
        "featured": False,
        "category_slug": "huawei-watch",
        "description": "Dong ho y te 38mm, ECG, SpO2, TempBody, theo doi giac ngu, pin 30 ngay, thiet ke duong kinh dien.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "version_name": "42mm", "sku": "WCH-SW2-BK42", "price": 7990000, "stock": 10, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "version_name": "42mm", "sku": "WCH-SW2-WH42", "price": 7990000, "stock": 8},
        ],
    },
    # -- Accessories: Additional (to reach 20) --
    {
        "name": "Samsung T7 Shield 2TB",
        "slug": "samsung-t7-shield-2tb",
        "brand": "Samsung",
        "sku": "ACC-ST7S2",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "SSD di dong 2TB, USB 3.2 Gen 2 1050MB/s, chong nuoc IP65, chong roi 3m, AES 256-bit.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-ST7S2-BK", "price": 4990000, "stock": 25, "is_default": True},
            {"color_name": "Blue", "color_code": "#4A7B9D", "sku": "ACC-ST7S2-BL", "price": 4990000, "stock": 18},
        ],
    },
    {
        "name": "Belkin BoostCharge Pro 3-in-1",
        "slug": "belkin-boostcharge-pro-3-in-1",
        "brand": "Belkin",
        "sku": "ACC-BCP3",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "Sac khong day 3-trong-1 MagSafe 15W cho iPhone, Apple Watch, AirPods, thiet ke sang trong 15W Qi2.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "ACC-BCP3-WH", "price": 3290000, "stock": 20, "is_default": True},
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-BCP3-BK", "price": 3290000, "stock": 15},
        ],
    },
    {
        "name": "Anker USB-C Hub 8-in-1",
        "slug": "anker-usb-c-hub-8-in-1",
        "brand": "Anker",
        "sku": "ACC-AHUB8",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "Hub USB-C HDMI 4K 60Hz, 2xUSB-A, USB-C PD 100W, SD/microSD, Ethernet, cho laptop USB-C.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "Space Gray", "color_code": "#5A5A5A", "sku": "ACC-AHUB8-SG", "price": 1190000, "stock": 35, "is_default": True},
        ],
    },
    {
        "name": "SanDisk Extreme Portable 4TB",
        "slug": "sandisk-extreme-portable-4tb",
        "brand": "SanDisk",
        "sku": "ACC-SDEX4",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "SSD di dong 4TB, USB 3.2 Gen 2x2 2000MB/s, chong nuoc IP55, chong roi 2m, AES 256-bit.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "Orange", "color_code": "#FF6B35", "sku": "ACC-SDEX4-OR", "price": 7990000, "stock": 15, "is_default": True},
        ],
    },
    {
        "name": "Elgato Stream Deck+",
        "slug": "elgato-stream-deck-plus",
        "brand": "Elgato",
        "sku": "ACC-SDP",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "ban-phim",
        "description": "Stream controller voi 8 nut LCD, 4 dial cam ung, touch strip, dieu khien OBS, Streamlabs, chinh luong.",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d3b0d3b1?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-SDP-BK", "price": 4990000, "stock": 12, "is_default": True},
        ],
    },
    {
        "name": "Dell Universal Dock D6000",
        "slug": "dell-universal-dock-d6000",
        "brand": "Dell",
        "sku": "ACC-DUD6",
        "product_type": "accessory",
        "featured": False,
        "category_slug": "sac-cap",
        "description": "Dock DisplayLink 2xHDMI 4K, USB-C/A, Ethernet, USB-C PD 90W, cho laptop Windows/Mac, 130W power.",
        "image_url": "https://images.unsplash.com/photo-1629429408209-1f0fe1e7b2c5?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "ACC-DUD6-BK", "price": 4290000, "stock": 18, "is_default": True},
        ],
    },
    # -- Audio: Final batch (to reach 20) --
    {
        "name": "AKG N700NC M2",
        "slug": "akg-n700nc-m2",
        "brand": "AKG",
        "sku": "AUD-AKN700",
        "product_type": "audio",
        "featured": False,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe ANC cao cap 40mm driver, 23h pin, aptX HD, gap gon, am thanh tham chua chuan AKG Reference.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "sku": "AUD-AKN700-BK", "price": 4990000, "stock": 18, "is_default": True},
            {"color_name": "Silver", "color_code": "#D1D1D6", "sku": "AUD-AKN700-SV", "price": 4990000, "stock": 12},
        ],
    },
    {
        "name": "Sennheiser Momentum True Wireless 4",
        "slug": "sennheiser-momentum-tw4",
        "brand": "Sennheiser",
        "sku": "AUD-SMTW4",
        "product_type": "audio",
        "featured": True,
        "category_slug": "tai-nghe-bluetooth",
        "description": "Tai nghe true wireless cao cap nhat 7mm driver, Adaptive ANC, aptX Lossless, pin 30h, sac khong day Qi.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=800&q=80",
        "variants": [
            {"color_name": "Black Copper", "color_code": "#3A2A1A", "sku": "AUD-SMTW4-BK", "price": 6990000, "stock": 15, "is_default": True},
            {"color_name": "White Silver", "color_code": "#E8E4DF", "sku": "AUD-SMTW4-WH", "price": 6990000, "stock": 10},
        ],
    },
    # -- Watches: Final batch (to reach 20) --
    {
        "name": "Samsung Galaxy Fit 4",
        "slug": "samsung-galaxy-fit-4",
        "brand": "Samsung",
        "sku": "WCH-GF4",
        "product_type": "watch",
        "featured": False,
        "category_slug": "samsung-galaxy-watch",
        "description": "Vo tay thong minh 1.6-inch AMOLED, theo doi suc khoe 24/7, pin 15 ngay, chong nuoc 5ATM, Samsung Health.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Graphite", "color_code": "#4A4A4A", "sku": "WCH-GF4-GR", "price": 1490000, "stock": 45, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "sku": "WCH-GF4-WH", "price": 1490000, "stock": 30},
        ],
    },
    {
        "name": "Garmin Forerunner 165",
        "slug": "garmin-forerunner-165",
        "brand": "Garmin",
        "sku": "WCH-GFR165",
        "product_type": "watch",
        "featured": False,
        "category_slug": "garmin",
        "description": "Dong ho chay bo AMOLED 1.2-inch, GPS, HR, Garmin Coach, pin 13 ngay, Race Predictor, giao dien moi.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Black", "color_code": "#1C1C1E", "version_name": "43mm", "sku": "WCH-GFR165-BK43", "price": 6490000, "stock": 20, "is_default": True},
            {"color_name": "White", "color_code": "#FFFFFF", "version_name": "43mm", "sku": "WCH-GFR165-WH43", "price": 6490000, "stock": 15},
        ],
    },
    {
        "name": "Google Pixel Watch 3 41mm",
        "slug": "google-pixel-watch-3-41mm",
        "brand": "Google",
        "sku": "WCH-PW3-41",
        "product_type": "watch",
        "featured": False,
        "category_slug": "apple-watch",
        "description": "Smartwatch Wear OS 5, 41mm AMOLED 2000 nits, Fitbit, ECG, phat hien te nga, pin 24h, sac nhanh USB-C.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "variants": [
            {"color_name": "Polished Silver", "color_code": "#D1D1D6", "version_name": "41mm BT", "sku": "WCH-PW3-41-SV", "price": 7990000, "stock": 18, "is_default": True},
            {"color_name": "Matte Black", "color_code": "#2C2C2E", "version_name": "41mm BT", "sku": "WCH-PW3-41-BK", "price": 7990000, "stock": 14},
        ],
    },
]

# ---------------------------------------------------------------------------
# Specification templates
# ---------------------------------------------------------------------------

SPECIFICATIONS = {
    "phone": [
        ("Màn hình", "Công nghệ", "OLED Super Retina XDR / Dynamic AMOLED"),
        ("Màn hình", "Kích thước", "6.1 - 6.9 inch"),
        ("Màn hình", "Tần số quét", "120Hz ProMotion"),
        ("Màn hình", "Độ phân giải", "2796 x 1290 pixels"),
        ("Bộ xử lý", "Chip", "A18 Pro / Snapdragon 8 Elite"),
        ("Bộ xử lý", "RAM", "8GB - 12GB"),
        ("Bộ xử lý", "Bộ nhớ trong", "128GB - 1TB"),
        ("Camera", "Camera sau", "48MP chính + 48MP siêu rộng + 12MP telephoto"),
        ("Camera", "Camera trước", "12MP TrueDepth"),
        ("Pin & Sạc", "Dung lượng pin", "4500 - 6000mAh"),
        ("Pin & Sạc", "Sạc nhanh", "30W - 65W có dây, 25W không dây"),
        ("Kết nối", "SIM", "2 Nano SIM + eSIM"),
        ("Kết nối", "Kết nối", "5G, Wi-Fi 7, Bluetooth 5.4, NFC"),
        ("Khác", "Hệ điều hành", "iOS 19 / Android 16"),
        ("Khác", "Chống nước", "IP68"),
        ("Khác", "Cảm biến vân tay", "Face ID / Ultrasonic dưới màn hình"),
    ],
    "laptop": [
        ("Màn hình", "Công nghệ", "Liquid Retina XDR / OLED"),
        ("Màn hình", "Kích thước", "14 - 16 inch"),
        ("Màn hình", "Độ phân giải", "3456 x 2234 pixels"),
        ("Màn hình", "Tần số quét", "120Hz ProMotion"),
        ("Phần cứng", "CPU", "Apple M4 Max / Intel Core Ultra 9"),
        ("Phần cứng", "RAM", "16GB - 64GB Unified Memory"),
        ("Phần cứng", "Ổ cứng", "512GB - 2TB SSD"),
        ("Phần cứng", "GPU", "Tích hợp / RTX 4070"),
        ("Pin & Sạc", "Dung lượng pin", "72 - 100Wh"),
        ("Pin & Sạc", "Sạc nhanh", "100W - 140W USB-C"),
        ("Kết nối", "Cổng kết nối", "Thunderbolt 5, USB-C, HDMI 2.1, MagSafe"),
        ("Khác", "Hệ điều hành", "macOS Sequoia / Windows 11"),
        ("Khác", "Trọng lượng", "1.08 - 2.15 kg"),
        ("Khác", "Bảo mật", "Touch ID / Windows Hello"),
    ],
    "audio": [
        ("Thiết kế", "Loại", "Over-ear / In-ear"),
        ("Thiết kế", "Trọng lượng", "250 - 380g"),
        ("Âm thanh", "Driver", "40mm - 50mm / Dynamic"),
        ("Âm thanh", "Đáp ứng tần số", "4Hz - 40kHz"),
        ("Âm thanh", "Chống ồn", "Chủ động ANC Adaptive"),
        ("Âm thanh", "Spatial Audio", "Hỗ trợ Dolby Atmos"),
        ("Kết nối", "Bluetooth", "5.4, codec LDAC/AAC/SBC"),
        ("Kết nối", "Khoảng cách", "Lên đến 15m"),
        ("Pin", "Thời lượng pin", "30 - 70 giờ"),
        ("Pin", "Sạc nhanh", "10 phút sạc = 5 giờ nghe"),
        ("Khác", "Chống nước", "IPX4 - IP55"),
        ("Khác", "Micro", "Mic kép khử ồn AI"),
    ],
    "watch": [
        ("Màn hình", "Công nghệ", "OLED / AMOLED"),
        ("Màn hình", "Kích thước", "40 - 51mm"),
        ("Màn hình", "Độ sáng tối đa", "2000 - 3000 nits"),
        ("Phần cứng", "Chip", "S10 / Exynos W1000"),
        ("Phần cứng", "Bộ nhớ", "32GB - 64GB"),
        ("Phần cứng", "RAM", "1GB - 2GB"),
        ("Cảm biến", "Sức khỏe", "Nhịp tim, ECG, SpO2, nhiệt độ"),
        ("Cảm biến", "GPS", "GPS L1+L5 đa băng tần"),
        ("Pin", "Thời lượng pin", "18 giờ - 29 ngày"),
        ("Pin", "Sạc", "Sạc từ Qi, sạc nhanh"),
        ("Khác", "Chống nước", "10 ATM / WR100"),
        ("Khác", "Hệ điều hành", "watchOS 12 / Wear OS 5"),
    ],
    "accessory": [
        ("Thiết kế", "Loại", "Chuột / Bàn phím / Ốp lưng / Sạc / Tai nghe"),
        ("Thiết kế", "Chất liệu", "Nhôm / Silicone / Nhựa ABS"),
        ("Thiết kế", "Trọng lượng", "60g - 300g"),
        ("Kết nối", "Kết nối", "USB-C / Wireless / Bluetooth 5.4"),
        ("Kết nối", "Tương thích", "Đa nền tảng (PC, Mac, Console)"),
        ("Khác", "Tính năng", "RGB / MagSafe / GaN / Chống ồn"),
        ("Khác", "Bảo hành", "12 - 24 tháng chính hãng"),
    ],
}

# ---------------------------------------------------------------------------
# Related products mapping
# ---------------------------------------------------------------------------

RELATED_MAP = {
    "PHN-IP16PM": ["PHN-IP16P", "PHN-IP16", "AUD-APP3", "WCH-AWU3"],
    "PHN-IP16P": ["PHN-IP16PM", "PHN-IP16", "AUD-APP3", "WCH-AWS10"],
    "PHN-IP16": ["PHN-IP16PM", "PHN-IP16P", "AUD-APP3", "ACC-ASC16"],
    "PHN-IP15": ["PHN-IPSE4", "AUD-APP3", "ACC-ASC16"],
    "PHN-IPSE4": ["PHN-IP15", "AUD-APP3", "WCH-AWSE3"],
    "PHN-S25U": ["PHN-S25P", "PHN-S25", "AUD-GB3P", "WCH-GW7"],
    "PHN-S25P": ["PHN-S25U", "PHN-S25", "AUD-GB3P"],
    "PHN-S25": ["PHN-S25U", "PHN-S25P", "AUD-GB3P"],
    "PHN-ZF7": ["PHN-ZF7F", "PHN-S25U"],
    "PHN-ZF7F": ["PHN-ZF7", "PHN-S25"],
    "PHN-X15P": ["PHN-RN14P", "PHN-PX7P", "WCH-XWS4"],
    "PHN-OFXP": ["PHN-VX200"],
    "PHN-VX200": ["PHN-OFXP"],
    "LAP-MBP16": ["LAP-MBP14", "LAP-MBA15", "ACC-UGAN"],
    "LAP-MBP14": ["LAP-MBP16", "LAP-MBA15", "ACC-UGAN"],
    "LAP-MBA15": ["LAP-MBP14", "LAP-MBP16", "ACC-UGAN"],
    "LAP-ROGG16": ["LAP-LEG7", "ACC-HX3", "ACC-GPX2"],
    "LAP-XPS16": ["LAP-TPX1C", "ACC-APC"],
    "LAP-LEG7": ["LAP-ROGG16", "ACC-RBW4", "ACC-HX3"],
    "LAP-TPX1C": ["LAP-XPS16", "ACC-APC"],
    "AUD-WHXM6": ["AUD-BQCU", "AUD-SM4", "AUD-JBL770"],
    "AUD-APP3": ["AUD-APM2", "AUD-GB3P", "AUD-NE"],
    "AUD-APM2": ["AUD-APP3", "AUD-WHXM6"],
    "AUD-GB3P": ["AUD-APP3", "AUD-NE", "WCH-GW7"],
    "AUD-BQCU": ["AUD-WHXM6", "AUD-SM4"],
    "AUD-SM4": ["AUD-WHXM6", "AUD-BQCU"],
    "AUD-NE": ["AUD-APP3", "AUD-GB3P"],
    "AUD-JBL770": ["AUD-WHXM6", "AUD-BQCU"],
    "WCH-AWU3": ["WCH-AWS10", "WCH-AWSE3", "PHN-IP16PM"],
    "WCH-AWS10": ["WCH-AWU3", "WCH-AWSE3", "PHN-IP16"],
    "WCH-AWSE3": ["WCH-AWS10", "WCH-AWU3", "PHN-IPSE4"],
    "WCH-GW7": ["WCH-GF265", "PHN-S25U", "AUD-GB3P"],
    "WCH-XWS4": ["PHN-X15P", "WCH-GF265"],
    "WCH-GF265": ["WCH-GF8", "WCH-GW7"],
    "WCH-GF8": ["WCH-GF265", "WCH-AWU3"],
    "ACC-GPX2": ["ACC-RDV3", "ACC-HX3", "LAP-ROGG16"],
    "ACC-RDV3": ["ACC-GPX2", "ACC-RBW4"],
    "ACC-RBW4": ["ACC-RDV3", "ACC-HX3"],
    "ACC-ASC16": ["PHN-IP16PM", "PHN-IP16", "ACC-APC"],
    "ACC-APC": ["ACC-UGAN", "ACC-ASC16"],
    "ACC-UGAN": ["ACC-APC", "LAP-MBP16", "LAP-MBP14"],
    "ACC-HX3": ["ACC-SANP", "ACC-GPX2", "LAP-LEG7"],
    "ACC-SANP": ["ACC-HX3", "ACC-GPX2", "LAP-ROGG16"],
}

# ---------------------------------------------------------------------------
# Product hotspots (image interactive points)
# ---------------------------------------------------------------------------

HOTSPOTS = {
    "PHN-IP16PM": [
        {"label": "Camera 48MP Fusion", "type": "camera", "x": 82, "y": 15, "description": "Camera chính 48MP với cảm biến Fusion và telephoto 5x quang học."},
        {"label": "Nút Action", "type": "button", "x": 70, "y": 30, "description": "Nút Action có thể tùy chỉnh phím tắt nhanh."},
        {"label": "Nút Camera Control", "type": "button", "x": 75, "y": 50, "description": "Nút Camera Control chuyên dụng cho chụp ảnh nhanh."},
        {"label": "Màn hình 6.9 inch", "type": "display", "x": 50, "y": 22, "description": "Màn hình Super Retina XDR OLED 6.9 inch 120Hz."},
        {"label": "Vỏ Titanium", "type": "material", "x": 20, "y": 45, "description": "Vỏ titanium cấp 5 siêu bền và nhẹ."},
    ],
    "LAP-ROGG16": [
        {"label": "Màn hình OLED 2.5K", "type": "display", "x": 50, "y": 20, "description": "Màn hình OLED 16 inch 2.5K 240Hz."},
        {"label": "Bàn phím RGB", "type": "keyboard", "x": 50, "y": 70, "description": "Bàn phím RGB từng phím với Per-Key Lighting."},
        {"label": "Touchpad", "type": "touchpad", "x": 50, "y": 85, "description": "Touchpad lớn hỗ trợ cử chỉ Windows Precision."},
        {"label": "Logo ROG", "type": "logo", "x": 30, "y": 55, "description": "Logo ROG phát sáng RGB AniMe Matrix."},
    ],
    "LAP-LEG7": [
        {"label": "Màn hình 16 inch IPS", "type": "display", "x": 50, "y": 18, "description": "Màn hình 16 inch WQXGA IPS 240Hz."},
        {"label": "Bàn phím Legion", "type": "keyboard", "x": 50, "y": 68, "description": "Bàn phím TrueStrike với switch cơ."},
        {"label": "Đèn RGB", "type": "lighting", "x": 50, "y": 60, "description": "Hệ thống đèn RGB 4 vùng."},
        {"label": "Cổng tản nhiệt", "type": "vent", "x": 65, "y": 45, "description": "Hệ thống tản nhiệt ColdFront 5.0."},
    ],
}

# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def _build_category_tree(session, parent, nodes):
    mapping = {}
    for node in nodes:
        slug = node["slug"]
        parent_path = f"{parent.path}/" if parent else ""
        full_path = f"{parent_path}{slug}"

        cat = session.query(Category).filter(Category.slug == slug).first()
        if not cat:
            cat = Category(
                id=str(uuid.uuid4()),
                name=node["name"],
                slug=slug,
                description=f"Sản phẩm {node['name'].lower()} chất lượng cao.",
                parent_id=parent.id if parent else None,
                level=(parent.level + 1) if parent else 0,
                path=full_path,
            )
            session.add(cat)
            session.flush()
            print(f"[CATEGORY] {cat.name} ({full_path})")
        mapping[slug] = cat

        children = node.get("children", [])
        if children:
            child_map = _build_category_tree(session, cat, children)
            mapping.update(child_map)

    return mapping


def _seed_variants(session, product, variants_data):
    for vd in variants_data:
        variant_sku = vd["sku"]
        existing_v = session.query(ProductVariant).filter(ProductVariant.sku == variant_sku).first()
        if existing_v:
            continue

        variant = ProductVariant(
            id=str(uuid.uuid4()),
            product_id=product.id,
            color_name=vd.get("color_name"),
            color_code=vd.get("color_code"),
            version_name=vd.get("version_name"),
            ram=vd.get("ram"),
            storage=vd.get("storage"),
            sku=variant_sku,
            price=vd["price"],
            stock=vd.get("stock", 0),
            image_url=vd.get("image_url") or product.image_url,
            is_default=vd.get("is_default", False),
        )
        session.add(variant)
        session.flush()

    existing_default = session.query(ProductVariant).filter(
        ProductVariant.product_id == product.id,
        ProductVariant.is_default == True,
    ).first()

    if not existing_default:
        first_variant = session.query(ProductVariant).filter(
            ProductVariant.product_id == product.id,
        ).order_by(ProductVariant.created_at).first()
        if first_variant:
            first_variant.is_default = True
            session.flush()


def _seed_specifications(session, product):
    template_list = SPECIFICATIONS.get(product.product_type, [])
    if not template_list:
        return

    existing_count = session.query(ProductSpecification).filter(
        ProductSpecification.product_id == product.id,
    ).count()
    if existing_count > 0:
        return

    for idx, (group_name, spec_key, spec_value) in enumerate(template_list, start=1):
        spec = ProductSpecification(
            product_id=product.id,
            group_name=group_name,
            spec_key=spec_key,
            spec_value=spec_value,
            display_order=idx,
        )
        session.add(spec)
    session.flush()


def _seed_related(session, product_map):
    for parent_sku, related_skus in RELATED_MAP.items():
        parent = product_map.get(parent_sku)
        if not parent:
            continue

        for rel_sku in related_skus:
            related = product_map.get(rel_sku)
            if not related or related.id == parent.id:
                continue

            existing = session.query(RelatedProduct).filter(
                RelatedProduct.product_id == parent.id,
                RelatedProduct.related_product_id == related.id,
            ).first()
            if existing:
                continue

            rp = RelatedProduct(
                id=str(uuid.uuid4()),
                product_id=parent.id,
                related_product_id=related.id,
            )
            session.add(rp)


def _seed_hotspots(session, product_map):
    inspector = inspect(session.bind)
    if "product_hotspots" not in inspector.get_table_names():
        return

    from .models import ProductHotspot as PH
    for product_sku, hotspots_list in HOTSPOTS.items():
        product = product_map.get(product_sku)
        if not product:
            continue

        already = session.query(PH).filter(PH.product_id == product.id).count()
        if already > 0:
            continue

        for h in hotspots_list:
            hs = PH(
                id=str(uuid.uuid4()),
                product_id=product.id,
                label=h["label"],
                type=h["type"],
                x_percent=h["x"],
                y_percent=h["y"],
                description=h.get("description"),
            )
            session.add(hs)
        session.flush()


# ---------------------------------------------------------------------------
# Main seed entry point
# ---------------------------------------------------------------------------

def seed_database():
    session = SessionLocal()
    try:
        print("=" * 60)
        print("  ELECTRONICS-COMMERCE SEED v2")
        print("=" * 60)

        print("\n--- Categories ---")
        category_map = _build_category_tree(session, None, CATEGORY_TREE)
        session.commit()
        print(f"  Total categories: {len(category_map)}")

        print("\n--- Products & Variants ---")
        product_map = {}
        for pd in PRODUCTS:
            cat = category_map.get(pd["category_slug"])
            if not cat:
                print(f"  [WARN] No category for slug '{pd['category_slug']}', skipping {pd['name']}")
                continue

            existing_p = session.query(Product).filter(Product.sku == pd["sku"]).first()
            if existing_p:
                product_map[pd["sku"]] = existing_p
                print(f"  [SKIP] Product exists: {pd['name']} ({pd['sku']})")
                continue

            product = Product(
                id=str(uuid.uuid4()),
                name=pd["name"],
                description=pd["description"],
                price=0,
                stock=0,
                category_id=cat.id,
                brand=pd["brand"],
                sku=pd["sku"],
                product_type=pd["product_type"],
                featured=pd.get("featured", False),
                status="active",
                image_url=pd.get("image_url"),
                rating=0.0,
                review_count=0,
                view_count=0,
                embedding=None,
            )
            session.add(product)
            session.flush()
            product_map[pd["sku"]] = product
            print(f"  [CREATE] Product: {pd['name']}")

            _seed_variants(session, product, pd.get("variants", []))

            default_v = session.query(ProductVariant).filter(
                ProductVariant.product_id == product.id,
                ProductVariant.is_default == True,
            ).first()
            if default_v:
                product.price = default_v.price
                product.stock = default_v.stock
            else:
                all_variants = session.query(ProductVariant).filter(
                    ProductVariant.product_id == product.id,
                ).order_by(ProductVariant.price).all()
                if all_variants:
                    product.price = all_variants[0].price
                    product.stock = sum(v.stock for v in all_variants)

            session.flush()

        session.commit()
        print(f"  Total products: {len(product_map)}")

        print("\n--- Specifications ---")
        for product in product_map.values():
            _seed_specifications(session, product)
        session.commit()
        print("  Done.")

        print("\n--- Related Products ---")
        _seed_related(session, product_map)
        session.commit()
        print("  Done.")

        print("\n--- Hotspots ---")
        _seed_hotspots(session, product_map)
        session.commit()
        print("  Done.")

        print("\n" + "=" * 60)
        print("  Seed completed successfully!")
        print("=" * 60)

    except Exception as exc:
        session.rollback()
        print(f"\n[ERROR] Seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
