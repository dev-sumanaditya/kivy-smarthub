#imports - import Config before anything.
from kivy.config import Config
Config.set('kivy','keyboard_mode','dock')
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '400')
Config.set('kivy','desktop','0')
Config.set('kivy','exit_on_escape','0')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'borderless', '1')
# uncomment this in production
# Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'fbo', 'hardware')

from kivy.app import App
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition, FallOutTransition, RiseInTransition
from kivy.clock import Clock
import time
from kivy.animation import Animation

# behiaviours
from kivy.uix.behaviors import ButtonBehavior

# properties
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty

# Layouts
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy.uix.scatter import Scatter

# widgets
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.video import Video
from kivy.uix.image import Image
from kivy.uix.slider import Slider

# others
from pymitter import EventEmitter
import subprocess
import os

# event emitter
ee = EventEmitter()


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

    def getString():
        return DataClass.quoteString
    
    def setFontSize(num):
        DataClass.fontSize = num


# Loading Screen
class LoadingScreen(Screen):
    def __init__(self,**kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
    
    def on_enter(self, *args):
        self.displayScreenThenLeave()
    
    def displayScreenThenLeave(self):
        #schedued after 3 seconds
        Clock.schedule_once(self.changeScreen, 2.3)

    def changeScreen(self, *args):
        #now switch to main screen
        self.parent.transition = RiseInTransition()
        self.parent.current = "wifi_screen"

# connect to wifi screen.
def createNewConnection(name, SSID, password):
        config = """<?xml version=\"1.0\"?>
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>"""+name+"""</name>
            <SSIDConfig>
                <SSID>
                    <name>"""+SSID+"""</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>"""+password+"""</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>"""
        command = "netsh wlan add profile filename=\""+name+".xml\""+" interface=Wi-Fi"
        with open(name+".xml", 'w') as file:
            file.write(config)
        os.system(command)
class WifiScreen(Screen):
    def __init__(self,**kwargs):
        super(WifiScreen, self).__init__(**kwargs)
        results = subprocess.check_output(["netsh", "wlan", "show", "network"])
        results = results.decode("ascii") # needed in python 3
        results = results.replace("\r","")
        ls = results.split("\n")
        ssids2 = [k for k in ls if 'SSID' in k]
        print(ssids2)
        ssids = [v.strip() for k,v in (p.split(':') for p in ls if 'SSID' in p)]
        print(ssids)
        createNewConnection('Mojo-Home 5G', 'Mojo-Home 5G', 'mojojojo')
    
    
        


#  login screen
class LoginScreen(Screen):
    def __init__(self,**kwargs):
        super(LoginScreen, self).__init__(**kwargs)
    
    def click(self):
        print('clicked')

class LoginComponent(BoxLayout):
    def __init__(self,**kwargs):
        super(LoginComponent, self).__init__(**kwargs)
    
    
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

# carousel
class HomeScreen(Screen):
    pass

# Overlay section
class MenuBar(AnchorLayout):

    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.button = MenuButton()
        self.showMenu = True;
        self.add_widget(self.button)
        self.event = Clock.schedule_once(self.hide, 3)

    def toggleMenu(self):
        print('toggle clicked')
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
        print('clicked')
        self.parent.parent.parent.transition = FadeTransition()
        self.parent.parent.parent.current = "settings_screen"


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
        self.parent.current = "home_screen"

class BackButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(BackButton, self).__init__(**kwargs)
        self.size_hint = (0.05,1)
        self.padding = 5
        image = Image(source='./assets/icons/back.png', height=100, width=100)
        self.add_widget(image)
    
    def on_press(self):
        print('clicked')
        self.parent.parent.parent.parent.parent.transition = FallOutTransition()
        self.parent.parent.parent.parent.parent.current = "home_screen"

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
        @ee.on("font_changed_from_slider")
        def handler(arg):
            self.font_size = int(arg)



# Window Manager
class WindowManager(ScreenManager):
    pass

# main app render
kv = Builder.load_file('main.kv')

class MainApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    MainApp().run()