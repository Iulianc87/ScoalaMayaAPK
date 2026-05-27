[app]
title = Scoala Mayei
package.name = scoalamaya
package.domain = org.test.scoalamaya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0

# Biblioteci necesare
requirements = python3,kivy,plyer

# Permisiuni necesare pentru Android
android.permissions = INTERNET, MICROPHONE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Setări pentru telefoane mai vechi (G7 / J4+)
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = armeabi-v7a

# Orientare ecran
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1