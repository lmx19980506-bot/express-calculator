from flask import Flask, render_template, request
import math

app = Flask(__name__)

# ==============================
# 顺丰快递计费逻辑（2025年7月 上海始发 陆运包裹）
# 来源：《陆运包裹-42430747-1753929218304.pdf》
# ==============================
def calculate_sf(weight, province):
    """
    严格按顺丰官方PDF实现，仅支持陆运包裹，上海市始发。
    西藏自治区未在PDF中列出，默认按新疆标准处理。
    运费四舍五入取整数。
    """
    # 同城（上海市）
    if province == "上海市":
        if weight <= 1:
            base, unit, first_w = 10, 2, 1
        elif weight <= 3:
            base, unit, first_w = 14, 2, 3
        elif weight <= 20:
            base, unit, first_w = 48, 3, 20
        else:
            base, unit, first_w = 48 + (weight - 20) * 3, 0, weight  # >20kg 统一计算
            return round(base)
    # 其他省份
    elif province == "云南省":
        if weight <= 1:
            base, unit, first_w = 15, 5.5, 1
        elif weight <= 3:
            base, unit, first_w = 26, 5, 3
        elif weight <= 15:
            base, unit, first_w = 86, 6.5, 15
        else:
            base, unit, first_w = 86 + (weight - 15) * 6.5, 0, weight
            return round(base)
    elif province == "内蒙古自治区":
        if weight <= 1:
            base, unit, first_w = 13, 5, 1
        elif weight <= 3:
            base, unit, first_w = 23, 4.5, 3
        elif weight <= 20:
            base, unit, first_w = 99.5, 6, 20
        else:
            base, unit, first_w = 99.5 + (weight - 20) * 6, 0, weight
            return round(base)
    elif province in ["北京市", "天津市", "山东省", "河南省", "河北省", "湖北省", "湖南省", "江西省"]:
        if weight <= 1:
            base, unit, first_w = 13, 5, 1
        elif weight <= 3:
            base, unit, first_w = 23, 4, 3
        elif weight <= 20:
            base, unit, first_w = 91, 5, 20
        else:
            base, unit, first_w = 91 + (weight - 20) * 5, 0, weight
            return round(base)
    elif province == "吉林省":
        if weight <= 1:
            base, unit, first_w = 15, 6.5, 1
        elif weight <= 3:
            base, unit, first_w = 28, 6, 3
        elif weight <= 15:
            base, unit, first_w = 100, 7.5, 15
        else:
            base, unit, first_w = 100 + (weight - 15) * 7.5, 0, weight
            return round(base)
    elif province in ["四川省", "广西壮族自治区", "海南省", "贵州省", "辽宁省", "重庆市"]:
        if weight <= 1:
            base, unit, first_w = 15, 5.5, 1
        elif weight <= 3:
            base, unit, first_w = 26, 5, 3
        elif weight <= 20:
            base, unit, first_w = 111, 6.5, 20
        else:
            base, unit, first_w = 111 + (weight - 20) * 6.5, 0, weight
            return round(base)
    elif province in ["安徽省", "江苏省", "浙江省"]:
        if weight <= 1:
            base, unit, first_w = 11, 2, 1
        elif weight <= 3:
            base, unit, first_w = 15, 2, 3
        elif weight <= 20:
            base, unit, first_w = 49, 3, 20
        else:
            base, unit, first_w = 49 + (weight - 20) * 3, 0, weight
            return round(base)
    elif province == "山西省":
        if weight <= 1:
            base, unit, first_w = 15, 5, 1
        elif weight <= 3:
            base, unit, first_w = 25, 4, 3
        elif weight <= 20:
            base, unit, first_w = 93, 5, 20
        else:
            base, unit, first_w = 93 + (weight - 20) * 5, 0, weight
            return round(base)
    elif province in ["广东省", "福建省"]:
        if weight <= 1:
            base, unit, first_w = 13, 5, 1
        elif weight <= 3:
            base, unit, first_w = 23, 5, 3
        elif weight <= 20:
            base, unit, first_w = 108, 6.5, 20
        else:
            base, unit, first_w = 108 + (weight - 20) * 6.5, 0, weight
            return round(base)
    elif province == "宁夏回族自治区":
        if weight <= 1:
            base, unit, first_w = 13, 5.5, 1
        elif weight <= 3:
            base, unit, first_w = 24, 6, 3
        elif weight <= 20:
            base, unit, first_w = 126, 7, 20
        else:
            base, unit, first_w = 126 + (weight - 20) * 7, 0, weight
            return round(base)
    elif province == "甘肃省":
        if weight <= 1:
            base, unit, first_w = 13, 5, 1
        elif weight <= 3:
            base, unit, first_w = 23, 4.5, 3
        elif weight <= 20:
            base, unit, first_w = 99.5, 6, 20
        else:
            base, unit, first_w = 99.5 + (weight - 20) * 6, 0, weight
            return round(base)
    elif province == "陕西省":
        if weight <= 1:
            base, unit, first_w = 15, 5, 1
        elif weight <= 3:
            base, unit, first_w = 25, 4, 3
        elif weight <= 20:
            base, unit, first_w = 93, 5, 20
        else:
            base, unit, first_w = 93 + (weight - 20) * 5, 0, weight
            return round(base)
    elif province == "青海省":
        if weight <= 1:
            base, unit, first_w = 14, 5.5, 1
        elif weight <= 3:
            base, unit, first_w = 25, 5, 3
        elif weight <= 20:
            base, unit, first_w = 110, 6.5, 20
        else:
            base, unit, first_w = 110 + (weight - 20) * 6.5, 0, weight
            return round(base)
    elif province == "新疆维吾尔自治区":
        if weight <= 1:
            base, unit, first_w = 19, 10, 1
        elif weight <= 3:
            base, unit, first_w = 39, 10, 3
        elif weight <= 20:
            base, unit, first_w = 209, 12, 20
        else:
            base, unit, first_w = 209 + (weight - 20) * 12, 0, weight
            return round(base)
    elif province == "黑龙江省":
        if weight <= 1:
            base, unit, first_w = 15, 7, 1
        elif weight <= 3:
            base, unit, first_w = 29, 6, 3
        elif weight <= 15:
            base, unit, first_w = 101, 7, 15
        else:
            base, unit, first_w = 101 + (weight - 15) * 7, 0, weight
            return round(base)
    else:
        # 西藏自治区、台湾、港澳等未列出地区 → 按新疆处理（最保守）
        if weight <= 1:
            base, unit, first_w = 19, 10, 1
        elif weight <= 3:
            base, unit, first_w = 39, 10, 3
        elif weight <= 20:
            base, unit, first_w = 209, 12, 20
        else:
            base, unit, first_w = 209 + (weight - 20) * 12, 0, weight
            return round(base)

    # 标准区间计算
    if weight <= first_w:
        cost = base
    else:
        cost = base + (weight - first_w) * unit
    return round(cost)


