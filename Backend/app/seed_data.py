from __future__ import annotations

import uuid
from datetime import datetime

from app.core.database import Base, SessionLocal, engine
from app.models import (
    Category,
    CpuBenchmark,
    GameRequirement,
    GpuBenchmark,
    Product,
    ProductSpecification,
    ProductVariant,
    RelatedProduct,
)


def gen_id() -> str:
    return str(uuid.uuid4())


def gen_sku(prefix: str, n: int) -> str:
    return f"{prefix}-{n:04d}"


CATEGORIES = [
    ("Dien thoai", "dien-thoai", "Dien thoai chinh hang phu hop thi truong Viet Nam.", None),
    ("Laptop", "laptop", "Laptop gaming, van phong, hoc tap va sang tao noi dung.", None),
    ("Tai nghe & Am thanh", "tai-nghe-am-thanh", "Tai nghe chong on, true wireless va gaming headset.", None),
    ("Phu kien", "phu-kien", "Phu kien sac, bao ve, hub va gaming gear.", None),
    ("Tablet", "tablet", "May tinh bang chuan bi mo ban.", None),
    ("Dong ho thong minh", "dong-ho-thong-minh", "Smartwatch chuan bi mo ban.", None),
    ("iPhone", "iphone", "Dien thoai Apple iPhone.", "dien-thoai"),
    ("Android cao cap", "android-cao-cap", "Android flagship va can flagship.", "dien-thoai"),
    ("Android pho thong", "android-pho-thong", "Dien thoai Android gia tot.", "dien-thoai"),
    ("Laptop gaming", "laptop-gaming", "Laptop GPU roi cho game va do hoa.", "laptop"),
    ("Laptop van phong", "laptop-van-phong", "Laptop mong nhe, pin tot cho cong viec.", "laptop"),
    ("Laptop sinh vien", "laptop-sinh-vien", "Laptop gia hop ly cho hoc tap.", "laptop"),
    ("MacBook", "macbook", "Laptop Apple MacBook.", "laptop"),
    ("Tai nghe chong on", "tai-nghe-chong-on", "Tai nghe ANC cao cap.", "tai-nghe-am-thanh"),
    ("Tai nghe gaming", "tai-nghe-gaming", "Headset gaming do tre thap.", "tai-nghe-am-thanh"),
    ("Tai nghe True Wireless", "tai-nghe-tws", "Tai nghe TWS nho gon.", "tai-nghe-am-thanh"),
    ("Sac & Pin du phong", "sac-pin-du-phong", "Sac nhanh GaN va pin du phong.", "phu-kien"),
    ("Op lung & Bao ve", "op-lung-bao-ve", "Op lung va bao ve thiet bi.", "phu-kien"),
    ("Hub & Adapter", "hub-adapter", "Hub USB-C, adapter va dau doc.", "phu-kien"),
    ("Chuot & Gaming gear", "chuot-gaming", "Chuot va phu kien gaming.", "phu-kien"),
]


CPU_BENCHMARKS = [
    ("Intel Core i3-1215U", 8500, "i3-1215u,core i3 1215u"),
    ("Intel Core i5-1235U", 11800, "i5-1235u,core i5 1235u"),
    ("Intel Core i5-12450H", 12500, "i5-12450h,core i5 12450h"),
    ("Intel Core i5-13420H", 14200, "i5-13420h,core i5 13420h"),
    ("Intel Core i7-12700H", 17500, "i7-12700h,core i7 12700h"),
    ("Intel Core i7-13700H", 18500, "i7-13700h,core i7 13700h"),
    ("Intel Core i7-14700HX", 21000, "i7-14700hx"),
    ("Intel Core i9-13900H", 21500, "i9-13900h,core i9 13900h"),
    ("Intel Core i9-14900HX", 24000, "i9-14900hx"),
    ("AMD Ryzen 5 5500U", 9500, "ryzen 5 5500u"),
    ("AMD Ryzen 5 5600H", 13500, "ryzen 5 5600h"),
    ("AMD Ryzen 5 7530U", 11500, "ryzen 5 7530u"),
    ("AMD Ryzen 7 5800H", 15500, "ryzen 7 5800h"),
    ("AMD Ryzen 7 6800H", 17000, "ryzen 7 6800h"),
    ("AMD Ryzen 7 7735HS", 18000, "ryzen 7 7735hs"),
    ("AMD Ryzen 7 7840HS", 19500, "ryzen 7 7840hs"),
    ("AMD Ryzen 9 7945HX", 25000, "ryzen 9 7945hx"),
    ("Apple M1", 15000, "m1,apple m1"),
    ("Apple M2", 17500, "m2,apple m2"),
    ("Apple M3", 20000, "m3,apple m3"),
    ("Apple M3 Pro", 22000, "m3 pro,apple m3 pro"),
    ("Apple M3 Max", 27000, "m3 max,apple m3 max"),
    ("Qualcomm Snapdragon X Elite", 23000, "snapdragon x elite"),
    ("Intel Core Ultra 5 125H", 16000, "core ultra 5 125h,ultra 5 125h"),
    ("Intel Core Ultra 7 155H", 19000, "core ultra 7 155h,ultra 7 155h"),
]


GPU_BENCHMARKS = [
    ("NVIDIA GeForce GTX 1650", 4500, "gtx 1650,geforce gtx 1650"),
    ("NVIDIA GeForce GTX 1660 Ti", 6500, "gtx 1660 ti"),
    ("NVIDIA GeForce RTX 3050", 6800, "rtx 3050,rtx3050"),
    ("NVIDIA GeForce RTX 3060", 9500, "rtx 3060,rtx3060"),
    ("NVIDIA GeForce RTX 3070 Ti", 13000, "rtx 3070 ti"),
    ("NVIDIA GeForce RTX 4050", 11500, "rtx 4050,rtx4050"),
    ("NVIDIA GeForce RTX 4060", 14500, "rtx 4060,rtx4060"),
    ("NVIDIA GeForce RTX 4070", 18500, "rtx 4070,rtx4070"),
    ("NVIDIA GeForce RTX 4070 Ti", 23000, "rtx 4070 ti"),
    ("NVIDIA GeForce RTX 4080", 26000, "rtx 4080,rtx4080"),
    ("NVIDIA GeForce RTX 4090", 33000, "rtx 4090,rtx4090"),
    ("AMD Radeon RX 6600M", 8500, "rx 6600m,radeon rx 6600m"),
    ("AMD Radeon RX 6700M", 11000, "rx 6700m"),
    ("AMD Radeon RX 7600M XT", 12000, "rx 7600m xt"),
    ("AMD Radeon RX 7700S", 13500, "rx 7700s"),
    ("AMD Radeon 780M (iGPU)", 3800, "radeon 780m,amd 780m"),
    ("Intel Iris Xe Graphics", 1800, "iris xe,intel iris xe"),
    ("Apple M3 GPU (10-core)", 18000, "m3 gpu 10 core"),
    ("Apple M3 Pro GPU (18-core)", 22000, "m3 pro gpu 18 core"),
    ("Apple M3 Max GPU (40-core)", 32000, "m3 max gpu 40 core"),
]


