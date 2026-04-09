[app]
title = Alzheimer's Aid
package.name = alz_aid
package.domain = org.alz.aid
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,db
source.include_patterns = assets/*,fonts/*,kv/*,data/*,screens/*
version = 1.0.0
# Requirements
requirements = python3,kivy==2.3.1,kivymd==1.2.0,requests,deep_translator,certifi,urllib3,plyer,sqlite3,android
orientation = portrait
fullscreen = 0
# Icons/Presplash (use existing if available)
# icon.filename = %(source.dir)s/assets/logo.png
# Android specific
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,VIBRATE,CALL_PHONE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
# Include architecture
android.archs = arm64-v8a, armeabi-v7a
# Allow custom fonts
android.add_src = fonts/noto.ttf
# Ensure database exists
# android.entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1
