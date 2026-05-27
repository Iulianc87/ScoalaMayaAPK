[app]
title = Scoala Mayei
package.name = scoalamaya
package.domain = org.test.scoalamaya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy,plyer
android.permissions = INTERNET, MICROPHONE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.archs = armeabi-v7a
android.gradle_dependencies = androidx.appcompat:appcompat:1.4.1
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
# Adăugăm acest parametru pentru a nu forța actualizarea SDK-ului
android.sdk_update = False
