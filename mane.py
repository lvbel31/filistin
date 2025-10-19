from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Basit bir veritabanı kurulumu
def init_db():
    conn = sqlite3.connect('donations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS donations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  amount REAL NOT NULL,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  card_last_four TEXT NOT NULL,
                  card_type TEXT NOT NULL,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# HTML template'ini doğrudan string olarak tanımlıyoruz
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Filistin'e Destek - Bağış Kampanyası</title>
    <style>
        :root {
            --palestine-black: #000000;
            --palestine-white: #FFFFFF;
            --palestine-green: #007A3D;
            --palestine-red: #CE1126;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        header {
            background: linear-gradient(to right, var(--palestine-black) 33%, var(--palestine-white) 33%, var(--palestine-white) 66%, var(--palestine-green) 66%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            position: relative;
        }
        
        header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background-color: var(--palestine-red);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .subtitle {
            font-size: 1.2rem;
            max-width: 800px;
            margin: 0 auto;
            color: var(--palestine-black);
            background-color: rgba(255,255,255,0.8);
            padding: 10px;
            border-radius: 5px;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .intro {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1.5rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .donation-options {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 2rem;
        }
        
        .donation-amount {
            background-color: white;
            border: 2px solid var(--palestine-green);
            border-radius: 8px;
            padding: 1.5rem 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .donation-amount:hover {
            background-color: var(--palestine-green);
            color: white;
            transform: translateY(-5px);
        }
        
        .donation-amount.selected {
            background-color: var(--palestine-red);
            color: white;
            border-color: var(--palestine-red);
        }
        
        .custom-amount {
            grid-column: 1 / -1;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 1rem;
        }
        
        .custom-amount input {
            width: 100%;
            max-width: 300px;
            padding: 0.8rem;
            border: 2px solid var(--palestine-green);
            border-radius: 5px;
            font-size: 1.1rem;
            text-align: center;
        }
        
        .payment-form {
            background-color: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        input, select {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        .card-details {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 15px;
        }
        
        .btn-donate {
            background-color: var(--palestine-red);
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s;
            font-weight: bold;
        }
        
        .btn-donate:hover {
            background-color: #a00d1e;
        }
        
        footer {
            background-color: var(--palestine-black);
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .security-notice {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .security-notice i {
            margin-right: 5px;
            color: var(--palestine-green);
        }
        
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
        }
        
        .alert-success {
            color: #3c763d;
            background-color: #dff0d8;
            border-color: #d6e9c6;
        }
        
        .alert-error {
            color: #a94442;
            background-color: #f2dede;
            border-color: #ebccd1;
        }
        
        .donation-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--palestine-red);
        }
        
        @media (max-width: 768px) {
            .donation-options {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
            
            .card-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>Filistin'e Destek Olun</h1>
            <p class="subtitle">İhtiyaç sahiplerine yardım ulaştırmak için bağışta bulunun. Her katkınız bir umut ışığıdır.</p>
        </div>
    </header>
    
    <div class="container">
        <section class="intro">
            <h2>Filistin'deki Kardeşlerimize Yardım Eli Uzatın</h2>
            <p>Filistin'deki zor durumdaki kardeşlerimize destek olmak için bağışlarınızı bekliyoruz. Bağışlarınız gıda, temiz su, tıbbi malzeme ve barınma ihtiyaçları için kullanılacaktır.</p>
        </section>
        
        <div class="donation-stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_donations }}$</div>
                <div>Toplanan Bağış</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ donation_count }}</div>
                <div>Bağışçı Sayısı</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ avg_donation }}$</div>
                <div>Ortalama Bağış</div>
            </div>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <h2>Bağış Miktarını Seçin</h2>
        <div class="donation-options">
            <div class="donation-amount" data-amount="5">5$</div>
            <div class="donation-amount" data-amount="10">10$</div>
            <div class="donation-amount" data-amount="20">20$</div>
            <div class="donation-amount" data-amount="30">30$</div>
            <div class="donation-amount" data-amount="40">40$</div>
            <div class="donation-amount" data-amount="50">50$</div>
            <div class="donation-amount" data-amount="100">100$</div>
            <div class="donation-amount" data-amount="250">250$</div>
            <div class="donation-amount" data-amount="500">500$</div>
            <div class="custom-amount">
                <input type="number" id="customAmount" placeholder="Diğer miktar ($)">
            </div>
        </div>
        
        <div class="payment-form">
            <h2>Ödeme Bilgileri</h2>
            <form id="donationForm" method="POST" action="/donate">
                <div class="form-group">
                    <label for="fullName">Ad Soyad</label>
                    <input type="text" id="fullName" name="fullName" required>
                </div>
                
                <div class="form-group">
                    <label for="email">E-posta</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="amount">Bağış Miktarı ($)</label>
                    <input type="number" id="amount" name="amount" step="0.01" required readonly>
                </div>
                
                <div class="form-group">
                    <label for="cardNumber">Kart Numarası</label>
                    <input type="text" id="cardNumber" name="cardNumber" placeholder="1234 5678 9012 3456" required>
                </div>
                
                <div class="form-group card-details">
                    <div>
                        <label for="expiryDate">Son Kullanma Tarihi</label>
                        <input type="text" id="expiryDate" name="expiryDate" placeholder="AA/YY" required>
                    </div>
                    
                    <div>
                        <label for="cvv">CVV</label>
                        <input type="text" id="cvv" name="cvv" placeholder="123" required>
                    </div>
                    
                    <div>
                        <label for="cardType">Kart Türü</label>
                        <select id="cardType" name="cardType" required>
                            <option value="">Seçiniz</option>
                            <option value="visa">Visa</option>
                            <option value="mastercard">Mastercard</option>
                            <option value="amex">American Express</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="btn-donate">Bağış Yap</button>
            </form>
            
            <div class="security-notice">
                <i>🔒</i> <span>Ödeme bilgileriniz güvenli bir şekilde işlenmektedir.</span>
            </div>
        </div>
    </div>
    
    <footer>
        <p>Filistin'e Destek Bağış Kampanyası &copy; 2023</p>
        <p>Tüm bağışlar Filistin'deki ihtiyaç sahiplerine ulaştırılacaktır.</p>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const donationAmounts = document.querySelectorAll('.donation-amount');
            const customAmountInput = document.getElementById('customAmount');
            const amountInput = document.getElementById('amount');
            let selectedAmount = 0;
            
            // Bağış miktarı seçimi
            donationAmounts.forEach(amount => {
                amount.addEventListener('click', function() {
                    // Tüm seçimleri kaldır
                    donationAmounts.forEach(a => a.classList.remove('selected'));
                    // Tıklananı seç
                    this.classList.add('selected');
                    // Özel miktarı temizle
                    customAmountInput.value = '';
                    // Seçilen miktarı kaydet ve inputa yaz
                    selectedAmount = this.getAttribute('data-amount');
                    amountInput.value = selectedAmount;
                });
            });
            
            // Özel miktar girişi
            customAmountInput.addEventListener('input', function() {
                // Diğer seçimleri kaldır
                donationAmounts.forEach(a => a.classList.remove('selected'));
                // Özel miktarı kaydet ve inputa yaz
                selectedAmount = this.value;
                amountInput.value = selectedAmount;
            });
            
            // Kart numarası formatlama
            document.getElementById('cardNumber').addEventListener('input', function(e) {
                let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
                let matches = value.match(/\d{4,16}/g);
                let match = matches && matches[0] || '';
                let parts = [];
                
                for (let i = 0, len = match.length; i < len; i += 4) {
                    parts.push(match.substring(i, i + 4));
                }
                
                if (parts.length) {
                    e.target.value = parts.join(' ');
                } else {
                    e.target.value = value;
                }
            });
            
            // Son kullanma tarihi formatlama
            document.getElementById('expiryDate').addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length >= 2) {
                    e.target.value = value.substring(0, 2) + '/' + value.substring(2, 4);
                }
            });
        });
    </script>
