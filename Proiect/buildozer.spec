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

android.api = 34
android.minapi = 24
android.sdk = 34
android.ndk = 25b

android.accept_sdk_license = True
android.skip_update = True
android.build_tools_version = 34.0.0

[buildozer]

log_level = 2
warn_on_root = 1
