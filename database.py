import json
import os
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta

class ModerationDB:
    def __init__(self, db_file: str = "moderation_data.json"):
        self.db_file = db_file
        self.data = self.load_data()
        self.on_data_change_callbacks: List[Callable] = []
    
    def add_data_change_callback(self, callback: Callable):
        """Add a callback to be called when data changes"""
        self.on_data_change_callbacks.append(callback)
    
    def notify_data_change(self):
        """Notify all callbacks that data has changed"""
        for callback in self.on_data_change_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in data change callback: {e}")
    
    def load_data(self) -> Dict:
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {
            'warnings': {},
            'mutes': {},
            'bans': {},
            'kick_log': []
        }
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
        # Notify that data has changed
        self.notify_data_change()
    
    def get_moderation_stats(self) -> Dict[str, any]:
        """Get current moderation statistics"""
        warnings = self.data.get('warnings', {})
        mutes = self.data.get('mutes', {})
        bans = self.data.get('bans', {})
        kicks = self.data.get('kick_log', [])
        
        # Count active mutes (not expired)
        active_mutes = 0
        for mute in mutes.values():
            if 'expires_at' in mute:
                try:
                    expires_at = datetime.fromisoformat(mute['expires_at'])
                    if expires_at > datetime.now():
                        active_mutes += 1
                except:
                    pass
        
        return {
            'total_warnings': sum(len(warns) for warns in warnings.values()),
            'total_users_warned': len(warnings),
            'active_mutes': active_mutes,
            'total_bans': len(bans),
            'total_kicks': len(kicks),
            'timestamp': datetime.now().isoformat()
        }
    
    def add_warning(self, user_id: int, moderator_id: int, reason: str):
        """Add a warning for a user"""
        user_id = str(user_id)
        if user_id not in self.data['warnings']:
            self.data['warnings'][user_id] = []
        
        warning = {
            'reason': reason,
            'moderator_id': moderator_id,
            'timestamp': datetime.now().isoformat(),
            'warning_id': len(self.data['warnings'][user_id]) + 1
        }
        
        self.data['warnings'][user_id].append(warning)
        self.save_data()
        return warning
    
    def get_warnings(self, user_id: int) -> List[Dict]:
        """Get all warnings for a user"""
        user_id = str(user_id)
        return self.data['warnings'].get(user_id, [])
    
    def clear_warnings(self, user_id: int):
        """Clear all warnings for a user"""
        user_id = str(user_id)
        if user_id in self.data['warnings']:
            del self.data['warnings'][user_id]
            self.save_data()
    
    def add_mute(self, user_id: int, moderator_id: int, duration: int, reason: str):
        """Add a mute record"""
        user_id = str(user_id)
        mute = {
            'moderator_id': moderator_id,
            'duration': duration,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=duration)).isoformat()
        }
        
        self.data['mutes'][user_id] = mute
        self.save_data()
        return mute
    
    def remove_mute(self, user_id: int):
        """Remove a mute record"""
        user_id = str(user_id)
        if user_id in self.data['mutes']:
            del self.data['mutes'][user_id]
            self.save_data()
    
    def get_mute(self, user_id: int) -> Optional[Dict]:
        """Get mute record for a user"""
        user_id = str(user_id)
        return self.data['mutes'].get(user_id)
    
    def add_ban(self, user_id: int, moderator_id: int, reason: str):
        """Add a ban record"""
        user_id = str(user_id)
        ban = {
            'moderator_id': moderator_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        self.data['bans'][user_id] = ban
        self.save_data()
        return ban
    
    def remove_ban(self, user_id: int):
        """Remove a ban record"""
        user_id = str(user_id)
        if user_id in self.data['bans']:
            del self.data['bans'][user_id]
            self.save_data()
    
    def log_kick(self, user_id: int, moderator_id: int, reason: str):
        """Log a kick action"""
        kick_log = {
            'user_id': user_id,
            'moderator_id': moderator_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        self.data['kick_log'].append(kick_log)
        self.save_data()
        return kick_log