GAME_REQUIREMENTS = [
    ("Valorant", "valorant,val", 3000, 6000, 9000, 4000, 8000, 11000, 4, 8, 16),
    ("League of Legends", "lol,league of legends,lien minh", 2000, 4500, 7000, 3500, 7000, 10000, 4, 8, 16),
    ("Counter-Strike 2", "cs2,counter strike 2,csgo", 4500, 9000, 14500, 6000, 11000, 18000, 8, 16, 16),
    ("PUBG: Battlegrounds", "pubg,playerunknown battlegrounds", 4500, 8500, 14000, 6000, 12000, 18000, 8, 16, 16),
    ("Fortnite", "fortnite", 4000, 9000, 18000, 5000, 11000, 19000, 8, 16, 16),
    ("Cyberpunk 2077", "cyberpunk,cyberpunk 2077", 6800, 11500, 22000, 9000, 12500, 18500, 8, 16, 16),
    ("GTA V", "gta 5,gta v,grand theft auto 5", 3500, 7000, 11500, 5000, 9000, 13000, 4, 8, 16),
    ("Red Dead Redemption 2", "rdr2,red dead redemption 2", 6500, 11000, 18500, 8000, 13500, 19000, 12, 16, 32),
    ("Elden Ring", "elden ring", 6000, 9500, 14500, 7000, 12500, 18000, 12, 16, 16),
    ("God of War", "god of war,gow", 4500, 8500, 14000, 6000, 12000, 17000, 8, 16, 16),
    ("Hogwarts Legacy", "hogwarts legacy,hogwarts", 6000, 11500, 18500, 8000, 14000, 20000, 16, 16, 32),
    ("Baldur's Gate 3", "bg3,baldur gate 3,baldur's gate 3", 6000, 11000, 18000, 7500, 13500, 20000, 8, 16, 16),
    ("Overwatch 2", "ow2,overwatch 2,overwatch", 3500, 7000, 11500, 5000, 9000, 14500, 8, 8, 16),
    ("Apex Legends", "apex,apex legends", 3500, 7000, 11500, 5500, 9500, 15000, 8, 8, 16),
    ("FIFA / EA Sports FC", "fifa,ea fc,ea sports fc,ea fc 24", 3000, 6000, 10000, 4000, 8000, 12000, 8, 16, 16),
    ("The Witcher 3", "witcher 3,the witcher 3", 5000, 9000, 14000, 6500, 11500, 17000, 8, 12, 16),
    ("Minecraft", "minecraft", 1800, 3500, 7000, 3000, 6000, 9500, 4, 8, 8),
    ("Call of Duty: Warzone", "warzone,cod warzone,call of duty warzone", 5000, 9500, 14500, 7000, 12500, 18000, 8, 16, 16),
    ("Diablo IV", "diablo 4,diablo iv", 5000, 9000, 14000, 6500, 11500, 17500, 8, 16, 16),
    ("AAA Games 2024", "aaa,aaa games,game aaa,game moi", 9000, 14500, 26000, 10000, 15000, 22000, 16, 16, 32),
]


COLOR_CODES = {
    "Den": "#111111",
    "Trang": "#F7F7F7",
    "Xanh": "#2563EB",
    "Bac": "#C0C0C0",
    "Vang": "#D4AF37",
    "Hong": "#F9A8D4",
    "Xam": "#6B7280",
    "Tim": "#8B5CF6",
    "Kem": "#EADBC8",
    "Do": "#DC2626",
    "Titan Den": "#2D2D2D",
    "Titan Trang": "#E8E1D9",
    "Titan Sa Mac": "#C8A26A",
    "Titan Xam": "#8A8A8A",
}


def compare_price(price: int, bump: float = 0.1) -> int:
    return int(round(price * (1 + bump) / 10000) * 10000)


def variant(color: str, storage: str | None, ram: str | None, price: int, stock: int, default: bool = False, version: str | None = None):
    return {
        "color_name": color,
        "color_code": COLOR_CODES.get(color, "#64748B"),
        "storage": storage,
        "ram": ram,
        "version_name": version,
        "price": price,
        "compare_price": compare_price(price),
        "stock": stock,
        "is_default": default,
    }


def phone_specs(display: str, camera: str, chip: str, ram: str, storage: str, battery: str, charge: str, note: str) -> list[tuple[str, str, str, int]]:
    return [
        ("Man hinh", "Kich thuoc", display, 0),
        ("Man hinh", "Cong nghe", "OLED/AMOLED 120Hz, do sang cao, hien thi HDR", 1),
        ("Man hinh", "Do phan giai", "FHD+ den QHD+ tuy model", 2),
        ("Camera", "Camera sau", camera, 0),
        ("Camera", "Camera truoc", "12MP den 32MP, ho tro quay video 4K tuy model", 1),
        ("Camera", "Tinh nang noi bat", note, 2),
        ("Hieu nang", "Chip xu ly", chip, 0),
        ("Hieu nang", "RAM", ram, 1),
        ("Luu tru", "Bo nho trong", storage, 0),
        ("Pin va sac", "Dung luong pin", battery, 0),
        ("Pin va sac", "Sac nhanh", charge, 1),
        ("Ket noi", "Mang", "5G, 4G LTE, NFC tuy thi truong", 0),
        ("Ket noi", "Wi-Fi / Bluetooth", "Wi-Fi 6/6E/7, Bluetooth 5.2 tro len", 1),
        ("Thiet ke", "Chong nuoc", "IP54 den IP68 tuy model", 0),
    ]


def laptop_specs(display: str, cpu: str, gpu: str, ram: str, storage: str, battery: str, weight: str, note: str) -> list[tuple[str, str, str, int]]:
    return [
        ("Man hinh", "Kich thuoc", display, 0),
        ("Man hinh", "Cong nghe", "IPS/OLED, chong choi, mau sac phu hop phan khuc", 1),
        ("Hieu nang", "CPU", cpu, 0),
        ("Hieu nang", "GPU", gpu, 1),
        ("Hieu nang", "RAM", ram, 2),
        ("Hieu nang", "Ghi chu hieu nang", note, 3),
        ("Luu tru", "O cung", storage, 0),
        ("Luu tru", "Khe mo rong", "M.2 NVMe tuy cau hinh", 1),
        ("Ket noi", "Cong", "USB-A, USB-C, HDMI, audio 3.5mm tuy dong may", 0),
        ("Ket noi", "Wi-Fi", "Wi-Fi 6/6E/7, Bluetooth 5.2 tro len", 1),
        ("Pin va sac", "Dung luong pin", battery, 0),
        ("Pin va sac", "Sac di kem", "USB-C/GaN hoac adapter cong suat cao tuy dong may", 1),
        ("Thiet ke", "Trong luong", weight, 0),
        ("Thiet ke", "He dieu hanh", "Windows 11 Home/Pro hoac macOS", 1),
    ]


def audio_specs(driver: str, anc: str, codec: str, bluetooth: str, battery: str, weight: str, extra: str) -> list[tuple[str, str, str, int]]:
    return [
        ("Am thanh", "Driver", driver, 0),
        ("Am thanh", "Chong on", anc, 1),
        ("Am thanh", "Codec Bluetooth", codec, 2),
        ("Ket noi", "Chuan Bluetooth", bluetooth, 0),
        ("Ket noi", "Do tre", "Do tre thap khi dung che do game/low latency neu co", 1),
        ("Ket noi", "Co day hay khong", "Khong day, mot so model ho tro cap 3.5mm/USB-C", 2),
        ("Pin va sac", "Thoi luong pin tai nghe", battery, 0),
        ("Pin va sac", "Sac nhanh", "5-10 phut sac cho 1-5 gio nghe tuy model", 1),
        ("Thiet ke", "Trong luong", weight, 0),
        ("Thiet ke", "Tinh nang them", extra, 1),
    ]


def accessory_specs(kind: str, main: str, ports: str, power: str, extra: str) -> list[tuple[str, str, str, int]]:
    return [
        ("Thong so chinh", "Loai san pham", kind, 0),
        ("Thong so chinh", "Thong so noi bat", main, 1),
        ("Thong so chinh", "Cong / tuong thich", ports, 2),
        ("Nguon va sac", "Cong suat", power, 0),
        ("Thiet ke", "Chat lieu", "Nhua cao cap, hop kim hoac silicone tuy san pham", 0),
        ("Thiet ke", "Tinh nang them", extra, 1),
        ("Bao hanh", "Thoi gian", "12 thang chinh hang", 0),
        ("Phu hop", "Nhu cau", "Su dung hang ngay, di lam, di hoc hoac gaming", 1),
    ]


