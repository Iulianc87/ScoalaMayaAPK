import random
import os
import time
import threading
import asyncio
import tempfile
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.core.text import LabelBase
from date_scoli import DATE_LOGICE
from plyer import tts

# =========================================================
# CONFIGURARE
# =========================================================
Window.size = (450, 750)
Window.clearcolor = get_color_from_hex('#F2E6F5')

FONT_PATH = "arial.ttf"
# Dacă nu găsește fontul în folderul aplicației, 
# Kivy va folosi fontul implicit, deci nu mai încerca să cauți în C:\Windows
if not os.path.exists(FONT_PATH):
    FONT_PATH = "" 
LabelBase.register(name='Arial', fn_regular=FONT_PATH)
F = 'Arial'

def culoare(hex): return get_color_from_hex(hex)

# =========================================================
# TTS
# =========================================================
def vorbeste(text):
    tts.speak(text)

# =========================================================
# DATE
# =========================================================
CUVINTE = []
for cat in DATE_LOGICE['cuvinte'].values():
    CUVINTE.extend(cat)

PROPOZITII = []
for cat in DATE_LOGICE['propozitii'].values():
    PROPOZITII.extend(cat)

TEXTE_DICTARE = DATE_LOGICE['texte_dictare']

# =========================================================
# HELPER UI
# =========================================================
def make_button(text, culoare_hex, height=55, font_size='18sp'):
    btn = Button(
        text=text, font_name=F, font_size=font_size, bold=True,
        background_normal='', background_color=culoare(culoare_hex),
        size_hint_y=None, height=height
    )
    return btn

def make_label(text, font_size='16sp', culoare_hex='#333333', bold=False, size_hint_y=None, height=None):
    lbl = Label(
        text=text, font_name=F, font_size=font_size, bold=bold,
        color=culoare(culoare_hex), halign='center', valign='middle'
    )
    lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0]*0.95, None)))
    if size_hint_y is not None:
        lbl.size_hint_y = size_hint_y
    if height is not None:
        lbl.size_hint_y = None
        lbl.height = height
    return lbl

# =========================================================
# ECRAN MENIU
# =========================================================
class EcranMeniu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        self.titlu = make_label('Scoala Mayei', '34sp', '#4A148C', bold=True, size_hint_y=0.25)
        subtitlu = make_label('Ce vrei sa exersam astazi?', '18sp', '#7B1FA2', size_hint_y=0.12)

        btn_scriere = make_button('SCRIERE', '#26A69A', height=70, font_size='20sp')
        btn_dictare = make_button('DICTARE', '#7B1FA2', height=70, font_size='20sp')
        btn_mate    = make_button('MATEMATICA', '#AB47BC', height=70, font_size='20sp')

        btn_scriere.bind(on_press=lambda x: self.start('scriere'))
        btn_dictare.bind(on_press=lambda x: self.start('dictare'))
        btn_mate.bind(on_press=lambda x: self.start('matematica'))

        self.titlu.bind(on_touch_down=self._tap_titlu)
        self._tap_count = 0
        self._tap_timer = None

        layout.add_widget(self.titlu)
        layout.add_widget(subtitlu)
        layout.add_widget(btn_scriere)
        layout.add_widget(btn_dictare)
        layout.add_widget(btn_mate)
        layout.add_widget(Label(size_hint_y=0.1))
        self.add_widget(layout)

    def _tap_titlu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self._tap_count += 1
            if self._tap_timer:
                self._tap_timer.cancel()
            if self._tap_count >= 3:
                self._tap_count = 0
                self.manager.current = 'adult'
            else:
                self._tap_timer = Clock.schedule_once(
                    lambda dt: setattr(self, '_tap_count', 0), 1.5
                )

    def start(self, tip):
        self.manager.get_screen('joc').porneste_joc(tip)
        self.manager.current = 'joc'

