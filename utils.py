# utils.py

import pandas as pd
import numpy as np
from datetime import datetime

def calculate_technical_indicators(df):
    """Teknik indikatörleri hesapla"""
    
    # RSI hesaplama
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD hesaplama
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df

def calculate_profit(trades):
    """İşlem geçmişinden toplam karı hesapla"""
    total_profit = 0
    for i in range(1, len(trades)):
        if trades[i]['side'] == 'SELL':
            buy_price = trades[i-1]['price']
            sell_price = trades[i]['price']
            quantity = trades[i]['quantity']
            profit = (sell_price - buy_price) * quantity
            total_profit += profit
    return total_profit

def calculate_win_rate(trades):
    """Kazanan işlemlerin oranını hesapla"""
    if len(trades) < 2:
        return 0
    
    winning_trades = 0
    total_trades = len(trades) // 2  # Her alım-satım çifti bir işlem
    
    for i in range(1, len(trades), 2):
        if i+1 < len(trades):
            buy_price = trades[i-1]['price']
            sell_price = trades[i]['price']
            if sell_price > buy_price:
                winning_trades += 1
    
    return (winning_trades / total_trades) * 100 if total_trades > 0 else 0

def format_number(number):
    """Sayıları okunaklı formata çevir"""
    return '{:.8f}'.format(number)

def get_current_time():
    """Şu anki zamanı string olarak döndür"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')