PRODUCTS = [
    # Smartphones: 20
    {"name": "iPhone 16 Pro Max", "brand": "Apple", "sku": "IP16PM-001", "product_type": "phone", "category_slug": "iphone", "price": 33990000, "rating": 4.9, "review_count": 312, "featured": True, "description": "iPhone 16 Pro Max voi chip A18 Pro, man hinh lon 6.9 inch va camera 48MP Fusion. May phu hop nguoi dung can hieu nang cao, quay phim tot va thoi luong pin dai.", "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=900&q=80", "variants": [variant("Titan Den", "256GB", "8GB", 33990000, 45, True), variant("Titan Den", "512GB", "8GB", 38490000, 30), variant("Titan Trang", "256GB", "8GB", 33990000, 38), variant("Titan Sa Mac", "1TB", "8GB", 45990000, 15)], "specs": phone_specs("6.9 inch", "48MP Fusion + 48MP Ultra Wide + 12MP Telephoto 5x", "Apple A18 Pro", "8GB", "256GB / 512GB / 1TB", "4685 mAh", "MagSafe 25W, USB-C 20W tro len", "Camera Control, ProRAW, 4K Dolby Vision")},
    {"name": "Samsung Galaxy S25 Ultra", "brand": "Samsung", "sku": "SGS25U-002", "product_type": "phone", "category_slug": "android-cao-cap", "price": 32990000, "rating": 4.9, "review_count": 260, "featured": True, "description": "Galaxy S25 Ultra la flagship Android voi Snapdragon 8 Elite, camera 200MP va S Pen. May manh ve zoom, ghi chu va xu ly AI tren thiet bi.", "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=900&q=80", "variants": [variant("Titan Xam", "256GB", "12GB", 32990000, 35, True), variant("Titan Den", "512GB", "12GB", 36990000, 22), variant("Titan Bac", "1TB", "12GB", 43990000, 8)], "specs": phone_specs("6.9 inch", "200MP wide + 50MP periscope + 50MP ultrawide + 10MP tele", "Qualcomm Snapdragon 8 Elite", "12GB", "256GB / 512GB / 1TB", "5000 mAh", "45W co day, 15W khong day", "S Pen, Galaxy AI, zoom xa tot")},
    {"name": "Google Pixel 9 Pro", "brand": "Google", "sku": "GP9P-003", "product_type": "phone", "category_slug": "android-cao-cap", "price": 24990000, "rating": 4.7, "review_count": 88, "featured": False, "description": "Pixel 9 Pro noi bat voi camera tinh toan, Android goc va tinh nang AI cua Google. May phu hop nguoi thich chup anh nhanh, mau anh tu nhien.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "128GB", "16GB", 24990000, 20, True), variant("Kem", "256GB", "16GB", 27990000, 16), variant("Hong", "256GB", "16GB", 27990000, 12)], "specs": phone_specs("6.3 inch", "50MP wide + 48MP tele + 48MP ultrawide", "Google Tensor G4", "16GB", "128GB / 256GB", "4700 mAh", "27W co day, 21W khong day", "AI photo editing, Android cap nhat lau dai")},
    {"name": "Xiaomi 14 Ultra", "brand": "Xiaomi", "sku": "XM14U-004", "product_type": "phone", "category_slug": "android-cao-cap", "price": 25990000, "rating": 4.8, "review_count": 140, "featured": True, "description": "Xiaomi 14 Ultra tap trung vao nhiep anh voi he camera Leica va cam bien 1 inch. Cau hinh Snapdragon 8 Gen 3 van rat manh cho game va tac vu nang.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "512GB", "16GB", 25990000, 25, True), variant("Trang", "512GB", "16GB", 25990000, 18), variant("Xanh", "1TB", "16GB", 29990000, 8)], "specs": phone_specs("6.73 inch", "Leica 50MP 1-inch + 50MP tele + 50MP periscope + 50MP ultrawide", "Qualcomm Snapdragon 8 Gen 3", "16GB", "512GB / 1TB", "5000 mAh", "90W co day, 80W khong day", "Leica Summilux, chup dem va chan dung manh")},
    {"name": "OnePlus 13", "brand": "OnePlus", "sku": "OP13-005", "product_type": "phone", "category_slug": "android-cao-cap", "price": 22990000, "rating": 4.7, "review_count": 74, "featured": False, "description": "OnePlus 13 co Snapdragon 8 Elite, pin lon va sac nhanh. May phu hop nguoi can flagship hieu nang cao voi giao dien muot.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "256GB", "12GB", 22990000, 30, True), variant("Xanh", "512GB", "16GB", 26990000, 20), variant("Trang", "512GB", "16GB", 26990000, 14)], "specs": phone_specs("6.82 inch", "50MP wide + 50MP periscope + 50MP ultrawide", "Qualcomm Snapdragon 8 Elite", "12GB / 16GB", "256GB / 512GB", "6000 mAh", "100W co day, 50W khong day", "Hasselblad color, pin lon, sac nhanh")},
    {"name": "Vivo X200 Pro", "brand": "vivo", "sku": "VVX200P-006", "product_type": "phone", "category_slug": "android-cao-cap", "price": 24990000, "rating": 4.8, "review_count": 95, "featured": False, "description": "Vivo X200 Pro manh ve chup chan dung va zoom voi ong kinh Zeiss. Chip Dimensity 9400 cho hieu nang flagship va tiet kiem pin tot.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "512GB", "16GB", 24990000, 18, True), variant("Xanh", "512GB", "16GB", 24990000, 16), variant("Bac", "1TB", "16GB", 28990000, 6)], "specs": phone_specs("6.78 inch", "50MP wide + 200MP periscope + 50MP ultrawide", "MediaTek Dimensity 9400", "16GB", "512GB / 1TB", "6000 mAh", "90W co day", "Zeiss portrait, zoom xa, chong rung tot")},
    {"name": "iPhone 15", "brand": "Apple", "sku": "IP15-007", "product_type": "phone", "category_slug": "iphone", "price": 17990000, "rating": 4.7, "review_count": 420, "featured": True, "description": "iPhone 15 van la lua chon iOS can bang voi chip A16 Bionic, Dynamic Island va camera 48MP. Gia tot hon dong Pro nhung van du manh cho nhieu nam.", "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=900&q=80", "variants": [variant("Xanh", "128GB", "6GB", 17990000, 80, True), variant("Hong", "128GB", "6GB", 17990000, 62), variant("Den", "256GB", "6GB", 20990000, 40)], "specs": phone_specs("6.1 inch", "48MP wide + 12MP ultrawide", "Apple A16 Bionic", "6GB", "128GB / 256GB", "3349 mAh", "USB-C 20W", "Dynamic Island, camera 48MP, iOS on dinh")},
    {"name": "Samsung Galaxy A55", "brand": "Samsung", "sku": "SGA55-008", "product_type": "phone", "category_slug": "android-cao-cap", "price": 9490000, "rating": 4.6, "review_count": 330, "featured": False, "description": "Galaxy A55 co khung kim loai, man hinh Super AMOLED 120Hz va Exynos 1480. May khong co jack 3.5mm, doi lai co IP67 va phan mem on dinh.", "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=900&q=80", "variants": [variant("Xanh", "128GB", "8GB", 9490000, 85, True), variant("Tim", "256GB", "8GB", 10490000, 54), variant("Den", "256GB", "12GB", 11490000, 30)], "specs": phone_specs("6.6 inch", "50MP OIS + 12MP ultrawide + 5MP macro", "Samsung Exynos 1480", "8GB / 12GB", "128GB / 256GB", "5000 mAh", "25W", "IP67, khong co jack 3.5mm, man hinh dep")},
    {"name": "Redmi Note 13 Pro+", "brand": "Xiaomi", "sku": "RN13P-009", "product_type": "phone", "category_slug": "android-cao-cap", "price": 8990000, "rating": 4.6, "review_count": 280, "featured": False, "description": "Redmi Note 13 Pro+ noi bat trong tam trung voi camera 200MP va sac nhanh 120W. Day la lua chon gia tot cho nguoi can sac cuc nhanh.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "256GB", "8GB", 8990000, 75, True), variant("Trang", "256GB", "12GB", 9990000, 48), variant("Tim", "512GB", "12GB", 11490000, 22)], "specs": phone_specs("6.67 inch", "200MP OIS + 8MP ultrawide + 2MP macro", "MediaTek Dimensity 7200 Ultra", "8GB / 12GB", "256GB / 512GB", "5000 mAh", "120W HyperCharge", "Sac 120W rat nhanh, camera 200MP trong tam trung")},
    {"name": "OPPO Reno12 Pro", "brand": "OPPO", "sku": "OPR12P-010", "product_type": "phone", "category_slug": "android-cao-cap", "price": 13990000, "rating": 4.5, "review_count": 170, "featured": False, "description": "OPPO Reno12 Pro co thiet ke mong nhe, camera chan dung va cac tinh nang AI. Phu hop nguoi dung thich selfie, quay chup mang xa hoi.", "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=900&q=80", "variants": [variant("Bac", "256GB", "12GB", 13990000, 55, True), variant("Den", "512GB", "12GB", 15990000, 28)], "specs": phone_specs("6.7 inch", "50MP OIS + 50MP tele + 8MP ultrawide", "MediaTek Dimensity 7300 Energy", "12GB", "256GB / 512GB", "5000 mAh", "80W SUPERVOOC", "AI portrait, selfie dep, thiet ke mong")},
    {"name": "Realme GT 6T", "brand": "Realme", "sku": "RMGT6T-011", "product_type": "phone", "category_slug": "android-cao-cap", "price": 10990000, "rating": 4.6, "review_count": 130, "featured": False, "description": "Realme GT 6T tap trung vao hieu nang voi Snapdragon 7+ Gen 3 va man hinh rat sang. May hop voi nguoi can may nhanh trong tam gia tren 10 trieu.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Bac", "256GB", "8GB", 10990000, 48, True), variant("Xanh", "256GB", "12GB", 12490000, 32)], "specs": phone_specs("6.78 inch", "50MP OIS + 8MP ultrawide", "Qualcomm Snapdragon 7+ Gen 3", "8GB / 12GB", "256GB", "5500 mAh", "120W", "Hieu nang cao, man hinh sang, sac nhanh")},
    {"name": "vivo V40", "brand": "vivo", "sku": "VV40-012", "product_type": "phone", "category_slug": "android-cao-cap", "price": 11990000, "rating": 4.5, "review_count": 120, "featured": False, "description": "vivo V40 co thiet ke mong, pin lon va camera hop tac Zeiss. May phu hop nguoi can dien thoai dep, chup chan dung tot.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Tim", "256GB", "12GB", 11990000, 42, True), variant("Bac", "512GB", "12GB", 13990000, 20)], "specs": phone_specs("6.78 inch", "50MP OIS + 50MP ultrawide Zeiss", "Qualcomm Snapdragon 7 Gen 3", "12GB", "256GB / 512GB", "5500 mAh", "80W", "Zeiss portrait, pin lon trong than may mong")},
    {"name": "Nothing Phone 2a", "brand": "Nothing", "sku": "NP2A-013", "product_type": "phone", "category_slug": "android-cao-cap", "price": 8490000, "rating": 4.4, "review_count": 95, "featured": False, "description": "Nothing Phone 2a co thiet ke Glyph doc dao va phan mem nhe. Hieu nang vua du, phu hop nguoi muon may khac biet trong tam gia.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Trang", "128GB", "8GB", 8490000, 50, True), variant("Den", "256GB", "12GB", 9990000, 30)], "specs": phone_specs("6.7 inch", "50MP OIS + 50MP ultrawide", "MediaTek Dimensity 7200 Pro", "8GB / 12GB", "128GB / 256GB", "5000 mAh", "45W", "Glyph Interface, Android gan goc")},
    {"name": "Samsung Galaxy A35", "brand": "Samsung", "sku": "SGA35-014", "product_type": "phone", "category_slug": "android-cao-cap", "price": 7990000, "rating": 4.4, "review_count": 210, "featured": False, "description": "Galaxy A35 la lua chon tam trung de dung voi man hinh AMOLED va pin 5000mAh. May phu hop hoc tap, cong viec nhe va chup anh co ban.", "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=900&q=80", "variants": [variant("Xanh", "128GB", "8GB", 7990000, 75, True), variant("Den", "256GB", "8GB", 8990000, 50)], "specs": phone_specs("6.6 inch", "50MP OIS + 8MP ultrawide + 5MP macro", "Samsung Exynos 1380", "8GB", "128GB / 256GB", "5000 mAh", "25W", "Man hinh AMOLED, pin ben, hieu nang vua phai")},
    {"name": "Redmi 13C", "brand": "Xiaomi", "sku": "R13C-015", "product_type": "phone", "category_slug": "android-pho-thong", "price": 2990000, "rating": 4.2, "review_count": 260, "featured": False, "description": "Redmi 13C la may pho thong gia tot voi pin lon va man hinh lon. Chip khong manh, phu hop nghe goi, hoc online va ung dung co ban.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "128GB", "4GB", 2990000, 130, True), variant("Xanh", "128GB", "6GB", 3490000, 90)], "specs": phone_specs("6.74 inch", "50MP wide + camera phu", "MediaTek Helio G85", "4GB / 6GB", "128GB", "5000 mAh", "18W", "Gia re, pin lon, han che khi choi game nang")},
    {"name": "Samsung Galaxy A15", "brand": "Samsung", "sku": "SGA15-016", "product_type": "phone", "category_slug": "android-pho-thong", "price": 4490000, "rating": 4.3, "review_count": 300, "featured": False, "description": "Galaxy A15 co man hinh Super AMOLED va pin 5000mAh trong tam gia pho thong. May chay on cho nhu cau hang ngay nhung khong danh cho game nang.", "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=900&q=80", "variants": [variant("Den", "128GB", "8GB", 4490000, 100, True), variant("Xanh", "256GB", "8GB", 5490000, 65)], "specs": phone_specs("6.5 inch", "50MP wide + 5MP ultrawide + 2MP macro", "MediaTek Helio G99", "8GB", "128GB / 256GB", "5000 mAh", "25W", "AMOLED dep, pin tot, hieu nang co ban")},
    {"name": "OPPO A3x", "brand": "OPPO", "sku": "OPA3X-017", "product_type": "phone", "category_slug": "android-pho-thong", "price": 3490000, "rating": 4.2, "review_count": 145, "featured": False, "description": "OPPO A3x tap trung vao do ben, pin lon va thiet ke gon. Hieu nang chi phu hop tac vu co ban, khong phu hop game nang.", "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=900&q=80", "variants": [variant("Do", "64GB", "4GB", 3490000, 90, True), variant("Den", "128GB", "4GB", 3990000, 75)], "specs": phone_specs("6.67 inch", "8MP wide + camera phu", "Qualcomm Snapdragon 6s 4G Gen 1", "4GB", "64GB / 128GB", "5100 mAh", "45W", "Ben bi, sac nhanh trong phan khuc, camera co ban")},
    {"name": "Realme C65", "brand": "Realme", "sku": "RMC65-018", "product_type": "phone", "category_slug": "android-pho-thong", "price": 4290000, "rating": 4.3, "review_count": 180, "featured": False, "description": "Realme C65 co pin 5000mAh, sac 45W va man hinh 90Hz. May phu hop nguoi can pin khoe, giao dien de dung va gia thap.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Den", "128GB", "6GB", 4290000, 88, True), variant("Vang", "256GB", "8GB", 5290000, 55)], "specs": phone_specs("6.67 inch", "50MP wide + camera phu", "MediaTek Helio G85", "6GB / 8GB", "128GB / 256GB", "5000 mAh", "45W", "Pin lon bu cho chip pho thong")},
    {"name": "vivo Y28", "brand": "vivo", "sku": "VVY28-019", "product_type": "phone", "category_slug": "android-pho-thong", "price": 4990000, "rating": 4.3, "review_count": 155, "featured": False, "description": "vivo Y28 co pin 6000mAh rat ben, hop voi nguoi can dung lau. Camera va hieu nang o muc co ban, uu tien pin hon suc manh.", "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=900&q=80", "variants": [variant("Xanh", "128GB", "8GB", 4990000, 80, True), variant("Den", "256GB", "8GB", 5990000, 45)], "specs": phone_specs("6.68 inch", "50MP wide + 2MP depth", "MediaTek Helio G85", "8GB", "128GB / 256GB", "6000 mAh", "44W", "Pin 6000mAh, khong phu hop game nang")},
    {"name": "iPhone SE 2022", "brand": "Apple", "sku": "IPSE22-020", "product_type": "phone", "category_slug": "iphone", "price": 6990000, "rating": 4.3, "review_count": 390, "featured": False, "description": "iPhone SE 2022 la lua chon iOS gia re nhat voi chip A15 Bionic. Thiet ke cu, man hinh nho va pin khiem ton nhung hieu nang van tot.", "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=900&q=80", "variants": [variant("Den", "64GB", "4GB", 6990000, 45, True), variant("Trang", "128GB", "4GB", 8490000, 28), variant("Do", "128GB", "4GB", 8490000, 22)], "specs": phone_specs("4.7 inch", "12MP wide", "Apple A15 Bionic", "4GB", "64GB / 128GB", "2018 mAh", "20W, Qi wireless", "Touch ID, thiet ke cu, iOS gia re")},
]


