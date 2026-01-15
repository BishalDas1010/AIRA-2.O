import pvporcupine
import pyaudio
import struct
import os
import signal
import sys
import json
import time
import subprocess
from vosk import Model, KaldiRecognizer
from difflib import SequenceMatcher
from datetime import datetime
import webbrowser
import urllib.parse
import requests
import re
from voskaModel import VoskEngine


class function_aira:
    def __init__(self,SOUND_EFFECT):
        self.SOUND_EFFECT=SOUND_EFFECT
    def pause_song(self):
        """Pause currently playing media"""
        os.system("playerctl pause")
        

    def resume_song(self):
        """Resume/play currently paused media"""
        os.system("playerctl play")
        

    def volume_up(self):
        """Increase system volume"""
        os.system("pactl set-sink-volume @DEFAULT_SINK@ +10%")
        os.system(self.SOUND_EFFECT)

    def volume_down(self):
        """Decrease system volume"""
        os.system("pactl set-sink-volume @DEFAULT_SINK@ -10%")
        os.system(self.SOUND_EFFECT)

    def date_today(self):
        """Speak the current date"""

    def get_battery_info(self):
        """Get battery percentage"""
        try:
            result = subprocess.run(
                "upower -i $(upower -e | grep BAT) | grep -E 'percentage' | awk '{print $2}'",
                shell=True,
                capture_output=True,
                text=True
            )
            battery_percent = result.stdout.strip()
            if battery_percent:
                return f"Battery is at {battery_percent}"
            else:
                return "Unable to get battery status"
        except Exception as e:
            return "Error checking battery"

    def airplane_mode_on(self):
        """Enable airplane mode (disable WiFi)"""
        os.system("nmcli radio wifi off")
        os.system(self.SOUND_EFFECT)

    def airplane_mode_off(self):
        """Disable airplane mode (enable WiFi)"""
        os.system("nmcli radio wifi on")
        os.system(self.SOUND_EFFECT)

    def brightness_up(self):
        """Increase screen brightness"""
        os.system("brightnessctl set +10%")
        os.system(self.SOUND_EFFECT)

    def brightness_down(self):
        """Decrease screen brightness"""
        os.system("brightnessctl set 10%-")
        os.system(self.SOUND_EFFECT)


    def play_song(self, song):
        """Play song on YouTube Music (with fallback to regular YouTube)"""
        query = urllib.parse.quote(song)
        
        try:
            # Try YouTube Music first
            music_search_url = f"https://music.youtube.com/search?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(music_search_url, headers=headers, timeout=5)
            html = response.text
            
            # Try multiple patterns for YouTube Music
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            
            if not video_ids:
                # Fallback: Try getting from regular YouTube
                print("🔄 Trying regular YouTube...")
                yt_search_url = f"https://www.youtube.com/results?search_query={query}+official+audio"
                response = requests.get(yt_search_url, headers=headers, timeout=5)
                html = response.text
                video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            
            if video_ids:
                # Open first result in YouTube Music
                music_url = f"https://music.youtube.com/watch?v={video_ids[0]}"
                print(f"🎵 Opening: {music_url}")
                webbrowser.open(music_url)
            else:
                # Last resort: direct search on YouTube Music
                print("⚠️ No video ID found, opening search page")
                webbrowser.open(f"https://music.youtube.com/search?q={query}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
    def next(self):
        os.system("playerctl next")

    def on_keyboard(self, script_path):
        os.system(f"{script_path} on")

    def off_keyboard(self, script_path):
        os.system(f"{script_path} off")

    def cpu_uses(self):
        """Get CPU usage percentage"""
        try:
            result = subprocess.run(
                "top -bn1 | grep 'Cpu(s)' | awk '{print 100 - $8}'",
                shell=True,
                capture_output=True,
                text=True
            )
            cpu_percent = result.stdout.strip()
            return cpu_percent if cpu_percent else "0"
        except Exception as e:
            return "0"
    
    #night mode on/off
    @staticmethod
    def night_mode_on():
        os.system("gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true")
    @staticmethod
    def night_mode_off():
        os.system("gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled false")


    #bluetooth feature 
    def bluetoot_on(self):
        os.system("bluetoothctl power on")
    def bluetooth_off(self):
        os.system("bluetoothctl power off")

    def function_screenshort(self):
        os.system("scrot")
        
