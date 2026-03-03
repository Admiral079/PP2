import re
import json

#1
with open("raw.txt", encoding="utf-8") as f:
    text = f.read()

prices = re.findall(r"\d{1,3}(?:\s\d{3})*,\d{2}", text)

print(prices)

#2
raw_products = re.findall(r"\d+\.\n([^\n]+)", text)
clean_products = []

for p in raw_products:
    p = re.sub(r"\[RX\]-", "", p)
    name = re.match(r"[А-Яа-яA-Za-z\s\-]+", p)
    if name:
        clean_products.append(name.group().strip())

for product in clean_products:
    print(product)
    
#3
total = re.search(r"ИТОГО:\n([\d\s]+,\d{2})", text)

if total:
    print(total.group(1))
    
#4
date = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", text)
if date:
    date_time = date.group(1)
    print(date_time)
    
#5
match = re.search(r"(Банковская карта|Наличные|Кредитная карта):", text)
if match:
    payment_method = match.group(1)
    print(payment_method)
    
#6
data = {}

data["receipt_number"] = re.search(r"Чек №(\d+)", text).group(1)
data["date_time"] = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", text).group(1)
data["payment_method"] = re.search(r"(Банковская карта|Наличные|Кредитная карта):", text).group(1)
data["total_amount"] = re.search(r"ИТОГО:\s*\n([\d\s]+,\d{2})", text).group(1)

print(json.dumps(data, ensure_ascii=False, indent=4))