LAPTOPS = [
    ("ASUS ROG Strix G16 (2024)", "ASUS", "ROG-G16-2024-001", "laptop-gaming", 35990000, 4.8, 115, True, "Intel Core i9-14900HX", "NVIDIA GeForce RTX 4070", "16 inch QHD+ 240Hz", "32GB DDR5 5600MHz", "1TB NVMe PCIe 4.0", "90Wh", "2.3kg", "Gaming manh, tan nhiet tot, phu hop AAA high setting.", [variant("Xam", "1TB", "32GB", 35990000, 15, True, "i9 / RTX 4070"), variant("Xam", "512GB", "16GB", 31990000, 20, False, "i9 / RTX 4070"), variant("Den", "1TB", "32GB", 45990000, 8, False, "i9 / RTX 4080")]),
    ("MSI Titan GT77", "MSI", "MSI-GT77-002", "laptop-gaming", 89990000, 4.9, 35, True, "Intel Core i9-14900HX", "NVIDIA GeForce RTX 4090", "17.3 inch Mini LED 4K 144Hz", "64GB DDR5", "2TB NVMe PCIe 4.0", "99Wh", "3.3kg", "Desktop replacement cuc manh, nang va gia cao.", [variant("Den", "2TB", "64GB", 89990000, 6, True, "i9 / RTX 4090"), variant("Den", "1TB", "32GB", 75990000, 9, False, "i9 / RTX 4080")]),
    ("Lenovo Legion 5 Pro", "Lenovo", "LEG5P-003", "laptop-gaming", 32990000, 4.7, 160, True, "AMD Ryzen 7 7735HS", "NVIDIA GeForce RTX 4060", "16 inch WQXGA 165Hz", "16GB DDR5", "1TB NVMe PCIe 4.0", "80Wh", "2.45kg", "Can bang gia va hieu nang, hop game thu pho thong.", [variant("Xam", "1TB", "16GB", 32990000, 25, True, "R7 / RTX 4060"), variant("Xam", "1TB", "32GB", 36990000, 12, False, "R7 / RTX 4070")]),
    ("Acer Predator Helios 16", "Acer", "PH16-004", "laptop-gaming", 41990000, 4.7, 92, False, "Intel Core i7-14700HX", "NVIDIA GeForce RTX 4070", "16 inch WQXGA 240Hz", "32GB DDR5", "1TB NVMe PCIe 4.0", "90Wh", "2.6kg", "Man hinh nhanh, GPU RTX 4070 du cho AAA high.", [variant("Den", "1TB", "32GB", 41990000, 13, True, "i7 / RTX 4070"), variant("Den", "512GB", "16GB", 35990000, 18, False, "i7 / RTX 4060")]),
    ("Dell Alienware m16", "Dell", "AWM16-005", "laptop-gaming", 62990000, 4.8, 45, False, "Intel Core i9-13900H", "NVIDIA GeForce RTX 4080", "16 inch QHD+ 240Hz", "32GB DDR5", "1TB NVMe PCIe 4.0", "86Wh", "3.25kg", "Thiet ke premium, hieu nang cao nhung nang.", [variant("Xam", "1TB", "32GB", 62990000, 8, True, "i9 / RTX 4080"), variant("Xam", "1TB", "16GB", 49990000, 10, False, "i7 / RTX 4070")]),
    ("HP OMEN 16", "HP", "OMEN16-006", "laptop-gaming", 34990000, 4.6, 120, False, "AMD Ryzen 7 7840HS", "NVIDIA GeForce RTX 4060", "16.1 inch QHD 165Hz", "16GB DDR5", "1TB NVMe PCIe 4.0", "83Wh", "2.35kg", "Gaming tot, thiet ke kin dao hon ROG.", [variant("Den", "1TB", "16GB", 34990000, 22, True, "R7 / RTX 4060"), variant("Den", "1TB", "32GB", 38990000, 12, False, "R7 / RTX 4070")]),
    ("MacBook Air M3 13 inch", "Apple", "MBA-M3-007", "macbook", 26990000, 4.8, 260, True, "Apple M3", "Apple M3 GPU (10-core)", "13.6 inch Liquid Retina", "8GB / 16GB unified memory", "256GB / 512GB SSD", "52.6Wh", "1.24kg", "Mong nhe, pin tot, khong danh cho game nang.", [variant("Bac", "256GB", "8GB", 26990000, 40, True, "8GB / 256GB"), variant("Xam", "512GB", "16GB", 34990000, 24, False, "16GB / 512GB")]),
    ("MacBook Pro 14 M3 Pro", "Apple", "MBP-M3P-008", "macbook", 52990000, 4.9, 150, True, "Apple M3 Pro", "Apple M3 Pro GPU (18-core)", "14.2 inch Liquid Retina XDR 120Hz", "18GB unified memory", "512GB / 1TB SSD", "72.4Wh", "1.61kg", "Tot cho lap trinh, do hoa va render nhe.", [variant("Bac", "512GB", "18GB", 52990000, 18, True, "18GB / 512GB"), variant("Xam", "1TB", "18GB", 60990000, 10, False, "18GB / 1TB")]),
    ("Dell XPS 15", "Dell", "XPS15-009", "laptop-van-phong", 44990000, 4.7, 82, False, "Intel Core Ultra 7 155H", "NVIDIA GeForce RTX 4050", "15.6 inch OLED cam ung", "16GB LPDDR5x", "1TB NVMe SSD", "86Wh", "1.92kg", "May sang tao noi dung, man OLED dep, khong phai gaming chuyen dung.", [variant("Bac", "1TB", "16GB", 44990000, 12, True, "Ultra 7 / RTX 4050"), variant("Bac", "1TB", "32GB", 52990000, 7, False, "Ultra 7 / RTX 4060")]),
    ("LG Gram 16", "LG", "LGG16-010", "laptop-van-phong", 32990000, 4.6, 95, False, "Intel Core Ultra 7 155H", "Intel Iris Xe Graphics", "16 inch WQXGA", "16GB LPDDR5x", "1TB NVMe SSD", "80Wh", "1.19kg", "Rat nhe cho man 16 inch, khong phu hop game nang.", [variant("Trang", "1TB", "16GB", 32990000, 20, True, "Ultra 7"), variant("Den", "512GB", "16GB", 28990000, 16, False, "Ultra 5")]),
    ("Asus Zenbook 14 OLED", "ASUS", "ZEN14-011", "laptop-van-phong", 24990000, 4.6, 170, False, "Intel Core Ultra 5 125H", "Intel Iris Xe Graphics", "14 inch OLED 2.8K", "16GB LPDDR5x", "512GB NVMe SSD", "75Wh", "1.2kg", "OLED dep, pin tot, phu hop van phong va hoc tap cao cap.", [variant("Xanh", "512GB", "16GB", 24990000, 35, True, "Ultra 5"), variant("Xam", "1TB", "16GB", 28990000, 20, False, "Ultra 7")]),
    ("HP Spectre x360 14", "HP", "SPX360-012", "laptop-van-phong", 39990000, 4.7, 65, False, "Intel Core Ultra 7 155H", "Intel Iris Xe Graphics", "14 inch OLED cam ung 2-in-1", "16GB LPDDR5x", "1TB NVMe SSD", "68Wh", "1.36kg", "2-in-1 cam ung, but stylus, hop hop hanh va sang tao nhe.", [variant("Den", "1TB", "16GB", 39990000, 14, True, "Ultra 7"), variant("Xanh", "512GB", "16GB", 34990000, 12, False, "Ultra 5")]),
    ("Acer Aspire 5", "Acer", "ASP5-013", "laptop-sinh-vien", 11990000, 4.3, 240, False, "Intel Core i5-1235U", "Intel Iris Xe Graphics", "15.6 inch FHD IPS", "8GB DDR4", "512GB NVMe SSD", "50Wh", "1.7kg", "Van phong hoc tap tot, khong chay duoc game nang.", [variant("Bac", "512GB", "8GB", 11990000, 70, True, "i5"), variant("Xam", "512GB", "16GB", 13990000, 45, False, "i5")]),
    ("Lenovo IdeaPad Slim 5", "Lenovo", "IPS5-014", "laptop-sinh-vien", 14990000, 4.4, 210, False, "AMD Ryzen 5 7530U", "AMD Radeon 780M (iGPU)", "14 inch WUXGA IPS", "16GB LPDDR4x", "512GB NVMe SSD", "56Wh", "1.46kg", "Mong nhe, pin on, cho hoc tap va van phong.", [variant("Xam", "512GB", "16GB", 14990000, 60, True, "R5"), variant("Xanh", "1TB", "16GB", 16990000, 24, False, "R7")]),
    ("HP 15s", "HP", "HP15S-015", "laptop-sinh-vien", 10990000, 4.2, 190, False, "Intel Core i3-1215U", "Intel Iris Xe Graphics", "15.6 inch FHD", "8GB DDR4", "512GB NVMe SSD", "41Wh", "1.69kg", "Gia re, phu hop Office va hoc online, han che ve game.", [variant("Bac", "512GB", "8GB", 10990000, 80, True, "i3"), variant("Bac", "512GB", "16GB", 12990000, 35, False, "i5")]),
    ("ASUS VivoBook 15", "ASUS", "VIVO15-016", "laptop-sinh-vien", 12990000, 4.4, 230, False, "Intel Core i5-1235U", "Intel Iris Xe Graphics", "15.6 inch FHD OLED tuy cau hinh", "8GB / 16GB DDR4", "512GB NVMe SSD", "42Wh", "1.7kg", "Gia tot, ban phim so tien loi, game nang khong phu hop.", [variant("Bac", "512GB", "8GB", 12990000, 68, True, "i5"), variant("Den", "512GB", "16GB", 14990000, 40, False, "i5")]),
    ("Dell Inspiron 15", "Dell", "INS15-017", "laptop-sinh-vien", 13990000, 4.3, 180, False, "AMD Ryzen 5 5500U", "AMD Radeon 780M (iGPU)", "15.6 inch FHD", "8GB DDR4", "512GB NVMe SSD", "54Wh", "1.83kg", "Ben, de bao tri, phu hop sinh vien va van phong.", [variant("Bac", "512GB", "8GB", 13990000, 55, True, "R5"), variant("Den", "1TB", "16GB", 16990000, 30, False, "R7")]),
    ("MSI Modern 14", "MSI", "MOD14-018", "laptop-sinh-vien", 12490000, 4.3, 150, False, "Intel Core i5-1235U", "Intel Iris Xe Graphics", "14 inch FHD IPS", "8GB DDR4", "512GB NVMe SSD", "39Wh", "1.4kg", "Nhe, gia tot, hop hoc tap va di chuyen nhieu.", [variant("Xam", "512GB", "8GB", 12490000, 58, True, "i5"), variant("Den", "512GB", "16GB", 14490000, 26, False, "i5")]),
]


