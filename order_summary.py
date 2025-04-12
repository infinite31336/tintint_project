from flask import Flask, jsonify, app
import logging
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(filename='api.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

orders_db = [
    {"order_id": 1, "order_date": "2025-01-11", "total_amount": 1300},
    {"order_id": 2, "order_date": "2025-02-18", "total_amount": 900},
    {"order_id": 3, "order_date": "2025-03-20", "total_amount": 1250},
    {"order_id": 4, "order_date": "2025-04-07", "total_amount": 0},
    {"order_id": 5, "order_date": "2025-04-11", "total_amount": 800}
]
order_items_db = [
    {"item_id": 1, "order_id": 1, "product_name": "文庫本", "category": "相片書", "quantity": 1, "price": 800},
    {"item_id": 2, "order_id": 1, "product_name": "桌曆", "category": "月曆系列", "quantity": 1, "price": 700},
    {"item_id": 3, "order_id": 2, "product_name": "生日卡", "category": "卡片系列", "quantity": 3, "price": 300},
    {"item_id": 4, "order_id": 3, "product_name": "無框畫照片", "category": "框畫系列", "quantity": 1, "price": 300},
    {"item_id": 5, "order_id": 3, "product_name": "謝卡", "category": "卡片系列", "quantity": 5, "price": 190},
    {"item_id": 6, "order_id": 5, "product_name": "賀年卡", "category": "卡片系列", "quantity": 4, "price": 200},
    {"item_id": 7, "order_id": 4, "product_name": "木框畫照片", "category": "框畫系列", "quantity": 2, "price": -350}
]

@app.route('/api/orders/summary/<start_date>/<end_date>', methods=['GET'])
def order_summary(start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if start > end:
            return jsonify({"status": "error", "message": "開始日期不能晚於結束日期"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "無效的日期格式"}), 400

    filtered_orders = [order for order in orders_db if start_date <= order["order_date"] <= end_date]
    filtered_order_ids = [order["order_id"] for order in filtered_orders]
    filtered_items = [item for item in order_items_db if item["order_id"] in filtered_order_ids]

    summary = {}
    for item in filtered_items:
        category = item["category"]
        if category not in summary:
            summary[category] = {"total_quantity": 0, "total_amount": 0}
        summary[category]["total_quantity"] += item["quantity"]
        summary[category]["total_amount"] += item["quantity"] * item["price"]

    summary = {}
    for item in filtered_items:
        category = item["category"]
        if category not in summary:
            summary[category] = {'total_quantity': 0, 'total_amount': 0}
        summary[category]["total_quantity"] += item["quantity"]
        summary[category]["total_amount"] += item['quantity'] * item['price']
        
    log_msg = f'Select Orders: start_date:{start_date}, end_date:{end_date}, results={len(filtered_orders)}'
    logging.info(log_msg)

    if not filtered_orders:
        return jsonify({"status": "success", "data": {}, "message": "無符合條件的訂單"})
    return jsonify({
        "status": "success",
        "data": {"total_orders": len(filtered_orders), "categories": summary},
        "message": "查詢成功"
    })

def check_order_consistency(orders, order_items):
    response = []

    for order in orders:
        check_results = []
        order_id = order['order_id']
        total_amount = order['total_amount']
        order_date = datetime.strptime(order['order_date'], '%Y-%m-%d')

        items = [item for item in order_items if item["order_id"] == order_id]

        if not items:
            check_results.append('訂單沒有項目')
        calculated_amount = 0
        for item in items:
            if item["price"] < 0:
                check_results.append(f'項目 {item['item_id']} 價格為負: {item['price']}')
            if order_date < datetime.strptime(order['order_date'], '%Y-%m-%d'):
                check_results.append('訂單日期早於項目創建時間')
            calculated_amount += item['quantity'] * item['price']
        if calculated_amount != total_amount:
            check_results.append(f'總金額不符: 應為 {calculated_amount}, 實際為 {total_amount}')

        response.append({'order_id': order_id, 'check_results': ','.join(check_results) if check_results else '結果一致'})

    return response

if __name__ == "__main__":

    test_orders = [
        {"order_id": 1, "order_date": "2025-01-11", "total_amount": 1300},
        {"order_id": 2, "order_date": "2025-02-18", "total_amount": 900},
        {"order_id": 3, "order_date": "2025-03-20", "total_amount": 1250},
        {"order_id": 4, "order_date": "2025-04-07", "total_amount": 0},
        {"order_id": 5, "order_date": "2025-04-11", "total_amount": 800}
    ]
    test_items = [
        {"item_id": 1, "order_id": 1, "product_name": "文庫本", "category": "相片書", "quantity": 1, "price": 800},
        {"item_id": 2, "order_id": 1, "product_name": "桌曆", "category": "月曆系列", "quantity": 1, "price": 700},
        {"item_id": 3, "order_id": 2, "product_name": "生日卡", "category": "卡片系列", "quantity": 3, "price": 300},
        {"item_id": 4, "order_id": 3, "product_name": "無框畫照片", "category": "框畫系列", "quantity": 1, "price": 300},
        {"item_id": 5, "order_id": 3, "product_name": "謝卡", "category": "卡片系列", "quantity": 5, "price": 190},
        {"item_id": 6, "order_id": 5, "product_name": "賀年卡", "category": "卡片系列", "quantity": 4, "price": 200},
        {"item_id": 7, "order_id": 4, "product_name": "木框畫照片", "category": "框畫系列", "quantity": 2, "price": -350}
    ]

    print("一致性檢查結果:")
    results = check_order_consistency(test_orders, test_items)
    for r in results:
        print(f"Order {r['order_id']}: {r['check_results']}")
    app.run(debug=True)
