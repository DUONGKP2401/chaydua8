import threading
import base64
import os
import time
import re
import requests
import socket
import sys
from time import sleep
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
from collections import deque, defaultdict, Counter
import random
import hashlib
import platform
import subprocess
import string
import urllib.parse

# Check và cài đặt các thư viện cần thiết
try:
    from colorama import init
    init(autoreset=True) # Vẫn giữ colorama init cho phần xác thực key
    import pytz
    from faker import Faker
    from requests import session
    # Thư viện Rich cho giao diện
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
except ImportError:
    print('__Đang cài đặt thư viện nâng cấp, vui lòng chờ...__')
    os.system("pip install requests colorama pytz faker pystyle bs4 rich")
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

# =====================================================================================
# PHẦN 1: MÃ NGUỒN TỪ KEYV8.PY (LOGIC XÁC THỰC - GIỮ NGUYÊN)
# =====================================================================================

# CONFIGURATION FOR VIP KEY
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display (từ keyv8.py)
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

# Đổi tên hàm banner của file banner.py để tránh xung đột
def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
{luc}████████╗ ██████╗░░ ██╗░░██╗░
{luc}╚══██╔══╝ ██╔══██╗░ ██║██╔╝░░
{luc}░░░██║░░░ ██║░░██║░ █████╔╝░░
{luc}░░░██║░░░ ██║░░██║░ ██╔═██╗░░
{luc}░░░██║░░░ ██║░░██║░ ██║░╚██╗░
{luc}░░░╚═╝░░░ ╚█████╔╝░ ╚═╝░░╚═╝░
{trang}══════════════════════════