for idx, item in enumerate(LAPTOPS, start=21):
    name, brand, sku, cat, price, rating, reviews, featured, cpu, gpu, display, ram, storage, battery, weight, note, variants = item
    PRODUCTS.append({
        "name": name,
        "brand": brand,
        "sku": sku,
        "product_type": "laptop",
        "category_slug": cat,
        "price": price,
        "rating": rating,
        "review_count": reviews,
        "featured": featured,
        "description": f"{name} la laptop phu hop thi truong Viet Nam 2024-2025. {note} Cau hinh {cpu} va {gpu} giup chatbot doi chieu benchmark khi tu van gaming.",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=900&q=80",
        "variants": variants,
        "specs": laptop_specs(display, cpu, gpu, ram, storage, battery, weight, note),
    })


AUDIO = [
    ("Sony WH-1000XM5", "Sony", "SNY-WHXM5-039", "tai-nghe-chong-on", 7490000, 4.8, 280, True, "30mm V1 custom", "ANC hang dau, 8 mic xu ly nhieu", "LDAC, AAC, SBC", "Bluetooth 5.2", "30 gio ANC, 40 gio tat ANC", "250g", "Gap gon de di chuyen, multipoint", ["Den", "Bac", "Kem"]),
    ("Bose QuietComfort 45", "Bose", "BOSE-QC45-040", "tai-nghe-chong-on", 5990000, 4.6, 220, False, "40mm dynamic", "ANC on dinh, che do Aware", "AAC, SBC", "Bluetooth 5.1", "24 gio", "240g", "De deo lau, am chat am", ["Den", "Trang"]),
    ("Apple AirPods Max", "Apple", "APM-041", "tai-nghe-chong-on", 12990000, 4.7, 180, True, "Apple dynamic driver", "ANC tot, Transparency tu nhien", "AAC", "Bluetooth 5.0", "20 gio", "384g", "Spatial Audio, chip H1", ["Bac", "Xam", "Xanh"]),
    ("Sennheiser Momentum 4", "Sennheiser", "SEN-MOM4-042", "tai-nghe-chong-on", 6990000, 4.7, 160, False, "42mm transducer", "Adaptive ANC", "aptX Adaptive, AAC, SBC", "Bluetooth 5.2", "60 gio", "293g", "Pin rat dai, am chat chi tiet", ["Den", "Trang"]),
    ("Apple AirPods Pro 2", "Apple", "APP2-043", "tai-nghe-tws", 5290000, 4.8, 430, True, "Apple high-excursion driver", "ANC chu dong, Adaptive Audio", "AAC", "Bluetooth 5.3", "6 gio tai nghe, 30 gio kem hop", "5.3g moi ben", "MagSafe case, Find My", ["Trang", "Den"]),
    ("Samsung Galaxy Buds3 Pro", "Samsung", "BUDS3P-044", "tai-nghe-tws", 4990000, 4.6, 190, False, "2-way dynamic", "Adaptive ANC", "SSC Hi-Fi, AAC, SBC", "Bluetooth 5.4", "6 gio ANC, 26 gio kem hop", "5.4g moi ben", "Galaxy AI, IP57", ["Bac", "Trang"]),
    ("Sony WF-1000XM5", "Sony", "SNY-WFXM5-045", "tai-nghe-tws", 5790000, 4.7, 210, False, "Dynamic Driver X", "ANC cao cap trong TWS", "LDAC, AAC, SBC", "Bluetooth 5.3", "8 gio ANC, 24 gio kem hop", "5.9g moi ben", "Nho gon, mic tot", ["Den", "Bac"]),
    ("Jabra Elite 10", "Jabra", "JAB-E10-046", "tai-nghe-tws", 4990000, 4.5, 120, False, "10mm dynamic", "Advanced ANC", "AAC, SBC", "Bluetooth 5.3", "6 gio ANC, 27 gio kem hop", "5.7g moi ben", "Dolby Head Tracking, IP57", ["Den", "Kem"]),
    ("SteelSeries Arctis Nova Pro", "SteelSeries", "SS-NOVAP-047", "tai-nghe-gaming", 7990000, 4.8, 95, False, "40mm high fidelity", "ANC hybrid", "LC3, SBC", "Wireless base station", "Pin kep thay nong", "337g", "GameDAC, chatmix, mic ClearCast", ["Den", "Trang"]),
    ("HyperX Cloud Alpha", "HyperX", "HX-CA-048", "tai-nghe-gaming", 2290000, 4.6, 260, False, "50mm dual chamber", "Cach am thu dong", "Co day 3.5mm", "Co day", "Khong dung pin", "336g", "Ben, mic roi, am bass tot", ["Den", "Do"]),
    ("Logitech G Pro X 2", "Logitech", "LOG-GPX2-049", "tai-nghe-gaming", 4990000, 4.7, 150, False, "Graphene 50mm", "Cach am thu dong", "LIGHTSPEED, Bluetooth, 3.5mm", "LIGHTSPEED 2.4GHz", "50 gio", "345g", "Mic Blue VO!CE, do tre thap", ["Den", "Trang"]),
    ("Razer BlackShark V2 Pro", "Razer", "RZ-BSV2P-050", "tai-nghe-gaming", 4590000, 4.6, 175, False, "TriForce Titanium 50mm", "Cach am thu dong", "Razer HyperSpeed", "2.4GHz / Bluetooth", "70 gio", "320g", "Mic HyperClear, eSports EQ", ["Den", "Trang"]),
]


