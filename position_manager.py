"""
Position Manager - Advanced SL & Target Management
==================================================
Handles stop-loss, target, and trailing SL automation
"""

import logging
from typing import Dict, Optional
from dhanhq import dhanhq
import strategy_config

class PositionManager:
    """
    Manages positions with automatic SL/Target and trailing SL
    """
    
    def __init__(self, dhan: dhanhq):
        self.dhan = dhan
        self.logger = logging.getLogger(__name__)
        self.positions = {}
        
        # Configuration
        self.max_loss = strategy_config.MAX_LOSS_PER_LOT
        self.target = strategy_config.TARGET_PER_LOT
        self.lot_size = strategy_config.LOT_SIZE
        self.trailing_sl_points = strategy_config.TRAILING_SL_AFTER_TARGET
    
    def add_position(self, order_id: str, entry_price: float, strike: int, 
                    option_type: str, quantity: int):
        """Add new position to monitor"""
        
        # Calculate SL and Target prices
        sl_per_contract = self.max_loss / self.lot_size
        target_per_contract = self.target / self.lot_size
        
        sl_price = entry_price - sl_per_contract
        target_price = entry_price + target_per_contract
        
        self.positions[order_id] = {
            'entry_price': entry_price,
            'current_price': entry_price,
            'sl_price': sl_price,
            'target_price': target_price,
            'strike': strike,
            'type': option_type,
            'quantity': quantity,
            'status': 'OPEN',
            'target_hit': False,
            'max_price': entry_price,
            'trailing_sl_active': False
        }
        
        self.logger.info(f"✅ Position added: {order_id}")
        self.logger.info(f"   Entry: ₹{entry_price:.2f}")
        self.logger.info(f"   SL: ₹{sl_price:.2f}")
        self.logger.info(f"   Target: ₹{target_price:.2f}")
    
    def update_position(self, order_id: str, current_price: float) -> Optional[str]:
        """
        Update position and check for SL/Target
        
        Returns: 'SL_HIT', 'TARGET_HIT', 'TRAILING_EXIT', or None
        """
        
        if order_id not in self.positions:
            return None
        
        pos = self.positions[order_id]
        pos['current_price'] = current_price
        
        # Update max price
        if current_price > pos['max_price']:
            pos['max_price'] = current_price
        
        # Phase 1: Before Target Hit
        if not pos['target_hit']:
            # Check if target hit
            if current_price >= pos['target_price']:
                self.logger.info(f"🎯 TARGET HIT for {order_id}!")
                self.logger.info(f"   Entry: ₹{pos['entry_price']:.2f}")
                self.logger.info(f"   Current: ₹{current_price:.2f}")
                self.logger.info(f"   Profit: Rs.{self.target:,.2f}")
                
                # Move SL to entry (lock profit)
                pos['sl_price'] = pos['entry_price']
                pos['target_hit'] = True
                pos['trailing_sl_active'] = True
                
                self.logger.info(f"✅ SL moved to entry: ₹{pos['entry_price']:.2f}")
                self.logger.info(f"✅ Trailing SL activated ({self.trailing_sl_points} points)")
                
                return 'TARGET_HIT'
            
            # Check if initial SL hit
            if current_price <= pos['sl_price']:
                self.logger.warning(f"🛑 STOP LOSS HIT for {order_id}")
                self.logger.warning(f"   Entry: ₹{pos['entry_price']:.2f}")
                self.logger.warning(f"   Exit: ₹{current_price:.2f}")
                self.logger.warning(f"   Loss: Rs.{self.max_loss:,.2f}")
                
                pos['status'] = 'CLOSED'
                return 'SL_HIT'
        
        # Phase 2: After Target Hit - Trailing SL
        else:
            # Calculate trailing SL (10 points below max)
            premium_per_point = self.lot_size / 50
            trailing_sl_price = pos['max_price'] - (self.trailing_sl_points * premium_per_point)
            
            # Keep SL at least at entry
            trailing_sl_price = max(trailing_sl_price, pos['entry_price'])
            
            # Update SL
            pos['sl_price'] = trailing_sl_price
            
            # Check if trailing SL hit
            if current_price <= trailing_sl_price:
                profit = (current_price - pos['entry_price']) * self.lot_size
                
                self.logger.info(f"✅ TRAILING SL EXIT for {order_id}")
                self.logger.info(f"   Entry: ₹{pos['entry_price']:.2f}")
                self.logger.info(f"   Max: ₹{pos['max_price']:.2f}")
                self.logger.info(f"   Exit: ₹{current_price:.2f}")
                self.logger.info(f"   Profit: Rs.{profit:,.2f}")
                
                pos['status'] = 'CLOSED'
                return 'TRAILING_EXIT'
        
        return None
    
    def get_position_status(self, order_id: str) -> Dict:
        """Get current position status"""
        if order_id in self.positions:
            pos = self.positions[order_id]
            current_pnl = (pos['current_price'] - pos['entry_price']) * self.lot_size
            
            return {
                'status': pos['status'],
                'entry': pos['entry_price'],
                'current': pos['current_price'],
                'sl': pos['sl_price'],
                'target': pos['target_price'],
                'pnl': current_pnl,
                'target_hit': pos['target_hit'],
                'trailing_active': pos['trailing_sl_active']
            }
        return None
    
    def close_position(self, order_id: str):
        """Mark position as closed"""
        if order_id in self.positions:
            self.positions[order_id]['status'] = 'CLOSED'
            self.logger.info(f"Position closed: {order_id}")
    
    def get_active_positions(self) -> Dict:
        """Get all active positions"""
        return {k: v for k, v in self.positions.items() if v['status'] == 'OPEN'}
    
    def get_daily_pnl(self) -> float:
        """Calculate total daily P&L"""
        total_pnl = 0.0
        for pos in self.positions.values():
            if pos['status'] == 'CLOSED':
                pnl = (pos['current_price'] - pos['entry_price']) * self.lot_size
                total_pnl += pnl
        return total_pnl
