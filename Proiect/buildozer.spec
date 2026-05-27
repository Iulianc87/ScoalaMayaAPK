[app]

title = ScoalaMaya
package.name = scoalamaya
package.domain = org.scoala

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.0

requirements = python3,kivy==2.2.1

orientation = portrait

fullscreen = 0

android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.build_tools_version = 34.0.0

android.accept_sdk_license = True
android.skip_update = True

android.archs = armeabi-v7a

log_level = 2

[buildozer]

warn_on_root = 1