for item in AUDIO:
    name, brand, sku, cat, price, rating, reviews, featured, driver, anc, codec, bt, battery, weight, extra, colors = item
    PRODUCTS.append({
        "name": name,
        "brand": brand,
        "sku": sku,
        "product_type": "audio",
        "category_slug": cat,
        "price": price,
        "rating": rating,
        "review_count": reviews,
        "featured": featured,
        "description": f"{name} la tai nghe {brand} phu hop nhu cau nghe nhac, lam viec va giai tri. San pham co {anc.lower()} va ket noi {bt}.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900&q=80",
        "variants": [variant(color, None, None, price, 35 - idx * 4, idx == 0) for idx, color in enumerate(colors[:4])],
        "specs": audio_specs(driver, anc, codec, bt, battery, weight, extra),
    })


ACCESSORIES = [
    ("Anker 737 Power Bank (24,000mAh)", "Anker", "ANK-737-051", "sac-pin-du-phong", 1890000, 4.8, 240, True, "Sac du phong", "24,000mAh, man hinh hien thi pin", "2x USB-C + 1x USB-A", "140W USB-C in/out", "Hop laptop USB-C, di cong tac"),
    ("Baseus 20000mAh 65W", "Baseus", "BAS-PB65-052", "sac-pin-du-phong", 1190000, 4.5, 210, False, "Sac du phong", "20,000mAh, sac nhanh laptop mong nhe", "USB-C + USB-A", "65W USB-C", "Gia tot, dung hang ngay"),
    ("Xiaomi 33W 20000mAh Power Bank", "Xiaomi", "XMI-PB33-053", "sac-pin-du-phong", 790000, 4.4, 300, False, "Sac du phong", "20,000mAh, ho tro sac nhanh dien thoai", "USB-C + 2x USB-A", "33W", "Phu hop smartphone va tablet"),
    ("Anker GaN 65W", "Anker", "ANK-GAN65-054", "sac-pin-du-phong", 890000, 4.7, 260, False, "Sac nhanh GaN", "Nho gon, hieu suat cao", "2x USB-C + USB-A", "65W", "Sac laptop mong, dien thoai va tablet"),
    ("Baseus GaN 100W", "Baseus", "BAS-GAN100-055", "sac-pin-du-phong", 1290000, 4.6, 180, False, "Sac nhanh GaN", "Cong suat cao cho laptop", "2x USB-C + 2x USB-A", "100W", "Co the sac nhieu thiet bi cung luc"),
    ("Ugreen Nexode 65W", "Ugreen", "UGR-GAN65-056", "sac-pin-du-phong", 990000, 4.6, 170, False, "Sac nhanh GaN", "Ho tro PD/PPS", "2x USB-C + USB-A", "65W", "On dinh, bao ve qua nhiet"),
    ("Ugreen USB-C Hub 7-in-1", "Ugreen", "UGR-HUB7-057", "hub-adapter", 890000, 4.5, 150, False, "Hub USB-C", "HDMI 4K, USB 3.0, SD/TF", "USB-C, HDMI, USB-A, SD, TF, PD", "PD pass-through 100W", "Mo rong cong cho MacBook/laptop"),
    ("Spigen Ultra Hybrid iPhone 16 Pro", "Spigen", "SPG-IP16P-058", "op-lung-bao-ve", 590000, 4.6, 140, False, "Op lung", "Chong soc Air Cushion", "iPhone 16 Pro", "Khong dung nguon", "Trong suot, ho tro MagSafe"),
    ("Samsung S25 Ultra Standing Grip Case", "Samsung", "SSG-S25U-059", "op-lung-bao-ve", 790000, 4.5, 95, False, "Op lung", "Grip dung may, bao ve camera", "Galaxy S25 Ultra", "Khong dung nguon", "Hop S Pen, cam chac tay"),
    ("Logitech G502 X Plus", "Logitech", "LOG-G502XP-060", "chuot-gaming", 3290000, 4.8, 220, True, "Chuot gaming", "LIGHTFORCE switch, HERO 25K", "LIGHTSPEED wireless, USB-C", "Pin sac USB-C", "RGB, nhieu nut, hop FPS/MOBA"),
]


