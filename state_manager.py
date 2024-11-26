# state_manager.py

import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, filename='bot_state.json'):
        self.filename = filename
        self.default_state = {
            'current_balance': 30,
            'current_coin': None,
            'trading_history': [],
            'last_update': None
        }

    def save_state(self, bot_instance):
        """Bot durumunu kaydet"""
        state = {
            'current_balance': bot_instance.current_balance,
            'current_coin': bot_instance.current_coin,
            'trading_history': [
                {
                    'timestamp': trade['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'quantity': trade['quantity'],
                    'price': trade['price']
                }
                for trade in bot_instance.trading_history
            ],
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.filename, 'w') as f:
            json.dump(state, f, indent=4)

    def load_state(self):
        """Kaydedilmiş durumu yükle"""
        if not os.path.exists(self.filename):
            return self.default_state
            
        try:
            with open(self.filename, 'r') as f:
                state = json.load(f)
                
            # Timestamp'leri datetime objesine çevir
            for trade in state['trading_history']:
                trade['timestamp'] = datetime.strptime(
                    trade['timestamp'], 
                    '%Y-%m-%d %H:%M:%S'
                )
                
            return state
        except Exception as e:
            print(f"Error loading state: {str(e)}")
            return self.default_state