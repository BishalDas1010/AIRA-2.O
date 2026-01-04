#!/bin/bash
# keyboard.sh - Control Dell keyboard backlight

LED_PATH="/sys/class/leds/dell::kbd_backlight/brightness"

if [ ! -e "$LED_PATH" ]; then
    echo "❌ Keyboard backlight not found"
    exit 1
fi

case "$1" in
    on)
        echo 1 > "$LED_PATH"
        ;;
    off)
        echo 0 > "$LED_PATH"
        ;;
    *)
        echo "Usage: $0 {on|off}"
        exit 1
        ;;
esac