for item in ACCESSORIES:
    name, brand, sku, cat, price, rating, reviews, featured, kind, main, ports, power, extra = item
    PRODUCTS.append({
        "name": name,
        "brand": brand,
        "sku": sku,
        "product_type": "accessory",
        "category_slug": cat,
        "price": price,
        "rating": rating,
        "review_count": reviews,
        "featured": featured,
        "description": f"{name} la phu kien {brand} phu hop nguoi dung cong nghe tai Viet Nam. San pham tap trung vao tinh on dinh, do ben va gia tri su dung hang ngay.",
        "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761?w=900&q=80",
        "variants": [variant("Den", None, None, price, 55, True), variant("Xanh", None, None, price, 30)],
        "specs": accessory_specs(kind, main, ports, power, extra),
    })


def upsert_category(db, data: dict) -> Category:
    category = db.query(Category).filter(Category.slug == data["slug"]).first()
    if not category:
        category = Category(id=gen_id(), slug=data["slug"])
        db.add(category)
    category.name = data["name"]
    category.description = data["description"]
    category.parent_id = data.get("parent_id")
    category.level = data["level"]
    category.path = data["path"]
    db.flush()
    return category


def create_categories(db) -> dict[str, Category]:
    cats: dict[str, Category] = {}
    for name, slug, description, parent_slug in CATEGORIES:
        parent = cats.get(parent_slug) if parent_slug else None
        level = 1 if parent else 0
        path = f"{parent.path}/{slug}" if parent else slug
        cats[slug] = upsert_category(db, {
            "name": name,
            "slug": slug,
            "description": description,
            "parent_id": parent.id if parent else None,
            "level": level,
            "path": path,
        })
    db.commit()
    return cats


