from functools import partial
import requests
import socket


#imports - import Config before any kivy packages.
from kivy.config import Config
Config.set('kivy','keyboard_mode','dock')
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '400')
# Config.set('kivy','desktop','0')
Config.set('kivy','exit_on_escape','0')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'borderless', '1')
# uncomment this in production
# Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'fbo', 'hardware')

from kivy.app import App
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, FallOutTransition, RiseInTransition
from kivy.clock import Clock
from kivy.core.window import Window

# behiaviours
from kivy.uix.behaviors import ButtonBehavior

# properties
from kivy.properties import ListProperty
from kivy.properties import NumericProperty

# Layouts
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# widgets
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.video import Video
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# others
from pymitter import EventEmitter
import nmcli
import socketio
from localStoragePy import localStoragePy

# event emitter
ee = EventEmitter()
# screen manager
sm = ScreenManager()

connected_to_server = False
sio = socketio.Client()

@sio.event
def connect():
    print("Connected!")
    global connected_to_server
    connected_to_server = True
@sio.event
def connect_error(data):
    print("The connection failed!")
    global connected_to_server
    connected_to_server = False
@sio.event
def disconnect():
    print("I'm disconnected!")
    global connected_to_server
    connected_to_server = False
@sio.on('NEW_QUOTE')
def handler(res):
    print('data received..')
    print(res)
    # ee.emit('quote_changed', res)
    
localStorage = localStoragePy('kivy.quotare.app', 'json')

# check if internet connection is truly available.
def is_internet_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def is_wifi_connected():
    try:
        status = nmcli.networking.connectivity()
        if(str(status) == 'NetworkConnectivity.FULL'):
            return True
        return False
    except Exception as e:
        return e

def get_saved_profiles():
    try:
        profiles = nmcli.connection()
        return profiles
    except Exception as e:
        return e

def scan_available_devices():
    devices  = nmcli.device.wifi('wlan0')
    return devices

def connect_to_saved_ap(ssid):
    try:
        res = nmcli.connection.up(ssid)
        return res
    except Exception as e:
        return e

def connect_to_new_ap(ssid, password):
    try:
        print('connecting to ap - ' + ssid)
        connect = nmcli.device.wifi_connect(ssid, password, 'wlan0');
        return connect
    except Exception as e:
        return e



# Main Data classes
class Theme:
    def __init__(self, type, source, font):
        self.type = type  # can be image | video | blank
        self.source = source
        self.font = font

class DataClass(object):
    themes = []
    themes.append(Theme('video','./assets/videos/1.mp4', './fonts/1.ttf'))
    themes.append(Theme('image', './assets/images/1.jpg', './fonts/2.ttf'))
    themes.append(Theme('image', './assets/images/i1.jpg', './fonts/7.otf'))
    themes.append(Theme('image', './assets/images/i2.jpg', './fonts/3.ttf'))
    themes.append(Theme('image', './assets/images/i3.jpg', './fonts/6.ttf'))
    themes.append(Theme('blank', '', './fonts/5.ttf'))

    quoteString = 'The only time you fail is when you fall down and stay down.'
    fontSize = 60

    def getString(self):
        return DataClass.quoteString
    
    def setFontSize(self, *args):
        DataClass.fontSize = args


# loading spinner
class LoadingSpinner(FloatLayout):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(LoadingSpinner, self).__init__(**kwargs)
        anim = Animation(angle = -360, duration=1) 
        anim += Animation(angle = -360, duration=1)
        anim.repeat = True
        anim.start(self)

    def on_angle(self, item, angle):
        if angle == -360:
            item.angle = 0

