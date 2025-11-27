from flask import Flask, render_template, request, jsonify
import os
import socket
import math

app = Flask(__name__)

# ========== 工具函数 ==========
def ceil_to_int(w):
    """申通/中通：1.2kg -> 2kg"""
    return math.ceil(w) if w > 1 else 1

def ceil_to_half(w):
    """顺丰：1.2kg -> 1.5kg, 1.7kg -> 2.0kg"""
    if w <= 1:
        return 1.0
    return math.ceil(w * 2) / 2

def add_waybill_fee(fee, province):
    """申通面单费规则"""
    if province == "北京市":
        return fee + 1.0
    elif province in ["上海市", "广东省"]:
        # 广东省包含深圳
        return fee + 0.6
    return fee

# ========== 快递计算逻辑 ==========
def calculate_shipping_fee(destination_province, weight_kg):
    if weight_kg <= 0:
        return {'申通': None, '中通': None, '顺丰': None}

    # --- 申通 ---
    def st_express_fee(prov, w):
        # 定义区域
        zones = {
            '一区': ['上海市', '江苏省', '浙江省', '安徽省'],
            '二区': ['湖北省', '湖南省', '河南省', '河北省', '广东省', '山东省', '福建省', '江西省', '天津市', '北京市'],
            '三区': ['陕西省', '山西省', '重庆市', '贵州省', '云南省', '四川省', '黑龙江省', '吉林省', '辽宁省'],
            '四区': ['广西壮族自治区', '内蒙古自治区', '甘肃省', '青海省', '宁夏回族自治区', '海南省', '新疆维吾尔自治区', '西藏自治区']
        }

        zone_name = next((z for z, ps in zones.items() if prov in ps), None)
        if not zone_name: return None

        # 计算重量（向上取整）
        calc_w = ceil_to_int(w)

        # 定价表
        prices = {
            '一区': [1.7, 1.9, 2.7, 3.6, 4, 0.8],
            '二区': [1.7, 1.9, 2.7, 3.6, 4, 1.5],
            '三区': [1.7, 1.9, 2.7, 3.6, 4, 2],
            '四区': [1.7, 1.9, 2.7, 3.6, 4, 6]  # 五区统一为6元/kg
        }

        base_price = prices[zone_name][0]
        price_05 = prices[zone_name][1]
        price_12 = prices[zone_name][2]
        price_23 = prices[zone_name][3]
        first_weight = prices[zone_name][4]
        continue_weight = prices[zone_name][5]

        if calc_w <= 0.5:
            total = base_price
        elif calc_w <= 1:
            total = price_05
        elif calc_w <= 2:
            total = price_12
        elif calc_w <= 3:
            total = price_23
        else:
            total = price_23 + (calc_w - 3) * continue_weight

        # 加面单费
        total = add_waybill_fee(total, prov)
        return round(total, 2)

    # --- 中通 ---
    def zto_freight(prov, w):
        zones = {
            '江浙沪': ['上海市', '江苏省', '浙江省'],
            '安徽': ['安徽省'],
            '福建江西天津山东': ['福建省', '江西省', '天津市', '山东省'],
            '北京湖北湖南河南河北广东': ['北京市', '湖北省', '湖南省', '河南省', '河北省', '广东省'],
            '广西陕西山西四川重庆': ['广西壮族自治区', '陕西省', '山西省', '四川省', '重庆市'],
            '云南贵州吉林黑龙江辽宁': ['云南省', '贵州省', '吉林省', '黑龙江省', '辽宁省'],
            '青海甘肃内蒙古宁夏海南': ['青海省', '甘肃省', '内蒙古自治区', '宁夏回族自治区', '海南省'],
            '新疆西藏': ['新疆维吾尔自治区', '西藏自治区']
        }
        zone_name = next((z for z, ps in zones.items() if prov in ps), None)
        if not zone_name: return None

        calc_w = ceil_to_int(w)

        if zone_name in ['青海甘肃内蒙古宁夏海南', '新疆西藏']:
            base = 7 if zone_name == '青海甘肃内蒙古宁夏海南' else 13
            sur = 5 if zone_name == '青海甘肃内蒙古宁夏海南' else 12
            total = base + max(0, calc_w - 1) * sur
        else:
            if calc_w <= 1: total = 2.5
            elif calc_w <= 2: total = 3.8
            elif calc_w <= 3: total = 4.8
            else:
                surcharge = {'江浙沪':1,'安徽':1,'福建江西天津山东':2,
                            '北京湖北湖南河南河北广东':2,
                            '广西陕西山西四川重庆':3,
                            '云南贵州吉林黑龙江辽宁':3}[zone_name]
                total = 4.8 + (calc_w - 3) * surcharge

        # 中通不加面单费
        return round(total, 2)

    # --- 顺丰 ---
    def sf_freight(prov, w):
        norm_prov = prov.strip()
        mapping = {"北京":"北京市","上海":"上海市","天津":"天津市","重庆":"重庆市",
                   "内蒙":"内蒙古自治区","广西":"广西壮族自治区","宁夏":"宁夏回族自治区",
                   "新疆":"新疆维吾尔自治区"}
        if norm_prov in mapping: norm_prov = mapping[norm_prov]
        
        rules = {
            "上海市":[(1,3,10,2),(3,20,14,2),(20,float('inf'),48,3)],
            "广东省":[(1,3,13,5),(3,20,23,5),(20,float('inf'),108,6.5)],
            "北京市":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "江苏省":[(1,3,11,2),(3,20,15,2),(20,float('inf'),49,3)],
            "浙江省":[(1,3,11,2),(3,20,15,2),(20,float('inf'),49,3)],
            "安徽省":[(1,3,11,2),(3,20,15,2),(20,float('inf'),49,3)],
            "山东省":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "河北省":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "河南省":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "四川省":[(1,3,15,5.5),(3,20,26,5),(20,float('inf'),111,6.5)],
            "湖南省":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "湖北省":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "福建省":[(1,3,13,5),(3,20,23,5),(20,float('inf'),108,6.5)],
            "江西省":[(1,3,13,5),(3,20,23,4),(20,float('inf'),91,5)],
            "云南省":[(1,3,15,5.5),(3,15,28,6),(15,float('inf'),100,7.5)],
            "广西壮族自治区":[(1,3,15,5.5),(3,20,26,5),(20,float('inf'),111,6.5)],
            "贵州省":[(1,3,15,5.5),(3,20,26,5),(20,float('inf'),111,6.5)],
            "黑龙江省":[(1,3,15,7),(3,15,29,6),(15,float('inf'),101,7)],
            "内蒙古自治区":[(1,3,13,5),(3,15,25,6),(15,float('inf'),97,7),
                             (1,3,13,5),(3,20,23,4.5),(20,float('inf'),99.5,6)],
            "新疆维吾尔自治区":[(1,3,19,10),(3,20,39,10),(20,float('inf'),209,12)],
            "西藏自治区":[(1,3,19,10),(3,20,39,10),(20,float('inf'),209,12)],
            "宁夏回族自治区":[(1,3,13,5.5),(3,20,24,6),(20,float('inf'),126,7)],
            "甘肃省":[(1,3,13,5),(3,20,23,4.5),(20,float('inf'),99.5,6)],
            "陕西省":[(1,3,15,5),(3,20,25,4),(20,float('inf'),93,5)],
            "青海省":[(1,3,14,5.5),(3,20,25,5),(20,float('inf'),110,6.5)],
            "辽宁省":[(1,3,15,5.5),(3,20,26,5),(20,float('inf'),111,6.5)],
            "吉林省":[(1,3,15,6.5),(3,15,28,6),(15,float('inf'),100,7.5)],
            "山西省":[(1,3,15,5),(3,20,25,4),(20,float('inf'),93,5)],
            "海南省":[(1,3,15,5.5),(3,20,26,5),(20,float('inf'),111,6.5)],
            "重庆市":[(1,3,15,5.5),(3,20,26,5),(20,float('inf'),111,6.5)]
        }
        if norm_prov not in rules:
            candidates = [p for p in rules.keys() if norm_prov in p or p in norm_prov]
            if len(candidates) == 1: norm_prov = candidates[0]
            else: return None

        calc_w = ceil_to_half(w)

        for min_w, max_w, base, unit in rules[norm_prov]:
            if min_w <= calc_w <= max_w:
                total = base if calc_w <= min_w else base + (calc_w - min_w) * unit
                return round(total, 2)
        last = rules[norm_prov][-1]
        total = last[2] + (calc_w - last[0]) * last[3]
        return round(total, 2)

    return {
        '申通': st_express_fee(destination_province, weight_kg),
        '中通': zto_freight(destination_province, weight_kg),
        '顺丰': sf_freight(destination_province, weight_kg)
    }

