# bot.py

from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
import time
import telegram
from datetime import datetime
import threading

from config import *
from models import PricePredictionModel
from utils import *
# bot.py

from state_manager import StateManager

class CryptoTradingBot:
    def __init__(self):
        # ... (mevcut init kodları) ...
        
        # State manager'ı ekle
        self.state_manager = StateManager()
        self.load_saved_state()
        
    def load_saved_state(self):
        """Kaydedilmiş durumu yükle"""
        state = self.state_manager.load_state()
        self.current_balance = state['current_balance']
        self.current_coin = state['current_coin']
        self.trading_history = state['trading_history']
        
    def save_current_state(self):
        """Mevcut durumu kaydet"""
        self.state_manager.save_state(self)
        
    def execute_trade(self, symbol, side, quantity):
        """Alım/satım işlemi gerçekleştir"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            trade_info = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': float(order['fills'][0]['price'])
            }
            
            self.trading_history.append(trade_info)
            self.save_current_state()  # Her işlemden sonra kaydet
            
            self.send_telegram_notification(
                f"{side} {quantity} {symbol} at {trade_info['price']}"
            )
            
            if self.on_trade_callback:
                self.on_trade_callback(trade_info)
            
            return order
            
        except BinanceAPIException as e:
            self.handle_error(f"Error executing trade: {str(e)}")
            return None

    def start(self):
        """Bot'u başlat"""
        self.is_running = True
        threading.Thread(target=self.trading_loop).start()

    def stop(self):
        """Bot'u durdur"""
        self.is_running = False

    def get_viable_coins(self):
    """1 dolar altı ve en yüksek hacimli 10 coini getir"""
    try:
        tickers = self.client.get_ticker()
        viable_coins = []
        
        for ticker in tickers:
            if ticker['symbol'].endswith('USDT'):
                price = float(ticker['lastPrice'])
                volume = float(ticker['volume']) * price
                
                if price < 1.0:  # 1 dolar altı coinler
                    viable_coins.append({
                        'symbol': ticker['symbol'],
                        'price': price,
                        'volume': volume
                    })
        
        # Hacme göre sırala ve ilk 10'u al
        viable_coins.sort(key=lambda x: x['volume'], reverse=True)
        return viable_coins[:10]
        
    except BinanceAPIException as e:
        self.handle_error(f"Error getting viable coins: {str(e)}")
        return []
            
        except BinanceAPIException as e:
            self.handle_error(f"Error getting viable coins: {str(e)}")
            return []

    def get_historical_data(self, symbol, interval='1h', limit=500):
        """Geçmiş fiyat verilerini getir"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return calculate_technical_indicators(df)
            
        except BinanceAPIException as e:
            self.handle_error(f"Error getting historical data: {str(e)}")
            return None

    def execute_trade(self, symbol, side, quantity):
        """Alım/satım işlemi gerçekleştir"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            trade_info = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': float(order['fills'][0]['price'])
            }
            
            self.trading_history.append(trade_info)
            self.send_telegram_notification(
                f"{side} {quantity} {symbol} at {trade_info['price']}"
            )
            
            if self.on_trade_callback:
                self.on_trade_callback(trade_info)
            
            return order
            
        except BinanceAPIException as e:
            self.handle_error(f"Error executing trade: {str(e)}")
            return None

    def trading_loop(self):
        """Ana trading döngüsü"""
        while self.is_running:
            try:
                if self.current_coin:
                    # Mevcut coin için verileri al
                    df = self.get_historical_data(self.current_coin)
                    if df is None:
                        continue
                    
                    # Fiyat tahmini yap
                    predicted_price = self.prediction_model.predict(df)
                    current_price = float(self.client.get_symbol_ticker(
                        symbol=self.current_coin
                    )['price'])
                    
                    # Trading sinyallerini kontrol et
                    last_row = df.iloc[-1]
                    rsi = last_row['RSI']
                    macd = last_row['MACD']
                    signal = last_row['Signal']
                    
                    # Trading kararları
                    if self.current_balance > 0:  # Alım için
                        if (rsi < 30 and macd > signal and 
                            predicted_price > current_price):
                            quantity = self.calculate_quantity(
                                self.current_coin,
                                self.current_balance
                            )
                            self.execute_trade(self.current_coin, 'BUY', quantity)
                    else:  # Satım için
                        if (rsi > 70 and macd < signal and 
                            predicted_price < current_price):
                            balance = self.get_coin_balance(self.current_coin)
                            if balance > 0:
                                self.execute_trade(self.current_coin, 'SELL', balance)
                
                time.sleep(UPDATE_INTERVAL)
                
            except Exception as e:
                self.handle_error(f"Error in trading loop: {str(e)}")
                time.sleep(UPDATE_INTERVAL)

    def calculate_quantity(self, symbol, amount):
        """İşlem miktarını hesapla"""
        try:
            info = self.client.get_symbol_info(symbol)
            price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            
            # Lot size kurallarını al
            lot_size_filter = next(filter(
                lambda x: x['filterType'] == 'LOT_SIZE',
                info['filters']
            ))
            
            min_qty = float(lot_size_filter['minQty'])
            step_size = float(lot_size_filter['stepSize'])
            
            # Miktarı hesapla
            quantity = (amount / price)
            
            # Step size'a göre yuvarla
            quantity = (quantity // step_size) * step_size
            
            if quantity < min_qty:
                return min_qty
                
            return quantity
            
        except Exception as e:
            self.handle_error(f"Error calculating quantity: {str(e)}")
            return None

    def get_coin_balance(self, symbol):
        """Coin bakiyesini getir"""
        try:
            coin = symbol.replace('USDT', '')
            balance = self.client.get_asset_balance(asset=coin)
            return float(balance['free'])
        except Exception as e:
            self.handle_error(f"Error getting balance: {str(e)}")
            return 0

    def send_telegram_notification(self, message):
        """Telegram bildirimi gönder"""
        try:
            self.telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message
            )
        except Exception as e:
            print(f"Telegram notification error: {str(e)}")

    def handle_error(self, error_message):
        """Hata yönetimi"""
        print(f"Error: {error_message}")
        self.send_telegram_notification(f"❌ Error: {error_message}")
        
        if self.on_error_callback:
            self.on_error_callback(error_message)

    def get_performance_metrics(self):
        """Performans metriklerini hesapla"""
        return {
            'total_profit': calculate_profit(self.trading_history),
            'win_rate': calculate_win_rate(self.trading_history),
            'total_trades': len(self.trading_history),
            'current_balance': self.current_balance
        }