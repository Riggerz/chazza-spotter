from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json, os

app = Flask(__name__)
DATA_FILE = 'spots.json'

BRANDS = {
    'guide london': {'tier': 1, 'max_buy': 8, 'list': '22-30', 'note': 'Statement shirts do well. Check cuffs, collar, buttons.'},
    'ted baker': {'tier': 1, 'max_buy': 7, 'list': '18-28', 'note': 'Good if pattern, floral, geometric or larger sizes.'},
    'pretty green': {'tier': 1, 'max_buy': 8, 'list': '20-35', 'note': 'Mod/utility/jackets/chinos are strong. Check condition.'},
    'hackett': {'tier': 1, 'max_buy': 8, 'list': '20-35', 'note': 'Chinos, shirts and jackets are worth checking.'},
    'allsaints': {'tier': 1, 'max_buy': 8, 'list': '18-35', 'note': 'Great brand, but inspect stains/fading carefully.'},
    'g star': {'tier': 1, 'max_buy': 10, 'list': '25-45', 'note': 'Strong on jackets/jeans. Check hems, crotch and hardware.'},
    'g-star': {'tier': 1, 'max_buy': 10, 'list': '25-45', 'note': 'Strong on jackets/jeans. Check hems, crotch and hardware.'},
    'superdry': {'tier': 2, 'max_buy': 5, 'list': '14-24', 'note': 'Good bread and butter if clean, logo/style decent.'},
    'nautica': {'tier': 2, 'max_buy': 5, 'list': '14-24', 'note': 'Quarter zips, jackets and vintage look can move.'},
    'craghoppers': {'tier': 2, 'max_buy': 4, 'list': '12-20', 'note': 'Outdoor utility sells. Best in larger sizes and nice colours.'},
    'fat face': {'tier': 2, 'max_buy': 4, 'list': '12-20', 'note': 'Good quality but not always high value. Buy cheap.'},
    'white stuff': {'tier': 2, 'max_buy': 4, 'list': '12-20', 'note': 'Nice patterns and larger sizes are best.'},
    'ralph lauren': {'tier': 1, 'max_buy': 8, 'list': '20-40', 'note': 'Check authenticity, pony, labels and condition.'},
    'polo ralph lauren': {'tier': 1, 'max_buy': 8, 'list': '20-40', 'note': 'Check authenticity, pony, labels and condition.'},
    'brave soul': {'tier': 4, 'max_buy': 1, 'list': '6-10', 'note': 'Low value. Only bother if dirt cheap, mint, or bundled.'},
    'forever 21': {'tier': 4, 'max_buy': 1, 'list': '5-10', 'note': 'Usually leave unless standout and pennies.'},
    'next': {'tier': 3, 'max_buy': 3, 'list': '10-18', 'note': 'Quality can be good. Needs style, condition and size.'},
    'marks and spencer': {'tier': 3, 'max_buy': 3, 'list': '10-18', 'note': 'Autograph/Collezione/linen can be okay cheap.'},
}

def load_spots():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_spots(spots):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(spots, f, indent=2)

def jacko_verdict(brand, garment, price, condition, notes):
    key = brand.strip().lower()
    data = BRANDS.get(key)
    price = float(price or 0)
    garment_l = (garment or '').lower()
    condition_l = (condition or '').lower()
    notes_l = (notes or '').lower()

    if not data:
        max_buy = 3
        tier = '?'
        list_price = 'unknown'
        base = "Unknown brand, mush. Judge by quality, fabric, condition, style and size."
    else:
        max_buy = data['max_buy']
        tier = data['tier']
        list_price = data['list']
        base = data['note']

    red_flags = []
    if any(w in condition_l + ' ' + notes_l for w in ['stain', 'hole', 'bobble', 'bobbling', 'fade', 'damaged', 'rip']):
        red_flags.append('Condition issue mentioned')
    if any(w in garment_l for w in ['jacket', 'coat', 'bag', 'jeans']):
        max_buy += 2
    if any(w in garment_l for w in ['shirt', 'polo', 'tee', 't-shirt']):
        max_buy += 0

    if price <= max_buy and not red_flags:
        decision = 'BUY'
        tone = 'Craig, this is worth a punt.'
    elif price <= max_buy and red_flags:
        decision = 'CHECK HARD'
        tone = 'Could still work, but inspect it properly before paying.'
    elif price <= max_buy + 3 and tier in [1, 2, '?']:
        decision = 'MAYBE'
        tone = 'Not mad, but only buy if it feels quality or has standout style.'
    else:
        decision = 'LEAVE'
        tone = 'Nah mush, money is better kept for a cleaner flip.'

    return {
        'decision': decision,
        'tier': tier,
        'max_buy': max_buy,
        'resale': list_price,
        'message': f"{tone} Max buy about £{max_buy}. Expected list: £{list_price}. {base}",
        'red_flags': red_flags,
    }

@app.route('/')
def index():
    return render_template('index.html', brands=sorted(BRANDS.keys()), spots=load_spots())

@app.route('/api/check', methods=['POST'])
def api_check():
    data = request.json or {}
    return jsonify(jacko_verdict(data.get('brand',''), data.get('garment',''), data.get('price',0), data.get('condition',''), data.get('notes','')))

@app.route('/api/save', methods=['POST'])
def api_save():
    data = request.json or {}
    verdict = jacko_verdict(data.get('brand',''), data.get('garment',''), data.get('price',0), data.get('condition',''), data.get('notes',''))
    spots = load_spots()
    item = {**data, 'verdict': verdict, 'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    spots.insert(0, item)
    save_spots(spots)
    return jsonify({'ok': True, 'item': item})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