{vang}Tool VIP V8
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# DEVICE ID AND IP ADDRESS FUNCTIONS
def get_device_id():
    """Generates a stable device ID based on CPU information."""
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]

    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    """Gets the user's public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    """Displays the banner, IP address, and Device ID."""
    authentication_banner() # Gọi hàm banner đã đổi tên
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")


# FREE KEY HANDLING FUNCTIONS
def luu_thong_tin_ip(ip, key, expiration_date):
    """Saves free key information to a json file."""
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('ip_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    """Loads free key information from the json file."""
    try:
        with open('ip_key.json', 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def kiem_tra_ip(ip):
    """Checks for a saved free key for the current IP."""
    data = tai_thong_tin_ip()
    if data and ip in data:
        try:
            expiration_date = datetime.fromisoformat(data[ip]['expiration_date'])
            # START MODIFICATION: Ensure expiration is timezone aware for correct checking
            hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            now_hcm = datetime.now(hcm_tz)
            # Make the stored date aware of the timezone
            aware_expiration = hcm_tz.localize(expiration_date)
            if aware_expiration > now_hcm:
                return data[ip]['key'], expiration_date
            # END MODIFICATION
        except (ValueError, KeyError, pytz.exceptions.AmbiguousTimeError, pytz.exceptions.NonExistentTimeError):
            return None, None
    return None, None

def generate_key_and_url(ip_address):
    """Creates a free key and a URL to bypass the link."""
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'VTD8{key1}{ip_numbers}'
    # START MODIFICATION: Set expiration to end of day in Ho Chi Minh timezone
    hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_hcm = datetime.now(hcm_tz)
    # This creates a naive datetime object representing the end of the day
    expiration_date = now_hcm.replace(hour=23, minute=59, second=59, microsecond=0).replace(tzinfo=None)
    # END MODIFICATION
    url = f'https://keyvtdv8.blogspot.com/2025/09/key-vtdv8_18.html?m={key}'
    return url, key, expiration_date

def get_shortened_link_phu(url):
    """Shortens the link to get the free key."""
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(ip_address):
    """Handles the entire process of obtaining a free key."""
    url, key, expiration_date = generate_key_and_url(ip_address)

    with ThreadPoolExecutor(max_workers=1) as executor:
        yeumoney_future = executor.submit(get_shortened_link_phu, url)
        yeumoney_data = yeumoney_future.result()

    if yeumoney_data and yeumoney_data.get('status') == "error":
        print(yeumoney_data.get('message'))
        return False, None

    link_key_yeumoney = yeumoney_data.get('shortenedUrl')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_yeumoney}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            sleep(2)
            luu_thong_tin_ip(ip_address, keynhap, expiration_date)
            # START MODIFICATION: Return key info
            key_info = {'type': 'Free', 'key': keynhap, 'expires': expiration_date}
            return True, key_info
            # END MODIFICATION
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_yeumoney}{trang}')


# VIP KEY HANDLING FUNCTIONS
def save_vip_key_info(device_id, key, expiration_date_str):
    """Saves VIP key information to a local cache file."""
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    """Loads VIP key information from the local cache file."""
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    """Calculates and displays the remaining time for a VIP key."""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()

        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    """Checks the VIP key from the URL on GitHub."""
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key (Status code: {response.status_code}).{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts

                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None

# MAIN AUTHENTICATION FLOW
# START MODIFICATION: Update function to return key info on success
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)

    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị cần thiết. Vui lòng kiểm tra kết nối mạng.{trang}")
        return False, None, None

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y').replace(hour=23, minute=59, second=59)
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                key_info = {'type': 'VIP', 'key': cached_vip_info['key'], 'expires': expiry_date}
                sleep(3)
                return True, device_id, key_info
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key. Vui lòng nhập lại key.{trang}")

    saved_key, expiration_date = kiem_tra_ip(ip_address)
    if saved_key:
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn. Mời bạn dùng tool...{trang}")
        key_info = {'type': 'Free', 'key': saved_key, 'expires': expiration_date}
        time.sleep(2)
        return True, device_id, key_info

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Dùng trong ngày){trang}")
        print(f"{trang}======================================")

        try:
            choice = input(f"{trang}[{do}<>{trang}] {xduong}Nhập lựa chọn của bạn: {trang}")
            print(f"{trang}═══════════════════════════════════")

            if choice == '1':
                vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP: {luc}')
                status, expiry_date_str = check_vip_key(device_id, vip_key_input)

                if status == 'valid':
                    print(f"{luc}Xác thực Key VIP thành công!{trang}")
                    save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                    display_remaining_time(expiry_date_str)
                    expiry_date_obj = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
                    key_info = {'type': 'VIP', 'key': vip_key_input, 'expires': expiry_date_obj}
                    sleep(3)
                    return True, device_id, key_info
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else:
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                success, key_info = process_free_key(ip_address)
                if success:
                    return True, device_id, key_info
                else:
                    return False, None, None

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except (KeyboardInterrupt):
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()
# END MODIFICATION

# =====================================================================================
# PHẦN 2: MÃ NGUỒN TOOL CHÍNH (ĐÃ NÂNG CẤP VÀ SỬA LỖI)
# =====================================================================================

console = Console()

NV = {
    1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'
}
ALL_NV_IDS = list(NV.keys())

# Lớp quản lý trạng thái chung (dùng cho việc tránh cược trùng)
class SharedStateManager:
    def __init__(self, api_endpoint, user_id):
        self.api_endpoint = api_endpoint
        self.user_id = user_id
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_shared_bets(self, issue_id):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get(str(issue_id), {})
            return {}
        except (requests.RequestException, json.JSONDecodeError):
            return {}

    def claim_bet(self, issue_id, bet_on_char):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            data = {}
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict):
                        data = {}
                except json.JSONDecodeError:
                    data = {}
            
            current_issue_num = int(issue_id)
            keys_to_delete = [key for key in data.keys() if not key.isdigit() or int(key) < current_issue_num - 5]
            for key in keys_to_delete:
                del data[key]

            issue_key = str(issue_id)
            if issue_key not in data:
                data[issue_key] = {}
            
            data[issue_key][str(bet_on_char)] = self.user_id

            requests.put(f"{self.api_endpoint}", data=json.dumps(data), headers=self.headers, timeout=5)
            return True
        except Exception:
            return False

# NÂNG CẤP: Logic AI mới
class LogicEngine:
    def __init__(self, state_manager, history_min_size=15):
        self.history = deque(maxlen=200)
        # START MODIFICATION: Add history for top 6 results
        self.history_top6 = deque(maxlen=200) 
        # END MODIFICATION
        self.state_manager = state_manager
        self.history_min_size = history_min_size
        self.last_bet_on = None
        self.losing_streak = 0

    # START MODIFICATION: Update add_result to handle full race result
    def add_result(self, result_list):
        if not result_list or len(result_list) < 6:
            return
        
        winner_id = result_list[0]
        top6_id = result_list[5] # The last one is top 6

        if winner_id in NV:
            self.history.append(winner_id)
        if top6_id in NV:
            self.history_top6.append(top6_id)
    # END MODIFICATION

    def record_win(self):
        self.losing_streak = 0
        self.last_bet_on = None

    def record_loss(self, bet_on):
        self.losing_streak += 1
        self.last_bet_on = bet_on

    def _get_frequencies(self, data):
        return Counter(data)

    def _get_transitions(self):
        transitions = defaultdict(Counter)
        for i in range(len(self.history) - 1):
            current_winner = self.history[i]
            next_winner = self.history[i+1]
            transitions[current_winner][next_winner] += 1
        return transitions

    def strategy_cold_hunter(self):
        if not self.history: return None
        seen_chars = set(self.history)
        unseen_chars = [nv_id for nv_id in ALL_NV_IDS if nv_id not in seen_chars]
        if unseen_chars: return random.choice(unseen_chars)
        
        last_seen_index = {char_id: -1 for char_id in ALL_NV_IDS}
        for i, char_id in enumerate(reversed(self.history)):
            if last_seen_index[char_id] == -1:
                last_seen_index[char_id] = len(self.history) - 1 - i
        
        return min(last_seen_index, key=last_seen_index.get)

    def strategy_anti_hot(self):
        recent_history = list(self.history)[-20:]
        if not recent_history: return None
        freq = self._get_frequencies(recent_history)
        return freq.most_common(1)[0][0]

    def strategy_transition_avoider(self):
        if len(self.history) < 2: return None
        last_winner = self.history[-1]
        transitions = self._get_transitions()
        if last_winner in transitions and transitions[last_winner]:
            return transitions[last_winner].most_common(1)[0][0]
        return self.strategy_anti_hot()

    def strategy_reverse_psychology(self):
        if not self.history: return None
        freq = self._get_frequencies(self.history)
        if len(freq) < len(ALL_NV_IDS):
            all_appeared = set(freq.keys())
            missing = [nv for nv in ALL_NV_IDS if nv not in all_appeared]
            return random.choice(missing)
        return freq.most_common()[-1][0]

    def analyze_and_select(self, issue_id):
        # START MODIFICATION: Logic to ban the character with the most top 6 finishes
        banned_character = None
        if len(self.history_top6) > 10: # Only ban if we have enough data
            top6_freq = self._get_frequencies(self.history_top6)
            banned_character = top6_freq.most_common(1)[0][0]
        
        # Create a list of allowed characters for betting
        allowed_nv_ids = [nv_id for nv_id in ALL_NV_IDS if nv_id != banned_character]
        # END MODIFICATION

        if len(self.history) < self.history_min_size:
            # START MODIFICATION: Choose from allowed characters
            return random.choice(allowed_nv_ids)
            # END MODIFICATION

        if self.losing_streak >= 3:
            strategy_choice = self.strategy_cold_hunter
        else:
            strategies = [self.strategy_anti_hot, self.strategy_transition_avoider, self.strategy_reverse_psychology, self.strategy_cold_hunter]
            strategy_choice = strategies[issue_id % len(strategies)]

        candidates = []
        main_candidate = strategy_choice()
        # START MODIFICATION: Ensure main candidate is not the banned one
        if main_candidate and main_candidate != banned_character: 
            candidates.append(main_candidate)
        # END MODIFICATION
        
        fallback_strategies = [self.strategy_cold_hunter, self.strategy_anti_hot, self.strategy_reverse_psychology]
        for strat in fallback_strategies:
            cand = strat()
            # START MODIFICATION: Ensure fallback candidates are not banned and not already in the list
            if cand and cand != banned_character and cand not in candidates:
                candidates.append(cand)
            # END MODIFICATION
        
        # START MODIFICATION: Fill remaining candidates from the allowed list
        while len(candidates) < len(allowed_nv_ids):
            rand_choice = random.choice(allowed_nv_ids)
            if rand_choice not in candidates:
                candidates.append(rand_choice)
        # END MODIFICATION

        if self.losing_streak > 0 and self.last_bet_on in candidates:
            candidates.remove(self.last_bet_on)
            candidates.append(self.last_bet_on)
        
        if self.state_manager:
            shared_bets = self.state_manager.get_shared_bets(issue_id)
            claimed_chars = [int(k) for k in shared_bets.keys()]

            for choice in candidates:
                if choice not in claimed_chars:
                    self.state_manager.claim_bet(issue_id, choice)
                    return choice
            
            # START MODIFICATION: Choose from allowed characters if all candidates are taken
            unclaimed = [nv for nv in allowed_nv_ids if nv not in claimed_chars]
            if unclaimed:
                final_choice = random.choice(unclaimed)
                self.state_manager.claim_bet(issue_id, final_choice)
                return final_choice
            # END MODIFICATION
        
        # If no candidates, return a random allowed choice as a last resort
        return candidates[0] if candidates else random.choice(allowed_nv_ids)


# =====================================================================================
# PHẦN GIAO DIỆN VÀ HIỂN THỊ (SỬA LỖI)
# =====================================================================================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def format_time(seconds):
    if seconds < 0: return "0 ngày 0 giờ 0 phút"
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} ngày {hours} giờ {minutes} phút"

def add_log(logs_deque, message):
    hanoi_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    timestamp = datetime.now(hanoi_tz).strftime('%H:%M:%S')
    # START MODIFICATION: Change append to appendleft to reverse log order
    logs_deque.appendleft(f"[grey70]{timestamp}[/grey70] {message}")
    # END MODIFICATION

# START MODIFICATION: Add helper function for key expiration countdown
def format_remaining_time(expiry_datetime):
    """Calculates and formats the remaining time for a key."""
    hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_hcm = datetime.now(hcm_tz)
    
    # The expiry_datetime is naive, so we localize it to the HCM timezone
    try:
        aware_expiry = hcm_tz.localize(expiry_datetime)
    except (pytz.exceptions.AmbiguousTimeError, pytz.exceptions.NonExistentTimeError):
        # Fallback for rare timezone transition issues
        aware_expiry = expiry_datetime
    
    delta = aware_expiry - now_hcm
    
    if delta.total_seconds() < 0:
        return "[bold red]Đã hết hạn[/bold red]"
        
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"[green]{days} ngày, {hours} giờ[/green]"
    else:
        return f"[yellow]{hours:02d}:{minutes:02d}:{seconds:02d}[/yellow]"
# END MODIFICATION

# SỬA LỖI: Viết lại hoàn toàn hàm generate_dashboard để sửa lỗi crash giao diện
# START MODIFICATION: Add key_info parameter to generate the new panel
def generate_dashboard(config, stats, wallet_asset, logs, coin_type, status_message, key_info) -> Panel:
    """Tạo giao diện hiển thị bằng Rich (phiên bản ổn định)."""
    
    total_games = stats['win'] + stats['lose']
    win_rate = (stats['win'] / total_games * 100) if total_games > 0 else 0
    profit = wallet_asset.get(coin_type, 0) - stats['asset_0']
    profit_str = f"[bold green]+{profit:,.4f}[/bold green]" if profit >= 0 else f"[bold red]{profit:,.4f}[/bold red]"

    stats_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    stats_table.add_column(style="cyan"); stats_table.add_column(style="white")
    stats_table.add_row("Phiên Bản", "LOGIC V8")
    stats_table.add_row("Lợi Nhuận", f"{profit_str} {coin_type}")
    stats_table.add_row("Tổng Trận", str(total_games))
    stats_table.add_row("Thắng / Thua", f"[green]{stats['win']}[/green] / [red]{stats['lose']}[/red] ({win_rate:.2f}%)")
    stats_table.add_row("Chuỗi Thắng", f"[green]{stats['streak']}[/green] (Max: {stats['max_streak']})")
    stats_table.add_row("Chuỗi Thua", f"[red]{stats['lose_streak']}[/red]")
    
    config_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    config_table.add_column(style="cyan"); config_table.add_column(style="yellow")
    config_table.add_row("Cược Cơ Bản", f"{config['bet_amount0']} {coin_type}")
    config_table.add_row("Hệ Số Gấp", str(config['heso']))
    config_table.add_row("Chế Độ Nghỉ", f"Chơi {config['delay1']} nghỉ {config['delay2']}")
    
    balance_table = Table(title="Số Dư", show_header=True, header_style="bold magenta", box=None)
    balance_table.add_column("Loại Tiền", style="cyan", justify="left")
    balance_table.add_column("Số Lượng", style="white", justify="right")
    balance_table.add_row("BUILD", f"{wallet_asset.get('BUILD', 0.0):,.4f}")
    balance_table.add_row("WORLD", f"{wallet_asset.get('WORLD', 0.0):,.4f}")
    balance_table.add_row("USDT", f"{wallet_asset.get('USDT', 0.0):,.4f}")

    # START MODIFICATION: Create the Key Information Panel
    key_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    key_table.add_column(style="cyan"); key_table.add_column(style="white")
    key_table.add_row("Loại Key", f"[bold yellow]{key_info.get('type', 'N/A')}[/bold yellow]")
    key_table.add_row("Key", str(key_info.get('key', 'N/A')))
    remaining_time_str = format_remaining_time(key_info.get('expires', datetime.now()))
    key_table.add_row("Còn Lại", remaining_time_str)
    key_panel = Panel(key_table, title="[bold]Thông Tin Key[/bold]", border_style="blue")
    # END MODIFICATION

    info_layout = Table.grid(expand=True)
    info_layout.add_column(ratio=1); info_layout.add_column(ratio=1)
    info_layout.add_row(Panel(stats_table, title="[bold]Thống Kê[/bold]", border_style="blue"), Panel(config_table, title="[bold]Cấu Hình[/bold]", border_style="blue"))
    # START MODIFICATION: Add the new key panel to the layout
    info_layout.add_row(Panel(balance_table, border_style="blue"), key_panel)
    # END MODIFICATION

    log_panel = Panel("\n".join(logs), title="[bold]Nhật Ký Hoạt Động[/bold]", border_style="green", height=12)
    status_panel = Panel(Align.center(Text(status_message, justify="center")), title="[bold]Trạng Thái[/bold]", border_style="yellow", height=3)
    
    main_grid = Table.grid(expand=True)
    main_grid.add_row(status_panel)
    main_grid.add_row(info_layout)
    main_grid.add_row(log_panel)
    
    dashboard = Panel(
        main_grid,
        title=f"[bold gold1]TOOL VIP V8[/bold gold1] - Thời gian chạy: {format_time(time.time() - config['start_time'])}",
        border_style="bold magenta"
    )
    return dashboard
# END MODIFICATION
# =====================================================================================
# CÁC HÀM LOGIC VÀ API
# =====================================================================================
def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        console.print(f"[cyan]Tìm thấy file dữ liệu đã lưu. Bạn có muốn sử dụng không? (y/n): [/cyan]", end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    console.print(f"\n[yellow]Hướng dẫn lấy link:\n1. Truy cập xworld.io và đăng nhập\n2. Vào game 'Chạy đua tốc độ'\n3. Copy link của trang game và dán vào đây[/yellow]")
    console.print(f"[cyan]📋 Vui lòng nhập link của bạn: [/cyan]", end=''); link = input()
    user_id = re.search(r'userId=(\d+)', link).group(1)
    secret_key = re.search(r'secretKey=([a-zA-Z0-9]+)', link).group(1)
    console.print(f"[green]    ✓ Lấy thông tin thành công! User ID: {user_id}[/green]")
    json_data = {'user-id': user_id, 'user-secret-key': secret_key}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def populate_initial_history(s, headers, logic_engine):
    console.print(f"\n[green]Đang lấy dữ liệu lịch sử ban đầu...[/green]")
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            for issue_data in reversed(response['data']['recent_10']):
                # START MODIFICATION: Pass the full result list
                logic_engine.add_result(issue_data['result'])
                # END MODIFICATION
            console.print(f"[green]✓ Nạp thành công lịch sử {len(response['data']['recent_10'])} ván.[/green]"); return True
    except Exception as e: console.print(f"[red]Lỗi khi nạp lịch sử: {e}[/red]")
    return False

def fetch_latest_issue_info(s, headers):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            latest_issue = response['data']['recent_10'][0]; return latest_issue['issue_id'], latest_issue
    except Exception: return None, None
    return None, None

def check_issue_result(s, headers, kq, ki):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        for issue in response['data']['recent_10']:
            if int(issue['issue_id']) == int(ki):
                actual_winner = issue['result'][0]; return actual_winner != kq, actual_winner
    except Exception: return None, None
    return None, None

def user_asset(s, headers):
    try:
        json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
        return s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data, timeout=5).json()['data']['user_asset']
    except Exception as e:
        console.print(f"[red]Lỗi khi lấy số dư: {e}. Thử lại...[/red]"); time.sleep(2); return user_asset(s, headers)

def bet_cdtd(s, headers, ki, kq, Coin, bet_amount, logs):
    try:
        bet_amount_randomized = round(bet_amount * random.uniform(0.995, 1.005), 8)
        json_data = {'issue_id': int(ki), 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': kq, 'bet_amount': bet_amount_randomized}
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data, timeout=10).json()
        
        if not (response.get('code') == 0 and response.get('msg') == 'ok'):
            log_msg = f"[red]Lỗi cược:[/red] [white]{response.get('msg', 'Không rõ lỗi')}[/white]"
            add_log(logs, log_msg)
        return response
    except requests.exceptions.RequestException as e:
        add_log(logs, f"[red]Lỗi mạng khi đặt cược:[/red] [white]{e}[/white]")
        return None

def get_user_input(prompt, input_type=float):
    while True:
        try:
            # SỬA LỖI: In câu hỏi bằng console.print để xử lý markup, sau đó gọi input()
            console.print(prompt, end="")
            value = input_type(input())
            return value
        except ValueError:
            console.print("[bold red]Định dạng không hợp lệ, vui lòng nhập lại một số.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Đã xảy ra lỗi: {e}. Vui lòng thử lại.[/bold red]")

# Vòng lặp chính của tool
# START MODIFICATION: Add key_info parameter to the main function
def main_cdtd(device_id, key_info):
    s = requests.Session()
    data = load_data_cdtd()
    headers = {'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'], 'user-agent': 'Mozilla/5.0'}

    clear_screen()
    
    asset = user_asset(s, headers)
    console.print(f"[cyan]Chọn loại tiền bạn muốn chơi:[/cyan]\n  1. USDT\n  2. BUILD\n  3. WORLD")
    while True:
        # SỬA LỖI: Tách `print` và `input` để hiển thị đúng màu
        console.print(f'[cyan]Nhập lựa chọn (1/2/3): [/cyan]', end="")
        x = input()
        if x in ['1', '2', '3']: 
            Coin = ['USDT', 'BUILD', 'WORLD'][int(x)-1]
            break
        else: 
            console.print(f"[red]Lựa chọn không hợp lệ, vui lòng nhập lại...[/red]")

    bet_amount0 = get_user_input(f'[cyan]Nhập số {Coin} muốn đặt ban đầu: [/cyan]', float)
    heso = get_user_input(f'[cyan]Nhập hệ số cược sau khi thua: [/cyan]', int)
    delay1 = get_user_input(f'[cyan]Chơi bao nhiêu ván thì nghỉ (999 nếu không nghỉ): [/cyan]', int)
    delay2 = get_user_input(f'[cyan]Nghỉ trong bao nhiêu ván: [/cyan]', int)
    
    console.print(f'[cyan]Bật chế độ chống cược trùng với người khác? (y/n): [/cyan]', end='');
    use_shared_state = input().lower() == 'y'

    SHARED_API_ENDPOINT = "https://api.jsonblob.com/api/jsonBlob/1286918519102373888"
    user_unique_id = hashlib.sha256(device_id.encode()).hexdigest()[:8]
    state_manager = SharedStateManager(SHARED_API_ENDPOINT, user_unique_id) if use_shared_state else None
    logic_engine = LogicEngine(state_manager)

    stats = {'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'lose_streak': 0, 'asset_0': asset.get(Coin, 0)}
    config = {'bet_amount0': bet_amount0, 'heso': heso, 'delay1': delay1, 'delay2': delay2, 'start_time': time.time()}
    logs = deque(maxlen=10); tong_van = 0

    populate_initial_history(s, headers, logic_engine); time.sleep(2)
    last_known_id, _ = fetch_latest_issue_info(s, headers)
    if not last_known_id:
        console.print(f"[red]Không thể lấy ID ván đầu tiên. Vui lòng kiểm tra lại mạng và API.[/red]")
        sys.exit()
    # START MODIFICATION: Pass key_info to the dashboard
    with Live(generate_dashboard(config, stats, asset, logs, Coin, "", key_info), console=console, screen=True, auto_refresh=False) as live:
        while True:
            try:
                current_asset = user_asset(s, headers)
                status_msg = f"Đang chờ ván #{last_known_id + 1} bắt đầu..."
                live.update(generate_dashboard(config, stats, current_asset, logs, Coin, status_msg, key_info), refresh=True)

                newly_completed_id = last_known_id
                while newly_completed_id == last_known_id:
                    time.sleep(1)
                    newly_completed_id, newly_completed_issue_data = fetch_latest_issue_info(s, headers)
                    if newly_completed_id is None: newly_completed_id = last_known_id

                last_known_id = newly_completed_id
                if newly_completed_issue_data and 'result' in newly_completed_issue_data:
                    # START MODIFICATION: Pass the full result list
                    logic_engine.add_result(newly_completed_issue_data['result'])
                    # END MODIFICATION

                target_issue_id = last_known_id + 1; tong_van += 1
                bet_amount = bet_amount0 * (heso ** stats['lose_streak'])

                cycle = delay1 + delay2
                pos = (tong_van - 1) % cycle if cycle > 0 else 0
                is_resting = pos >= delay1
                
                if not is_resting and random.random() < 0.05:
                    rest_msg = f"[yellow]💤 Bỏ qua ván này ngẫu nhiên để thay đổi hành vi.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    time.sleep(30); continue

                if is_resting:
                    rest_msg = f"[yellow]💤 Tạm nghỉ. Tiếp tục sau {cycle - pos} ván nữa.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    time.sleep(30); continue

                pre_bet_delay = random.uniform(2, 5)
                time.sleep(pre_bet_delay)

                kq = logic_engine.analyze_and_select(target_issue_id)
                
                response = bet_cdtd(s, headers, target_issue_id, kq, Coin, bet_amount, logs)
                if response and response.get('code') == 0:
                    start_wait_time = time.time()
                    while True:
                        result, actual_winner = check_issue_result(s, headers, kq, target_issue_id)
                        if result is not None: break
                        elapsed = int(time.time() - start_wait_time)
                        wait_message = f"⏳ Đợi KQ kì #{target_issue_id}: {elapsed}s. {NV.get(kq, kq)}.   [yellow]{bet_amount:,.4f} {Coin}[/yellow]"
                        live.update(generate_dashboard(config, stats, current_asset, logs, Coin, wait_message, key_info), refresh=True)
                        time.sleep(1)

                    if result:
                        logic_engine.record_win(); stats['win'] += 1; stats['streak'] += 1; stats['lose_streak'] = 0
                        stats['max_streak'] = max(stats['max_streak'], stats['streak'])
                        log_msg = (f"[bold green]THẮNG[/bold green] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[cyan]{NV.get(actual_winner, actual_winner)}[/cyan]'")
                    else:
                        logic_engine.record_loss(kq); stats['lose'] += 1; stats['lose_streak'] += 1; stats['streak'] = 0
                        log_msg = (f"[bold red]THUA[/bold red] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[red]{NV.get(actual_winner, actual_winner)}[/red]' (Trùng)")
                    add_log(logs, log_msg)
                    
                    final_asset = user_asset(s, headers)
                    live.update(generate_dashboard(config, stats, final_asset, logs, Coin, "", key_info), refresh=True)
                    time.sleep(random.uniform(5, 10))
            # END MODIFICATION
            except KeyboardInterrupt:
                console.print(f"\n\n[yellow]Đã dừng tool. Cảm ơn bạn đã sử dụng![/yellow]"); sys.exit()
            except Exception as e:
                import traceback; error_message = traceback.format_exc()
                # add_log(logs, f"[bold red]Lỗi nghiêm trọng. Đã ghi chi tiết vào 'error_log.txt'[/bold red]")
                # with open("error_log.txt", "a", encoding="utf-8") as f:
                #     f.write(f"--- Lỗi lúc {datetime.now()} ---\n{error_message}\n")
                time.sleep(10)

def show_banner():
    clear_screen()
    banner_text = Text.from_markup(f"""
[bold cyan]
 ████████╗██████╗ ██╗  ██╗
 ╚══██╔══╝██╔══██╗██║ ██╔╝
    ██║   ██║  ██║█████╔╝
    ██║   ██║  ██║██╔═██╗
    ██║   ██████╔╝██║  ██╗
    ╚═╝   ╚═════╝ ╚═╝  ╚═╝
[/bold cyan]
    """, justify="center")
    console.print(Panel(banner_text, border_style="magenta"))
    console.print(Align.center("[bold gold1]Tool VIP V8 - Khởi tạo thành công![/bold gold1]\n"))
    time.sleep(3)


if __name__ == "__main__":
    # START MODIFICATION: Unpack the new return values from authentication
    authentication_successful, device_id, key_info = main_authentication()

    if authentication_successful:
        show_banner()
        # Pass key_info to the main tool function
        main_cdtd(device_id, key_info)
    else:
        print(f"\n{do}Xác thực không thành công. Vui lòng chạy lại tool.{end}")
        sys.exit()
    # END MODIFICATION