# ==============================
# 申通快递计费逻辑（保持不变）
# ==============================
COURIER_REGIONS_STO = {
    "one": ["上海市", "江苏省", "浙江省", "安徽省"],
    "two": ["北京市", "天津市", "河北省", "河南省", "山东省", "湖北省", "湖南省",
            "江西省", "广东省", "福建省"],
    "three": ["陕西省", "山西省", "重庆市", "贵州省", "辽宁省"],
    "four": ["四川省", "广西壮族自治区", "吉林省", "黑龙江省", "云南省"],
    "five": ["内蒙古自治区", "甘肃省", "海南省", "宁夏回族自治区", "青海省"],
    "new_tibet": ["新疆维吾尔自治区", "西藏自治区"]
}

def get_region_sto(province):
    for region, provinces in COURIER_REGIONS_STO.items():
        if province in provinces:
            return region
    return "two"

def calculate_sto(weight, province):
    region = get_region_sto(province)
    if region == "new_tibet":
        return round(weight * 13.0, 2)
    elif region == "five":
        return round(weight * 6.0, 2)
    else:
        if weight <= 0.5:
            price = 1.7
        elif weight <= 1.0:
            price = 2.3
        elif weight <= 2.0:
            price = 3.2
        elif weight <= 3.0:
            price = 4.0
        else:
            base_price = 4.0
            if region == "one":
                unit = 0.8
            elif region == "two":
                unit = 1.5
            else:
                unit = 2.0
            price = base_price + (weight - 3.0) * unit
        return round(price, 2)