def upsert_benchmark(db, model, name: str, aliases: str, score: int):
    item = db.query(model).filter(model.name == name).first()
    if not item:
        item = model(id=gen_id(), name=name)
        db.add(item)
    item.aliases = aliases
    item.score = score
    return item


def create_cpu_benchmarks(db) -> None:
    for name, score, aliases in CPU_BENCHMARKS:
        upsert_benchmark(db, CpuBenchmark, name, aliases, score)
    db.commit()


def create_gpu_benchmarks(db) -> None:
    for name, score, aliases in GPU_BENCHMARKS:
        upsert_benchmark(db, GpuBenchmark, name, aliases, score)
    db.commit()


def create_game_requirements(db) -> None:
    for row in GAME_REQUIREMENTS:
        (
            game_name,
            aliases,
            min_gpu,
            rec_gpu,
            ultra_gpu,
            min_cpu,
            rec_cpu,
            ultra_cpu,
            min_ram,
            rec_ram,
            ultra_ram,
        ) = row
        game = db.query(GameRequirement).filter(GameRequirement.game_name == game_name).first()
        if not game:
            game = GameRequirement(id=gen_id(), game_name=game_name)
            db.add(game)
        game.aliases = aliases
        game.min_gpu_score = min_gpu
        game.recommended_gpu_score = rec_gpu
        game.ultra_gpu_score = ultra_gpu
        game.min_cpu_score = min_cpu
        game.recommended_cpu_score = rec_cpu
        game.ultra_cpu_score = ultra_cpu
        game.min_ram_gb = min_ram
        game.recommended_ram_gb = rec_ram
        game.ultra_ram_gb = ultra_ram
    db.commit()


def upsert_product(db, data: dict, cats: dict[str, Category]) -> Product:
    product = db.query(Product).filter(Product.sku == data["sku"]).first()
    if not product:
        product = Product(id=gen_id(), sku=data["sku"])
        db.add(product)

    product.name = data["name"]
    product.description = data["description"]
    product.price = data["price"]
    product.stock = sum(v["stock"] for v in data["variants"])
    product.category_id = cats[data["category_slug"]].id
    product.image_url = data["image_url"]
    product.brand = data["brand"]
    product.product_type = data["product_type"]
    product.rating = data["rating"]
    product.review_count = data["review_count"]
    product.featured = data["featured"]
    product.status = "active"
    db.flush()
    return product


def upsert_variants(db, product: Product, product_sku: str, variants: list[dict]) -> None:
    seen = set()
    for idx, data in enumerate(variants, start=1):
        sku = f"{product_sku}-V{idx:02d}"
        seen.add(sku)
        item = db.query(ProductVariant).filter(ProductVariant.sku == sku).first()
        if not item:
            item = ProductVariant(id=gen_id(), sku=sku, product_id=product.id)
            db.add(item)
        item.product_id = product.id
        item.color_name = data.get("color_name")
        item.color_code = data.get("color_code")
        item.version_name = data.get("version_name")
        item.ram = data.get("ram")
        item.storage = data.get("storage")
        item.price = data["price"]
        item.compare_price = data["compare_price"]
        item.stock = data["stock"]
        item.image_url = product.image_url
        item.is_default = bool(data.get("is_default"))
        item.status = "active"
    for stale in db.query(ProductVariant).filter(ProductVariant.product_id == product.id).all():
        if stale.sku not in seen:
            db.delete(stale)
    db.flush()


def replace_specs(db, product: Product, specs: list[tuple[str, str, str, int]]) -> None:
    db.query(ProductSpecification).filter(ProductSpecification.product_id == product.id).delete()
    for group_name, spec_key, spec_value, display_order in specs:
        db.add(ProductSpecification(
            id=gen_id(),
            product_id=product.id,
            group_name=group_name,
            spec_key=spec_key,
            spec_value=spec_value,
            display_order=display_order,
        ))
    db.flush()


def create_product_group(db, cats: dict[str, Category], product_type: str) -> list[Product]:
    products = []
    for data in [p for p in PRODUCTS if p["product_type"] == product_type]:
        product = upsert_product(db, data, cats)
        upsert_variants(db, product, data["sku"], data["variants"])
        replace_specs(db, product, data["specs"])
        products.append(product)
    db.commit()
    return products


def create_smartphones(db, cats: dict[str, Category]) -> list[Product]:
    return create_product_group(db, cats, "phone")


def create_laptops(db, cats: dict[str, Category]) -> list[Product]:
    return create_product_group(db, cats, "laptop")


def create_audio_products(db, cats: dict[str, Category]) -> list[Product]:
    return create_product_group(db, cats, "audio")


def create_accessories(db, cats: dict[str, Category]) -> list[Product]:
    return create_product_group(db, cats, "accessory")


def create_related_products(db, all_products: list[Product]) -> None:
    by_type: dict[str, list[Product]] = {}
    for product in all_products:
        by_type.setdefault(product.product_type or "other", []).append(product)

    for group in by_type.values():
        group = sorted(group, key=lambda p: p.sku or "")
        for index, product in enumerate(group):
            db.query(RelatedProduct).filter(RelatedProduct.product_id == product.id).delete()
            candidates = [group[(index + offset) % len(group)] for offset in (1, 2, 3) if len(group) > offset]
            for related in candidates[:3]:
                if related.id == product.id:
                    continue
                db.add(RelatedProduct(id=gen_id(), product_id=product.id, related_product_id=related.id))
    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Creating categories...")
        cats = create_categories(db)
        print(f"  -> {len(cats)} categories")

        print("Creating benchmarks...")
        create_cpu_benchmarks(db)
        create_gpu_benchmarks(db)
        create_game_requirements(db)
        print("  -> benchmarks done")

        print("Creating smartphones...")
        phones = create_smartphones(db, cats)
        print(f"  -> {len(phones)} products")

        print("Creating laptops...")
        laptops = create_laptops(db, cats)
        print(f"  -> {len(laptops)} products")

        print("Creating audio products...")
        audios = create_audio_products(db, cats)
        print(f"  -> {len(audios)} products")

        print("Creating accessories...")
        accs = create_accessories(db, cats)
        print(f"  -> {len(accs)} products")

        print("Creating related products...")
        all_products = phones + laptops + audios + accs
        create_related_products(db, all_products)
        print("  -> related products done")

        print("\n=== SEED COMPLETE ===")
        print(f"Total products: {len(all_products)}")
    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
