from flask import Flask, render_template, request
import math

app = Flask(__name__)

# ==============================
# 顺丰快递计费（月结客户专属模型）
# 基于真实账单：021HL_0210967957_20251101_20251126.xlsx
# 仅适用于“陆运包裹”产品，上海市始发
# ==============================
def calculate_sf(weight, province):
    """
    顺丰月结协议价模型（非公开报价）
    根据实际账单拟合，四舍五入取整
    """
    if province == "上海市":
        return round(8.5 + 2.0 * weight)
    elif province in ["江苏省", "浙江省", "安徽省"]:
        return round(9.0 + 2.0 * weight)
    elif province in ["广东省", "福建省"]:
        return round(10.0 + 4.8 * weight)
    elif province in ["湖北省", "湖南省", "江西省", "河南省", "山东省", "河北省", "北京市", "天津市"]:
        return round(10.0 + 4.5 * weight)
    elif province in ["陕西省", "山西省", "重庆市", "四川省", "广西壮族自治区", "云南省"]:
        return round(8.0 + 6.0 * weight)
    elif province in ["辽宁省", "吉林省", "黑龙江省"]:
        if weight <= 3:
            return round(10 + 5.0 * weight)
        else:
            return round(8 + 6.5 * weight)
    elif province in ["贵州省", "海南省", "内蒙古自治区", "甘肃省", "宁夏回族自治区", "青海省"]:
        return round(8.0 + 7.0 * weight)
    else:  # 新疆维吾尔自治区, 西藏自治区
        return round(8.0 + 8.0 * weight)


# ==============================
# 申通快递计费逻辑（保持原样，未改动）
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
# 中通快递计费逻辑（保持原样，未改动）
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
# 城市附加费（保持原样，未改动）
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