# ==============================
# 中通快递计费逻辑（保持不变）
# ==============================
def calculate_zto(weight, province):
    n = math.ceil(weight)
    if province in ["青海省", "甘肃省", "内蒙古自治区", "宁夏回族自治区", "海南省"]:
        if n == 1:
            total = 7.0
        elif n == 2:
            total = 12.0
        elif n == 3:
            total = 17.0
        else:
            total = 17.0 + (n - 3) * 5.0
    elif province in ["新疆维吾尔自治区", "西藏自治区"]:
        if n == 1:
            total = 13.0
        else:
            total = 13.0 + (n - 1) * 12.0
    else:
        if n == 1:
            total = 2.5
        elif n == 2:
            total = 3.8
        elif n == 3:
            total = 4.8
        else:
            total = 4.8 + (n - 3) * 1.0
    return round(total, 2)


# ==============================
# 城市附加费（保持不变）
# ==============================
def add_city_fee(courier, province):
    fee = 0.0
    if courier == "申通":
        if province == "上海市":
            fee += 0.6
        elif province == "北京市":
            fee += 1.0
    elif courier == "中通":
        if province == "上海市" or province == "北京市":
            fee += 0.5
    return fee


# ==============================
# 支持的省份列表
# ==============================
PROVINCES = [
    "上海市", "江苏省", "浙江省", "安徽省", "北京市", "天津市", "河北省", "河南省",
    "山东省", "湖北省", "湖南省", "江西省", "广东省", "福建省", "陕西省", "山西省",
    "重庆市", "贵州省", "辽宁省", "四川省", "广西壮族自治区", "吉林省", "黑龙江省",
    "云南省", "内蒙古自治区", "甘肃省", "海南省", "宁夏回族自治区", "青海省",
    "新疆维吾尔自治区", "西藏自治区"
]


# ==============================
# Flask 路由
# ==============================
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    selected_courier = ""
    weight_val = ""
    selected_province = ""

    if request.method == 'POST':
        selected_courier = request.form.get('courier', '')
        weight_val = request.form.get('weight', '').strip()
        selected_province = request.form.get('province', '')

        try:
            weight_float = float(weight_val)
            if weight_float <= 0:
                result = "重量必须大于0"
            elif selected_courier not in ["顺丰", "申通", "中通"]:
                result = "请选择有效的快递公司"
            elif selected_province not in PROVINCES:
                result = "请选择有效的目的省份"
            else:
                if selected_courier == "顺丰":
                    base_cost = calculate_sf(weight_float, selected_province)
                elif selected_courier == "申通":
                    base_cost = calculate_sto(weight_float, selected_province)
                elif selected_courier == "中通":
                    base_cost = calculate_zto(weight_float, selected_province)
                else:
                    base_cost = 0

                extra_fee = add_city_fee(selected_courier, selected_province)
                total_cost = base_cost + extra_fee
                result = total_cost

        except ValueError:
            result = "请输入有效的数字重量"

    return render_template(
        'index.html',
        result=result,
        courier=selected_courier,
        weight=weight_val,
        province=selected_province,
        provinces=PROVINCES
    )


if __name__ == '__main__':
    app.run(debug=True)