# Loading Screen
class LoadingScreen(Screen):

    def __init__(self,**kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
        print('Entered Loading screen');

    def on_enter(self, *args):
        Clock.schedule_once(self.check, 4);

    # remember to add some delay before changing screen. I spent 10 days trying to solve the problem - no screen with name "bla_bla_bla".
    # Adding the clock.schedule_once of 4 second worked. I think the screen manager takes time to register all the screens so changing the screen in init method or onenter will throw error.
    # thanks for taking time to read this - (Version 2.1.0 - 2nd commit)
    def check(self, *args):
        is_connected = is_wifi_connected()
        if(is_connected):
            print('already connected')
            self.check_auth_state_and_proceed()
        else:
            profiles = get_saved_profiles()
            if(len(profiles) > 0):
                for profile in profiles:
                    res = connect_to_saved_ap(profile.name)
                    if(res == None or 'None'):
                        print('connection success.')
                        self.check_auth_state_and_proceed()
                    else:
                        continue
                self.go_to_wifi_screen()
            else:
                self.go_to_wifi_screen()

    def go_to_wifi_screen(self, *args):
        sm.transition = RiseInTransition()
        sm.current = "wifi_screen"
                
    def check_auth_state_and_proceed(self, *args):
        token = localStorage.getItem('_token')
        sm.transition = RiseInTransition()
        if(token):
            sm.current = "home_screen"
        else:
            sm.current = "login_screen"

# connect to wifi screen.
class WifiScreen(Screen):
    check_status_attempt = 0;

    def __init__(self,**kwargs):
        super(WifiScreen, self).__init__(**kwargs)
        print('entered wifi screen')

    def back_button_handler(self, event):
        self.remove_widget(self.connect_layout)
        self.add_widget(self.scrlView)

    def connection_success_handler(self, *args):    
        token = localStorage.getItem('_token')
        sm.transition = RiseInTransition()
        if(token):
            sm.current = "home_screen"
        else:
            sm.current = "login_screen"

    # connect to wifi here
    def connect_button_handler(self, *args):
        password = self.password_input.text
        self.remove_widget(self.connect_layout)        
        # connecting layout
        self.connecting_layout = AnchorLayout(anchor_x='center', anchor_y="center")
        self.connecting_widget = GridLayout(cols=1, spacing=40)
        self.connecting_label = Label(font_size=28, color=[0.9,0.9,1,1], text="Connecting to - " + args.ssid, halign="center", valign="center")
        self.connecting_label2 = Label(font_size=14, color=[0.9,0.9,1,1], text="It usually takes 10 seconds to connect.")
        self.connecting_widget.add_widget(self.connecting_label)
        self.connecting_widget.add_widget(self.connecting_label2)
        self.connecting_layout.add_widget(self.connecting_widget)
        self.add_widget(self.connecting_layout)

        res = connect_to_new_ap(args.ssid, password)
        print(res);
        # handle connect success and failure here

    def button_callback_handler(self, *args):
        print('args >>>>>>>>>>>>>>>>>>>')
        print(args)
        self.remove_widget(self.scrlView)
        self.connect_layout = AnchorLayout(anchor_x='center', anchor_y="center")
        self.connect_widget = GridLayout(cols=1, padding=40, spacing=40, size_hint=[0.5,1])
        self.connecting_label = Label(font_size=28, color=[0.9,0.9,1,1], text="Connect to - " + args.ssid)
        self.password_input = TextInput(multiline=False, font_size=20, padding_x = [20,20], padding_y = [28,5], height=40, background_color=[0.4,0.4,0.7,0.4], foreground_color=[1,1,1,1], halign="center", hint_text="Enter password")
        self.cancel_button = Button(text="Back", size_hint_y=None, height=50, font_size=22, background_color=[0.4, 0.4, 0.4, 1], border=(6, 6, 6, 6))
        self.cancel_button.bind(on_press=self.back_button_handler)
        self.connect_button = Button(text="Connect", size_hint_y=None, height=50, font_size=22, background_color=[0.2, 0.2, 0.8, 1], border=(6, 6, 6, 6))
        connect_button_callback = partial(self.connect_button_handler, args)
        self.connect_button.bind(on_press=connect_button_callback)
        button_layout = GridLayout(cols=2, spacing=40)
        button_layout.add_widget(self.cancel_button)
        button_layout.add_widget(self.connect_button)
        self.connect_widget.add_widget(self.connecting_label)
        self.connect_widget.add_widget(self.password_input)
        self.connect_widget.add_widget(button_layout)
        self.connect_layout.add_widget(self.connect_widget)
        self.add_widget(self.connect_layout)

    
    def on_enter(self, *args):
        devices = scan_available_devices()
        self.scrlView = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.box = GridLayout(cols=3, spacing=25, size_hint_y=None, padding=25)
        self.box.bind(minimum_height=self.box.setter('height'))
        for device in devices:
            ssid = device.ssid
            buttoncallback = partial(self.button_callback_handler, device)
            btn = Button(text=str(ssid), size_hint_y=None, height=50, font_size=22, background_color=[0.9, 0.9, 0.9, 0.2], border=(6, 6, 6, 6))
            btn.bind(on_press=buttoncallback)
            if ssid is None:
                continue
            self.box.add_widget(btn)
        self.scrlView.add_widget(self.box)
        self.add_widget(self.scrlView)
    
    def on_leave(self, *args):
        self.clear_widgets()

#  login screen
class LoginScreen(Screen):

    def handle_login_failed(self, *args):
        self.remove_widget(self.logging_in_label)
        self.pass_input.text = ''
        self.add_widget(self.login_layout)
    
    def handle_login_success(self, *args):
        sm.current = 'home_screen'

    def handle_login(self, *args):
        if(len(self.email_input.text) < 1 or len(self.pass_input.text) < 1):
            return
        else:
            self.remove_widget(self.login_layout)
            self.logging_in_label = Label(text="Logging in, please wait", font_size=32, color=[1,1,1,1], halign="center")
            self.add_widget(self.logging_in_label)
            req = requests.post('https://quot-are.herokuapp.com/api/auth/login', data={'email': self.email_input.text, 'password': self.pass_input.text})            
            self.res = req.json()
            if(self.res['code'] == 200):
                self.logging_in_label.text = "Login Successful."
                self.pass_input.text = ''
                data = self.res['data']
                localStorage.setItem('_token', data['accessToken'])
                localStorage.setItem('_token_expiry', data['expiresIn'])
                user_req = requests.get('https://quot-are.herokuapp.com/api/user/me', headers={'Authorization': 'Bearer ' + data['accessToken']})
                user = user_req.json()
                localStorage.setItem('user_id', user['data']['id'])
                localStorage.setItem('user_email', user['data']['email'])
                localStorage.setItem('user_fname', user['data']['firstname'])
                localStorage.setItem('user_lname', user['data']['lastname'])

                Clock.schedule_once(self.handle_login_success, 4)
            else:
                self.logging_in_label.text = "Login Failed!"
                Clock.schedule_once(self.handle_login_failed, 4)
                

    def __init__(self,**kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        print('entered login screen')
        self.login_layout = AnchorLayout(anchor_x="center", anchor_y="center")
        grid_layout_main = GridLayout(cols=1, spacing=25, size_hint=[0.4, 0.85])
        grid_layout = GridLayout(cols=1, spacing=15, size_hint=[1, 0.7])
        main_label = Label(text="Login to your account", font_size=32, color=[1,1,1,1], halign="left")
        self.email_input = TextInput(multiline=False, font_size=24, padding_x = [20,20], padding_y = [20,5], height=40, background_color=[0.4,0.4,0.7,0.4], foreground_color=[1,1,1,1], halign="center", hint_text="Enter email")
        self.pass_input = TextInput(multiline=False, font_size=24, padding_x = [20,20], padding_y = [20,5], height=40, background_color=[0.4,0.4,0.7,0.4], foreground_color=[1,1,1,1], halign="center", hint_text="Enter password")
        btn = Button(text="Login", size_hint_y=None, size_hint=[1,0.22], font_size=28, background_color=[1, 1, 0.9, 0.4], border=(6, 6, 6, 6))
        btn.bind(on_press=self.handle_login)

        grid_layout.add_widget(main_label)
        grid_layout.add_widget(self.email_input)
        grid_layout.add_widget(self.pass_input)
        grid_layout_main.add_widget(grid_layout)
        grid_layout_main.add_widget(btn)

        self.login_layout.add_widget(grid_layout_main)

    def on_enter(self, *args):
        self.add_widget(self.login_layout)
    
    def on_leave(self, *args):
        self.clear_widgets()

# carousel
class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        print('home screen')
    # This is crashing if the network connection is not available.
    # def on_enter(self):
    #     print(localStorage.getItem('user_id'))
    #     sio.connect('https://quot-are.herokuapp.com/quote?id=' + str(localStorage.getItem('user_id')))
    #     print('my sid is', sio.sid)

        
    
# Overlay section
class MenuBar(AnchorLayout):

    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.button = MenuButton()
        self.showMenu = True;
        self.add_widget(self.button)
        self.event = Clock.schedule_once(self.hide, 3)

    def toggleMenu(self):
        if(self.showMenu == True):
            self.hide()
        else:
            self.show()
    
    def show(self):
        self.showMenu = True
        entryAnim = Animation(size_hint=(0.05,0.15), opacity=1, duration=0.2)
        entryAnim.start(self.button)
        self.event()

    def hide(self, *largs):
        self.showMenu = False
        exitAnim = Animation(size_hint=(0,0), opacity=0, duration=0.2)
        exitAnim.start(self.button)
        self.event.cancel()

class MenuButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.size_hint = (0.05,0.15)
        self.padding = 5
        image = Image(source='./assets/icons/menu.png', height=60, width=60)
        self.add_widget(image)
    
    def on_press(self):
        sm.transition = FadeTransition()
        sm.current = "settings_screen"

class SlideComponent(BoxLayout):
    def __init__(self, **kwargs):
        super(SlideComponent, self).__init__(**kwargs)
        
        carousel = Carousel(direction='right')
        for idx, i in enumerate(DataClass.themes):
            if(i.type == 'blank'):
                theme = BlankTheme()
                carousel.add_widget(theme, idx)
            elif(i.type == 'video'):
                theme = VideoTheme()
                carousel.add_widget(theme, idx)
            elif(i.type == 'image'):
                theme = ImageTheme(i.source, i.font)
                carousel.add_widget(theme, idx)
        self.add_widget(carousel)

    def handleSlideClick(self):
        self.mbr.toggleMenu()

class BlankTheme(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super(BlankTheme, self).__init__(**kwargs)
        layout = BoxLayout(width= 1280, height= 400, padding= [40,60,40,60])
        label2 = ShadowLabel(text= DataClass.quoteString, font_size= DataClass.fontSize, font_name="./fonts/1.ttf", tint= [.5, .5, .5, .5], color= [1,1,1,1], bold= True, text_size= [1240,360], halign= 'center', valign= 'middle', decal= [2, 0])
        layout.add_widget(label2)
        self.add_widget(layout)
    
    def on_press(self):
        self.parent.parent.parent.handleSlideClick()

class VideoTheme(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super(VideoTheme, self).__init__(**kwargs)
        video = Video(source="./assets/videos/1.mp4", play="True", options= {'eos': 'loop'}, height= 400, width= 1280)
        self.add_widget(video)
        
        layout = BoxLayout(width= 1280, height= 400, padding= [40,60,40,60], orientation= 'vertical')
        label = ShadowLabel(text= DataClass.quoteString, font_size= DataClass.fontSize, font_name="./fonts/5.ttf", tint= [.5, .5, .5, .5], color= [1,1,1,1], bold= True, text_size= [1240,360], halign= 'center', valign= 'middle', decal= [2, 0])
        layout.add_widget(label)
        self.add_widget(layout)
    
    def on_press(self):
        self.parent.parent.parent.handleSlideClick()

class ImageTheme(ButtonBehavior, Widget):
    def __init__(self, source, font, **kwargs):
        super(ImageTheme, self).__init__(**kwargs)
        self.source = source
        self.font = font

        image = Image(source=self.source, height= 400, width= 1280)
        self.add_widget(image)
        
        layout = BoxLayout(width= 1280, height= 400, padding= [40,60,40,60], orientation= 'vertical')
        label = ShadowLabel(text= DataClass.quoteString, font_size= DataClass.fontSize, font_name=self.font, tint= [.5, .5, .5, .5], color= [1,1,1,1], bold= True, text_size= [1240,360], halign= 'center', valign= 'middle', decal= [2, 0])
        layout.add_widget(label)
        self.add_widget(layout)
    
    def on_press(self):
        self.parent.parent.parent.handleSlideClick()


# Settings screen
class SettingsScreen(Screen):
    def __init__(self,**kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def goToHome(self):
        sm.current = "home_screen"
    
    def logout(self):
        localStorage.clear()
        sm.current = "wifi_screen"

    def connect_wifi(self):
        sm.current = "wifi_screen"

class BackButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(BackButton, self).__init__(**kwargs)
        self.size_hint = (0.05,1)
        self.padding = 5
        image = Image(source='./assets/icons/back.png', height=100, width=100)
        self.add_widget(image)

    def on_press(self):
        sm.transition = FallOutTransition()
        sm.current = "home_screen"

class SliderComponent(Slider):
    def __init__(self, **kwargs):
        super(SliderComponent, self).__init__(**kwargs)
        self.max = 100
        self.min = 20
        self.step = 1
        self.value = 50
        self.cursor_height = 46
        self.cursor_width = 46
    
    def on_touch_up(self, touch):
        self.fontLabel.setLabel(str(self.value))
        DataClass.fontSize = self.value
        ee.emit("font_changed_from_slider", str(self.value))

class SliderLabel(Label):
    def __init__(self, **kwargs):
        super(SliderLabel, self).__init__(**kwargs)
        self.text = str(DataClass.fontSize)
        self.font_size = 60
    
    def setLabel(self, label):
        self.text = label


# Shadow Label Component / main label component for quote slides
class ShadowLabel(Label):
    decal = ListProperty([0, 0])
    tint = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(ShadowLabel, self).__init__(**kwargs)
        @ee.on("quote_changed")
        def handler(arg):
            self.text = arg
        @ee.on("font_changed_from_slider")
        def handler(arg):
            self.font_size = int(arg)
class MainApp(App):
    def build(self):
        sm.add_widget(LoadingScreen(name='loading_screen'))
        sm.add_widget(WifiScreen(name='wifi_screen'))
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(HomeScreen(name='home_screen'))
        sm.add_widget(SettingsScreen(name='settings_screen'))        

        return sm

if __name__ == "__main__":
    MainApp().run()