# =========================================================
# ECRAN JOC
# =========================================================
class EcranJoc(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tip_joc = ''
        self.numar = 0
        self.exercitii = []
        self.raspunsuri_corecte = 0
        self.lista_exercitii = []
        self.corect_curent = ''
        self.timer_event = None
        self.timp_ramas = 0
        self.incercari = 3
        self.faza = 'citire'

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)

        self.lbl_progres = make_label('', '15sp', '#7B1FA2', size_hint_y=None, height=30)
        self.lbl_info    = make_label('', '16sp', '#4A148C', bold=True, size_hint_y=None, height=50)
        self.lbl_timer   = make_label('', '22sp', '#C62828', bold=True, size_hint_y=None, height=40)

        from kivy.graphics import Color, RoundedRectangle
        cutie = BoxLayout(size_hint_y=0.35, padding=10)
        with cutie.canvas.before:
            Color(1, 1, 1, 1)
            self._rect = RoundedRectangle(size=cutie.size, pos=cutie.pos, radius=[18])
        cutie.bind(size=lambda i,v: setattr(self._rect, 'size', v))
        cutie.bind(pos=lambda i,v: setattr(self._rect, 'pos', v))

        self.lbl_exercitiu = make_label('', '28sp', '#000000', bold=True)
        cutie.add_widget(self.lbl_exercitiu)

        self.txt_input = TextInput(
            multiline=False, font_name=F, font_size='24sp',
            size_hint_y=None, height=55, halign='center'
        )

        self.btn_tts = make_button('Asculta din nou', '#00897B', height=50, font_size='16sp')
        self.btn_tts.bind(on_press=lambda x: vorbeste(self.corect_curent))

        self.btn_actiune = make_button('...', '#7B1FA2', height=60, font_size='18sp')
        self.btn_actiune.bind(on_press=self.actiune)

        self.lbl_feedback = make_label('', '15sp', '#C62828', size_hint_y=None, height=50)

        self.layout.add_widget(self.lbl_progres)
        self.layout.add_widget(self.lbl_info)
        self.layout.add_widget(self.lbl_timer)
        self.layout.add_widget(cutie)
        self.layout.add_widget(self.txt_input)
        self.layout.add_widget(self.btn_tts)
        self.layout.add_widget(self.btn_actiune)
        self.layout.add_widget(self.lbl_feedback)
        self.add_widget(self.layout)

    def porneste_joc(self, tip):
        self.tip_joc = tip
        self.numar = 0
        self.raspunsuri_corecte = 0
        self.lista_exercitii = []

        if tip == 'scriere':
            cuvinte = random.sample(CUVINTE, 5)
            propozitii = random.sample(PROPOZITII, 5)
            self.exercitii = [('cuvant', c) for c in cuvinte] + [('propozitie', p) for p in propozitii]
            random.shuffle(self.exercitii)
        elif tip == 'dictare':
            texte = random.sample(TEXTE_DICTARE, 10)
            self.exercitii = [('dictare', t) for t in texte]
        else:
            self.exercitii = [('matematica', None) for _ in range(10)]

        self.urmatorul_exercitiu()

    def urmatorul_exercitiu(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        if self.numar >= 10:
            ecran_adult = self.manager.get_screen('adult')
            ecran_adult.pregateste_verificare(self.lista_exercitii, self.tip_joc)
            self.manager.current = 'adult'
            return

        self.numar += 1
        self.faza = 'citire'
        self.lbl_feedback.text = ''
        self.txt_input.text = ''
        self.lbl_progres.text = f'Exercitiul {self.numar} din 10'

        tip_ex, continut = self.exercitii[self.numar - 1]

        if tip_ex == 'matematica':
            self._genereaza_matematica()
        elif tip_ex == 'cuvant':
            self._incepe_cuvant(continut)
        elif tip_ex == 'propozitie':
            self._incepe_propozitie(continut)
        elif tip_ex == 'dictare':
            self._incepe_dictare(continut)

    def _incepe_cuvant(self, cuvant):
        self.corect_curent = cuvant
        self.lista_exercitii.append({'tip': 'cuvant', 'text': cuvant, 'corect': None})
        self.lbl_info.text = 'Citeste cuvantul, apoi scrie-l pe caiet!'
        self.lbl_exercitiu.text = cuvant
        self.lbl_timer.text = '30 secunde'
        self.txt_input.opacity = 0
        self.btn_tts.opacity = 0
        self.btn_actiune.text = 'Am scris pe caiet!'
        self.btn_actiune.background_color = culoare('#26A69A')
        self.timp_ramas = 30
        self.timer_event = Clock.schedule_interval(self._tick_cuvant, 1)

    def _tick_cuvant(self, dt):
        self.timp_ramas -= 1
        self.lbl_timer.text = f'{self.timp_ramas} secunde'
        if self.timp_ramas <= 0:
            self.timer_event.cancel()
            self._ascunde_text()

    def _incepe_propozitie(self, propozitie):
        self.corect_curent = propozitie
        self.lista_exercitii.append({'tip': 'propozitie', 'text': propozitie, 'corect': None})
        self.lbl_info.text = 'Citeste propozitia! Poti asculta cu butonul de mai jos.'
        self.lbl_exercitiu.text = propozitie
        self.lbl_timer.text = '60 secunde'
        self.txt_input.opacity = 0
        self.btn_tts.opacity = 1
        self.btn_tts.text = 'Citeste cu voce tare'
        self.btn_actiune.text = 'Am scris pe caiet!'
        self.btn_actiune.background_color = culoare('#26A69A')
        self.timp_ramas = 60
        self.timer_event = Clock.schedule_interval(self._tick_propozitie, 1)

    def _tick_propozitie(self, dt):
        self.timp_ramas -= 1
        self.lbl_timer.text = f'{self.timp_ramas} secunde'
        if self.timp_ramas <= 0:
            self.timer_event.cancel()
            self._ascunde_text()

    def _ascunde_text(self):
        self.faza = 'scriere'
        self.lbl_exercitiu.text = '- - -'
        self.lbl_timer.text = ''
        self.btn_tts.opacity = 0
        self.lbl_info.text = 'Textul a disparut!\nApasa cand ai terminat de scris!'
        self.btn_actiune.text = 'Urmatorul'
        self.btn_actiune.background_color = culoare('#AB47BC')

    def _incepe_dictare(self, text):
        self.corect_curent = text
        self.lista_exercitii.append({'tip': 'dictare', 'text': text, 'corect': None})
        self.lbl_info.text = 'Asculta si scrie pe caiet!'
        self.lbl_exercitiu.text = text
        self.lbl_timer.text = ''
        self.txt_input.opacity = 0
        self.btn_tts.opacity = 1
        self.btn_tts.text = 'Asculta din nou'
        self.btn_actiune.text = 'Am scris pe caiet!'
        self.btn_actiune.background_color = culoare('#26A69A')
        vorbeste(text)

    def _genereaza_matematica(self):
        self.faza = 'matematica'
        self.incercari = 3
        self.txt_input.opacity = 1
        self.btn_tts.opacity = 0
        self.lbl_timer.text = ''

        operatie = random.choice(['+', '-'])
        stil = random.choice(['orizontal', 'vertical'])

        if operatie == '+':
            n1 = random.randint(10, 99)
            n2 = random.randint(1, 99)
            corect = n1 + n2
        else:
            n1 = random.randint(20, 99)
            n2 = random.randint(1, n1)
            corect = n1 - n2

        self.corect_curent = str(corect)
        self._n1, self._n2, self._operatie = n1, n2, operatie
        self.lista_exercitii.append({
            'tip': 'matematica', 'n1': n1, 'n2': n2,
            'op': operatie, 'corect': corect, 'rezultat_copil': None
        })

        if stil == 'vertical':
            self.lbl_info.text = 'Calculeaza! Scrie una sub alta pe caiet!'
            self.lbl_exercitiu.text = f'  {n1}\n{operatie} {n2}\n------'
        else:
            self.lbl_info.text = 'Calculeaza pe caiet!'
            self.lbl_exercitiu.text = f'{n1} {operatie} {n2} = ?'

        self.btn_actiune.text = f'Trimite raspunsul  (incercari: {self.incercari})'
        self.btn_actiune.background_color = culoare('#7B1FA2')
        self.txt_input.input_filter = 'int'
        self.txt_input.text = ''

    def actiune(self, instance):
        if self.tip_joc == 'matematica' or self.faza == 'matematica':
            self._verifica_matematica()
        elif self.faza == 'citire':
            if self.timer_event:
                self.timer_event.cancel()
            self._ascunde_text()
        else:
            self.urmatorul_exercitiu()

    def _verifica_matematica(self):
        raspuns = self.txt_input.text.strip()
        if not raspuns:
            self.lbl_feedback.text = 'Scrie un raspuns!'
            return

        try:
            e_corect = int(raspuns) == int(self.corect_curent)
        except ValueError:
            e_corect = False

        if e_corect:
            self.lista_exercitii[-1]['rezultat_copil'] = raspuns
            self.lista_exercitii[-1]['corect_final'] = True
            self.raspunsuri_corecte += 1
            self.lbl_feedback.text = 'Bravo! Corect!'
            Clock.schedule_once(lambda dt: self.urmatorul_exercitiu(), 1)
        else:
            self.incercari -= 1
            self.lista_exercitii[-1]['rezultat_copil'] = raspuns
            if self.incercari > 0:
                n1, n2, op = self._n1, self._n2, self._operatie
                if op == '-':
                    u1, u2 = n1 % 10, n2 % 10
                    if u1 < u2:
                        hint = 'Ai nevoie de imprumut la unitati!'
                    else:
                        hint = 'Scade unitatile si zecile separat!'
                else:
                    hint = 'Aduna unitatile intai!'
                self.lbl_feedback.text = f'Mai incearca! Incercari ramase: {self.incercari}\n{hint}'
                self.btn_actiune.text = f'Trimite raspunsul  (incercari: {self.incercari})'
                self.txt_input.text = ''
            else:
                self.lista_exercitii[-1]['corect_final'] = False
                self.lbl_feedback.text = f'Raspuns corect era: {self.corect_curent}'
                Clock.schedule_once(lambda dt: self.urmatorul_exercitiu(), 2)

# =========================================================
# ECRAN ADULT
# =========================================================
class EcranAdult(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exercitii = []
        self.index_curent = 0
        self.scor = 0
        self.tip_joc = ''
        self.mod = 'asteapta'
        self._tap_count = 0
        self._tap_timer = None

        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        self.lbl_titlu = make_label(
            'Scoala Mayei', '30sp', '#4A148C', bold=True,
            size_hint_y=None, height=80
        )
        self.lbl_titlu.bind(on_touch_down=self._tap_titlu)

        self.lbl_mesaj = make_label(
            'Bravo! Ai terminat!\n\nCheama un adult sa verifice caietul!',
            '20sp', '#7B1FA2', size_hint_y=0.4
        )

        self.lbl_hint = make_label(
            '( Adultul apasa de 3 ori pe titlu )',
            '13sp', '#AAAAAA', size_hint_y=None, height=30
        )

        self.lbl_exercitiu_adult = make_label('', '20sp', '#000000', bold=True, size_hint_y=0.3)
        self.lbl_progres_adult = make_label('', '15sp', '#7B1FA2', size_hint_y=None, height=30)

        self.btn_corect = make_button('Corect', '#2E7D32', height=65, font_size='20sp')
        self.btn_gresit = make_button('Gresit', '#C62828', height=65, font_size='20sp')
        self.btn_corect.bind(on_press=lambda x: self._raspuns_adult(True))
        self.btn_gresit.bind(on_press=lambda x: self._raspuns_adult(False))

        self.layout.add_widget(self.lbl_titlu)
        self.layout.add_widget(self.lbl_mesaj)
        self.layout.add_widget(self.lbl_hint)
        self.layout.add_widget(self.lbl_progres_adult)
        self.layout.add_widget(self.lbl_exercitiu_adult)
        self.layout.add_widget(self.btn_corect)
        self.layout.add_widget(self.btn_gresit)
        self.add_widget(self.layout)

        self._mod_asteapta()

    def _tap_titlu(self, instance, touch):
        if instance.collide_point(*touch.pos) and self.mod == 'asteapta':
            self._tap_count += 1
            if self._tap_timer:
                self._tap_timer.cancel()
            if self._tap_count >= 3:
                self._tap_count = 0
                self._mod_verifica()
            else:
                self._tap_timer = Clock.schedule_once(
                    lambda dt: setattr(self, '_tap_count', 0), 1.5
                )

    def pregateste_verificare(self, exercitii, tip_joc):
        self.tip_joc = tip_joc
        self.index_curent = 0
        self.scor = 0

        if tip_joc == 'matematica':
            self.exercitii = [e for e in exercitii if not e.get('corect_final', True)]
            self.scor = sum(1 for e in exercitii if e.get('corect_final', False))
        else:
            self.exercitii = exercitii

        self._mod_asteapta()

    def _mod_asteapta(self):
        self.mod = 'asteapta'
        self.lbl_mesaj.opacity = 1
        self.lbl_hint.opacity = 1
        self.lbl_exercitiu_adult.opacity = 0
        self.lbl_progres_adult.opacity = 0
        self.btn_corect.opacity = 0
        self.btn_gresit.opacity = 0

    def _mod_verifica(self):
        self.mod = 'verifica'
        self.lbl_mesaj.opacity = 0
        self.lbl_hint.opacity = 0
        self.lbl_exercitiu_adult.opacity = 1
        self.lbl_progres_adult.opacity = 1
        self.btn_corect.opacity = 1

        if self.tip_joc == 'matematica':
            if not self.exercitii:
                self._arata_rezultat()
                return
            self.btn_gresit.opacity = 0
            self._arata_exercitiu_adult()
        else:
            self.btn_gresit.opacity = 1
            self._arata_exercitiu_adult()

    def _arata_exercitiu_adult(self):
        if self.index_curent >= len(self.exercitii):
            self._arata_rezultat()
            return

        ex = self.exercitii[self.index_curent]
        total = len(self.exercitii)
        self.lbl_progres_adult.text = f'Exercitiul {self.index_curent + 1} din {total}'

        if ex['tip'] == 'matematica':
            self.btn_corect.text = 'Urmatorul'
            n1, n2, op = ex['n1'], ex['n2'], ex['op']
            corect = ex['corect']
            u1, u2 = n1 % 10, n2 % 10
            if op == '-' and u1 < u2:
                explicatie = f"La {n1} - {n2} = {corect}\nCifrele unitatilor s-au certat!\n{u1} e prea mic, trebuie imprumutat de la zeci!"
            elif op == '-':
                explicatie = f"La {n1} - {n2} = {corect}\nScadem unitatile si zecile separat,\naliniind cifrele una sub alta!"
            else:
                explicatie = f"La {n1} + {n2} = {corect}\nAdunam unitatile, daca trece de 9\ntinem minte zecimea si o adunam la zeci!"
            self.lbl_exercitiu_adult.text = explicatie
        else:
            self.lbl_exercitiu_adult.text = ex['text']

    def _raspuns_adult(self, corect):
        if self.tip_joc != 'matematica':
            if corect:
                self.scor += 1
        self.index_curent += 1
        if self.index_curent >= len(self.exercitii):
            self._arata_rezultat()
        else:
            self._arata_exercitiu_adult()

    def _arata_rezultat(self):
        self.manager.get_screen('rezultat').afiseaza(self.scor, self.tip_joc)
        self.manager.current = 'rezultat'

# =========================================================
# ECRAN REZULTAT
# =========================================================
class EcranRezultat(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=25, spacing=20)

        self.lbl_animal = make_label('', '36sp', '#4A148C', bold=True, size_hint_y=0.25)
        self.lbl_nota   = make_label('', '26sp', '#4A148C', bold=True, size_hint_y=0.15)
        self.lbl_mesaj  = make_label('', '18sp', '#7B1FA2', size_hint_y=0.35)

        btn_meniu = make_button('Inapoi la Meniu', '#4A148C', height=60)
        btn_meniu.bind(on_press=lambda x: setattr(self.manager, 'current', 'meniu'))

        layout.add_widget(self.lbl_animal)
        layout.add_widget(self.lbl_nota)
        layout.add_widget(self.lbl_mesaj)
        layout.add_widget(btn_meniu)
        self.add_widget(layout)

    def afiseaza(self, scor, tip_joc):
        nota = scor
        if nota >= 9:
            animal = 'UNICORN !'
            mesaj = 'Extraordinar! Esti o campioana!\nMaya cea isteata!'
        elif nota >= 6:
            animal = 'Pisicuta !'
            mesaj = 'Foarte bine!\nPisicuta te aplauda!'
        elif nota >= 4:
            animal = 'Puisor !'
            mesaj = 'Bine! Puisorul cel mic\neste mandru de tine!'
        else:
            animal = 'Floricea !'
            mesaj = 'Mai exersam impreuna!\nIn fiecare zi esti mai buna!'

        self.lbl_animal.text = animal
        self.lbl_nota.text   = f'Nota ta: {nota} din 10'
        self.lbl_mesaj.text  = mesaj

# =========================================================
# APP
# =========================================================
class ScoalaMayeiApp(App):
    def build(self):
        self.title = 'Scoala Mayei'
        sm = ScreenManager()
        sm.add_widget(EcranMeniu(name='meniu'))
        sm.add_widget(EcranJoc(name='joc'))
        sm.add_widget(EcranAdult(name='adult'))
        sm.add_widget(EcranRezultat(name='rezultat'))
        return sm

if __name__ == '__main__':
    ScoalaMayeiApp().run()