# ========== 省份列表 ==========
PROVINCES = [
    "北京市", "天津市", "河北省", "山西省", "内蒙古自治区", "辽宁省", "吉林省", "黑龙江省",
    "上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省",
    "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区", "海南省",
    "重庆市", "四川省", "贵州省", "云南省", "西藏自治区",
    "陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区"
]

# ========== 路由 ==========
@app.route('/')
def index():
    return render_template('index.html', provinces=PROVINCES)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    province = data.get('province')
    weight = float(data.get('weight', 1))
    result = calculate_shipping_fee(province, weight)
    return jsonify(result)

# ========== 启动 ==========
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>快递运费计算器</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 30px auto; padding: 20px; background: #fafafa; }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 25px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 6px; font-weight: bold; color: #34495e; }
        select, input { width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #3498db; color: white; font-size: 18px; border: none; border-radius: 6px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #2980b9; }
        #result { margin-top: 25px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); display: none; }
        .company { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; font-size: 16px; }
        .company:last-child { border-bottom: none; }
        .price { font-weight: bold; color: #e74c3c; }
        .note { font-size: 12px; color: #7f8c8d; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>📦 快递运费计算器（申通已更新）</h1>
    <div class="form-group">
        <label for="province">目的省份：</label>
        <select id="province">
            {% for p in provinces %}
            <option value="{{ p }}">{{ p }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="form-group">
        <label for="weight">重量 (kg)：</label>
        <input type="number" id="weight" step="0.1" min="0.1" value="1.2">
    </div>
    <button onclick="calculate()">计算运费</button>
    <div class="note">💡 规则说明：<br>
        • 申通：1.2kg → 按 2kg 计，北京+1元，上海/深圳+0.6元<br>
        • 中通：1.2kg → 按 2kg 计，北上广+0.5元<br>
        • 顺丰：1.2kg → 按 1.5kg 计，1.7kg → 按 2.0kg 计
    </div>
    <div id="result"></div>

    <script>
        function calculate() {
            const province = document.getElementById('province').value;
            const weight = parseFloat(document.getElementById('weight').value);
            if (!weight || weight <= 0) {
                alert('请输入有效的重量！');
                return;
            }
            fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({province: province, weight: weight})
            })
            .then(response => response.json())
            .then(data => {
                let html = '<h3>🚚 运费结果（精确到分）：</h3>';
                for (const [company, price] of Object.entries(data)) {
                    const priceStr = price !== null ? price.toFixed(2) + ' 元' : '不支持';
                    html += `<div class="company"><span>${company}</span><span class="price">${priceStr}</span></div>`;
                }
                document.getElementById('result').innerHTML = html;
                document.getElementById('result').style.display = 'block';
            })
            .catch(err => {
                console.error(err);
                alert('计算出错，请重试');
            });
        }
    </script>
</body>
</html>''')

    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    port = find_free_port()
    print(f"\n✅ 快递运费计算器（申通已更新）已启动！")
    print(f"🔗 请访问：http://localhost:{port}")
    print(f"👥 同事使用：需在同一局域网，并将 localhost 替换为你的电脑 IP 地址\n")

    app.run(debug=False, host='0.0.0.0', port=port)
