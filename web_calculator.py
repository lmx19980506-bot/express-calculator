from flask import Flask, render_template, request

app = Flask(__name__)

# ==============================
# 顺丰价格表（上海市始发陆运包裹）
# 来源：2025年7月官方PDF + 账单验证
# ==============================

SF_PRICE_TABLE = {
    "同省": [
        {"first": 1, "max": 3, "base": 10, "unit": 2},
        {"first": 3, "max": 20, "base": 14, "unit": 2},
        {"first": 20, "max": float('inf'), "base": 48, "unit": 3}
    ],
    "云南省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 15, "base": 26, "unit": 5},
        {"first": 15, "max": float('inf'), "base": 86, "unit": 6.5}
    ],
    "内蒙古自治区": [
        {"first": 1, "max": 3, "base": 13, "unit": 6},
        {"first": 3, "max": 15, "base": 25, "unit": 6},
        {"first": 15, "max": float('inf'), "base": 97, "unit": 7}
    ],
    "北京市": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "天津市": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "吉林省": [
        {"first": 1, "max": 3, "base": 15, "unit": 6.5},
        {"first": 3, "max": 15, "base": 28, "unit": 6},
        {"first": 15, "max": float('inf'), "base": 100, "unit": 7.5}
    ],
    "四川省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 20, "base": 26, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 111, "unit": 6.5}
    ],
    "宁夏回族自治区": [
        {"first": 1, "max": 3, "base": 13, "unit": 5.5},
        {"first": 3, "max": 20, "base": 24, "unit": 6},
        {"first": 20, "max": float('inf'), "base": 126, "unit": 7}
    ],
    "安徽省": [
        {"first": 1, "max": 3, "base": 11, "unit": 2},
        {"first": 3, "max": 20, "base": 15, "unit": 2},
        {"first": 20, "max": float('inf'), "base": 49, "unit": 3}
    ],
    "山东省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "山西省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5},
        {"first": 3, "max": 20, "base": 25, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 93, "unit": 5}
    ],
    "广东省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 108, "unit": 6.5}
    ],
    "广西壮族自治区": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 20, "base": 26, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 111, "unit": 6.5}
    ],
    "新疆维吾尔自治区": [
        {"first": 1, "max": 3, "base": 19, "unit": 10},
        {"first": 3, "max": 20, "base": 39, "unit": 10},
        {"first": 20, "max": float('inf'), "base": 209, "unit": 12}
    ],
    "江苏省": [
        {"first": 1, "max": 3, "base": 11, "unit": 2},
        {"first": 3, "max": 20, "base": 15, "unit": 2},
        {"first": 20, "max": float('inf'), "base": 49, "unit": 3}
    ],
    "江西省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "河北省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "河南省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "浙江省": [
        {"first": 1, "max": 3, "base": 11, "unit": 2},
        {"first": 3, "max": 20, "base": 15, "unit": 2},
        {"first": 20, "max": float('inf'), "base": 49, "unit": 3}
    ],
    "海南省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 20, "base": 26, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 111, "unit": 6.5}
    ],
    "湖北省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "湖南省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 91, "unit": 5}
    ],
    "甘肃省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 4.5},
        {"first": 20, "max": float('inf'), "base": 99.5, "unit": 6}
    ],
    "福建省": [
        {"first": 1, "max": 3, "base": 13, "unit": 5},
        {"first": 3, "max": 20, "base": 23, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 108, "unit": 6.5}
    ],
    "贵州省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 20, "base": 26, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 111, "unit": 6.5}
    ],
    "辽宁省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 20, "base": 26, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 111, "unit": 6.5}
    ],
    "重庆市": [
        {"first": 1, "max": 3, "base": 15, "unit": 5.5},
        {"first": 3, "max": 20, "base": 26, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 111, "unit": 6.5}
    ],
    "陕西省": [
        {"first": 1, "max": 3, "base": 15, "unit": 5},
        {"first": 3, "max": 20, "base": 25, "unit": 4},
        {"first": 20, "max": float('inf'), "base": 93, "unit": 5}
    ],
    "青海省": [
        {"first": 1, "max": 3, "base": 14, "unit": 5.5},
        {"first": 3, "max": 20, "base": 25, "unit": 5},
        {"first": 20, "max": float('inf'), "base": 110, "unit": 6.5}
    ],
    "黑龙江省": [
        {"first": 1, "max": 3, "base": 15, "unit": 7},
        {"first": 3, "max": 15, "base": 29, "unit": 6},
        {"first": 15, "max": float('inf'), "base": 101, "unit": 7}
    ]
}

def calculate_sf(weight, province):
    key = "同省" if province == "上海市" else province
    if key not in SF_PRICE_TABLE:
        return None

    tiers = SF_PRICE_TABLE[key]
    for tier in tiers:
        if weight <= tier["max"]:
            cost = tier["base"] + (weight - tier["first"]) * tier["unit"]
            return round(cost)
    return None


# ==============================
# 申通快递（第五区修正）
# ==============================

STO_FIFTH_ZONE_PRICES = {
    "内蒙古自治区": 6,
    "甘肃省": 6,
    "海南省": 6,
    "宁夏回族自治区": 6,
    "青海省": 6,
    "新疆维吾尔自治区": 13,
    "西藏自治区": 13
}

def calculate_sto(weight, province):
    unit_price = STO_FIFTH_ZONE_PRICES.get(province, 5)  # 默认5元/kg
    handling_fee = 0.5 if province in ["北京市", "上海市"] else 0
    total = weight * unit_price + handling_fee
    return round(total, 2)


# ==============================
# 中通快递（仅北京上海收0.5元面单费）
# ==============================

def calculate_zto(weight, province):
    base_price_per_kg = 5  # 可根据实际调整
    handling_fee = 0.5 if province in ["北京市", "上海市"] else 0
    total = weight * base_price_per_kg + handling_fee
    return round(total, 2)


# ==============================
# 省份按地理大区排序
# ==============================

PROVINCE_ORDER = [
    # 华东
    "上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省",
    # 华北
    "北京市", "天津市", "河北省", "山西省", "内蒙古自治区",
    # 华南
    "广东省", "广西壮族自治区", "海南省",
    # 华中
    "河南省", "湖北省", "湖南省",
    # 西南
    "重庆市", "四川省", "贵州省", "云南省", "西藏自治区",
    # 西北
    "陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区",
    # 东北
    "辽宁省", "吉林省", "黑龙江省"
]


# ==============================
# Flask 路由
# ==============================

@app.route("/")
def index():
    return render_template("index.html", provinces=PROVINCE_ORDER)

@app.route("/calculate", methods=["POST"])
def calculate():
    courier = request.form["courier"]
    weight = float(request.form["weight"])
    province = request.form["province"]

    result = None
    if courier == "顺丰":
        result = calculate_sf(weight, province)
    elif courier == "申通":
        result = calculate_sto(weight, province)
    elif courier == "中通":
        result = calculate_zto(weight, province)

    return render_template(
        "index.html",
        provinces=PROVINCE_ORDER,
        courier=courier,
        weight=weight,
        province=province,
        result=result
    )

if __name__ == "__main__":
    app.run(debug=True)