</body>
</html>
'''

def get_donation_stats():
    """Bağış istatistiklerini getirir"""
    conn = sqlite3.connect('donations.db')
    c = conn.cursor()
    
    # Toplam bağış miktarı
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM donations WHERE status = 'completed'")
    total_donations = c.fetchone()[0]
    
    # Toplam bağışçı sayısı
    c.execute("SELECT COUNT(DISTINCT email) FROM donations WHERE status = 'completed'")
    donation_count = c.fetchone()[0]
    
    # Ortalama bağış miktarı
    c.execute("SELECT COALESCE(AVG(amount), 0) FROM donations WHERE status = 'completed'")
    avg_donation = round(c.fetchone()[0], 2)
    
    conn.close()
    
    return total_donations, donation_count, avg_donation

@app.route('/')
def index():
    """Ana sayfa"""
    total_donations, donation_count, avg_donation = get_donation_stats()
    return render_template('index.html', 
                         total_donations=total_donations,
                         donation_count=donation_count,
                         avg_donation=avg_donation)

@app.route('/donate', methods=['POST'])
def donate():
    """Bağış işlemini işler"""
    try:
        # Form verilerini al
        amount = float(request.form['amount'])
        name = request.form['fullName']
        email = request.form['email']
        card_number = request.form['cardNumber'].replace(' ', '')
        expiry_date = request.form['expiryDate']
        cvv = request.form['cvv']
        card_type = request.form['cardType']
        
        # Basit validasyon
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Geçersiz bağış miktarı'})
        
        if len(card_number) < 13 or len(card_number) > 19:
            return jsonify({'success': False, 'message': 'Geçersiz kart numarası'})
        
        # Kartın son 4 hanesini al
        card_last_four = card_number[-4:]
        
        # Veritabanına kaydet
        conn = sqlite3.connect('donations.db')
        c = conn.cursor()
        c.execute('''INSERT INTO donations 
                    (amount, name, email, card_last_four, card_type, status) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (amount, name, email, card_last_four, card_type, 'completed'))
        conn.commit()
        conn.close()
        
        # Başarı mesajı
        return jsonify({
            'success': True, 
            'message': f'${amount} bağışınız için teşekkür ederiz! Ödeme işleminiz başarıyla tamamlandı.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Bir hata oluştu: {str(e)}'})

# HTML template'ini Flask'a kaydet
@app.route('/index.html')
def html_template():
    return HTML_TEMPLATE

if __name__ == '__main__':
    # Veritabanını başlat
    init_db()
    
    # Flask uygulamasını çalıştır
    print("Filistin Bağış Sitesi başlatılıyor...")
    print("Site adresi: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
