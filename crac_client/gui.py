from re import T
import config
from crac_protobuf.button_pb2 import (
    ButtonLabel,
    ButtonKey,
)
from crac_client.loc import _name
from gui_constants import GuiLabel
import logging
import math
import PySimpleGUI as sg  # type: ignore
from tkinter import PhotoImage, NW
from typing import Tuple
from typing import Dict


logger = logging.getLogger(__name__)


class Gui:

    def __init__(self):
        self.east_steps = 0
        self.west_steps = 0
        self.n_step_corsa = config.Config.getInt('n_step_corsa', "encoder_step")
        self.alt_max_tend_e = config.Config.getInt("max_est", "tende")
        self.alt_max_tend_w = config.Config.getInt("max_west", "tende")
        self.alt_min_tend_e = config.Config.getInt("park_est", "tende")
        self.alt_min_tend_w = config.Config.getInt("park_west", "tende")
        self.alpha_min_conf = config.Config.getInt("alpha_min", "tende")
        self.increm_e = (self.alt_max_tend_e - self.alt_min_tend_e) / self.n_step_corsa
        self.increm_w = (self.alt_max_tend_w - self.alt_min_tend_w) / self.n_step_corsa
        self.conv = 2 * math.pi / 360  # conversion from degrees to radians for applying math trigonometric algorithms
        self.tenda_e = None
        self.line2_e = None
        self.line3_e = None
        self.line4_e = None
        self.tenda_w = None
        self.line2_w = None
        self.line3_w = None
        self.line4_w = None
        self.image = None

        self.l = 390
        self.t = self.l / 4.25
        self.delta_pt = 1.5 * self.t
        self.h = int(self.l / 1.8)
        self.was_light_turned_on = False
#        sg.theme('Dark')

        theme_dict = {
            'BACKGROUND': '#313030',
            'TEXT': '#FFFFFF',
            'INPUT': '#F2EFE8',
            'TEXT_INPUT': '#000000',
            'SCROLL': '#F2EFE8',
            'BUTTON': ('#000000', '#C2D4D8'),
            'PROGRESS': ('#FFFFFF', '#C7D5E0'),
            'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0
        }

        # sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
        sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
        sg.theme('Dashboard')

        BORDER_COLOR = '#C7D5E0'
        PAD = (2, 2)
        PAD_LEFT_INSIDE = (1, 1), (1, 1)
        PAD_DOWN = (3, 0)
        FONT = 'Any 12'
        SIZE_GAUGE = (20, 20)
        FONT_BUTTON_CAM=("Helvetica", 8)
        
        block_3T = [
            [sg.Text('Controllo 3T - Tetto Telescopio Tende', font=FONT)],
            [
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_CLOSE), key=ButtonKey.KEY_ROOF, metadata="OPEN", disabled=False, size=(8, 1), tooltip="apre il tetto", button_color=("white", "red")),
                ]]), title="Tetto", pad=PAD_DOWN),
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_TELESCOPE_DISCONNECTED), key=ButtonKey.KEY_TELESCOPE_CONNECTION_TOGGLE, metadata="TELESCOPE_CONNECT", disabled=True, size=(10, 1), tooltip='connetti crac al telescopio', button_color=("white", "red")),
                    sg.Button(_name(ButtonLabel.LABEL_SYNC), key=ButtonKey.KEY_SYNC, metadata="SYNC", disabled=True, size=(8, 1), tooltip='sincronizza il telescopio sulle coordinate di park', button_color=("white", "red")),
                    sg.Button(_name(ButtonLabel.LABEL_PARK), key=ButtonKey.KEY_PARK, metadata="PARK_POSITION", disabled=True, size=(8, 1), tooltip='porta il telescopio in posizione di park e disattiva il tracking', button_color=("white", "red")),
                    sg.Button(_name(ButtonLabel.LABEL_FLAT), key=ButtonKey.KEY_FLAT, metadata="FLAT_POSITION", disabled=True, size=(8, 1) , tooltip='porta il telescopio in posizione di flat e disattiva il tracking con il pannello spento', button_color=("white", "red"))
                ]]), title="Telescopio", pad=PAD_DOWN),
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_DISABLE), key=ButtonKey.KEY_CURTAINS, metadata="ENABLE", disabled=True, size=(8, 1), tooltip='clicca per attivare le tendine', button_color=("white", "red")),
                    sg.Button(_name(ButtonLabel.LABEL_CALIBRATE), key=ButtonKey.KEY_CALIBRATE, metadata="CALIBRATE_CURTAINS", disabled=True,  size=(10, 1), tooltip='clicca per calibrare le tendine', button_color=("white", "red"))
                ]]), title="Tende", pad=PAD_DOWN)
            ]
        ]
        
        block_video = [
            [sg.Text('Videocamere', font=FONT)],
            [
                sg.Column(layout=(
                    [
                        sg.Column(layout=(
                            [sg.pin(
                                sg.Frame(layout=([[
                                    sg.Button(_name(ButtonLabel.LABEL_CAMERA_DISCONNECTED), key=ButtonKey.KEY_CAMERA1_CONNECTION, metadata="CAMERA_CONNECT", disabled=True, size=(10, 1), tooltip="connetti alla videocamera", button_color=("white", "red")),
                                    sg.Button(_name(ButtonLabel.LABEL_CAMERA_HIDDEN), key=ButtonKey.KEY_CAMERA1_DISPLAY, metadata="CAMERA_SHOW", disabled=True, size=(8, 1), tooltip="mostra la videocamera", button_color=("white", "red")),
                                    sg.Button(_name(ButtonLabel.LABEL_CAMERA_IR_DISABLED), key=ButtonKey.KEY_CAMERA1_IR_TOGGLE, metadata="CAMERA_IR_ENABLE", disabled=False, size=(10, 1), tooltip="attiva o disattiva l'infrarosso", button_color=("white", "red")),
                                ]]), title="Camera 1", pad=PAD_DOWN, key="camera1"),
                            shrink=True)],
                            [sg.pin(
                                sg.Frame(layout=([[
                                    sg.Button(_name(ButtonLabel.LABEL_CAMERA_DISCONNECTED), key=ButtonKey.KEY_CAMERA2_CONNECTION, metadata="CAMERA_CONNECT", disabled=True, size=(10, 1), tooltip="connetti alla videocamera", button_color=("white", "red")),
                                    sg.Button(_name(ButtonLabel.LABEL_CAMERA_HIDDEN), key=ButtonKey.KEY_CAMERA2_DISPLAY, metadata="CAMERA_SHOW", disabled=True, size=(8, 1), tooltip="mostra la videocamera", button_color=("white", "red")),
                                    sg.Button(_name(ButtonLabel.LABEL_CAMERA_IR_DISABLED), key=ButtonKey.KEY_CAMERA2_IR_TOGGLE, metadata="CAMERA_IR_ENABLE", disabled=False, size=(10, 1), tooltip="attiva o disattiva l'infrarosso", button_color=("white", "red")),
                                ]]), title="Camera 2", pad=PAD_DOWN, key="camera2"),
                            shrink=True)],
                            [sg.pin(
                                sg.Frame(layout=([[
                                    sg.Checkbox('Abilita Autodisplay', key="autodisplay", default=True, tooltip="le camere mostrano automaticamente il video quando il telescopio è in slewing"),
                                ]]), title="Camere", key="cameras-autodisplay"),
                            shrink=True)]
                        ))
                    ],
                    [
                        sg.pin(
                            sg.Frame(layout=([
                                [
                                    sg.Combo(values=tuple(), size=(17, 1), key='camera-combo')
                                ],
                                [
                                    sg.RealtimeButton('↖️', key=ButtonKey.KEY_CAMERA_MOVE_UP, metadata="MOVE_TOP_LEFT", disabled=False, tooltip="muovi la camera in alto a sinistra" ),
                                    sg.RealtimeButton('⬆️', key=ButtonKey.KEY_CAMERA_MOVE_TOP_LEFT, metadata="MOVE_UP", disabled=False, tooltip="muovi la camera in alto"),
                                    sg.RealtimeButton('↗️', key=ButtonKey.KEY_CAMERA_MOVE_TOP_RIGHT, metadata="MOVE_TOP_RIGHT", disabled=False, tooltip="muovi la camera in alto a destra"),
                                ],
                                [
                                    sg.RealtimeButton('⬅️', key=ButtonKey.KEY_CAMERA_MOVE_LEFT, metadata="MOVE_LEFT", disabled=False, tooltip="muovi la camera a sinistra"),
                                    sg.RealtimeButton('❌', key=ButtonKey.KEY_CAMERA_STOP_MOVE, metadata="MOVE_STOP", disabled=False, tooltip="ferma la camera",),
                                    sg.RealtimeButton('➡️', key=ButtonKey.KEY_CAMERA_MOVE_RIGHT, metadata="MOVE_RIGHT", disabled=False, tooltip="muovi la camera in a destra"),
                                ],
                                [
                                    sg.RealtimeButton('↙️', key=ButtonKey.KEY_CAMERA_MOVE_BOTTOM_LEFT, metadata="MOVE_BOTTOM_LEFT", disabled=False, tooltip="muovi la camera in basso a sinistra"),
                                    sg.RealtimeButton('⬇️', key=ButtonKey.KEY_CAMERA_MOVE_DOWN, metadata="MOVE_DOWN", disabled=False, tooltip="muovi la camera in basso"),
                                    sg.RealtimeButton('↘️', key=ButtonKey.KEY_CAMERA_MOVE_BOTTOM_RIGHT, metadata="MOVE_BOTTOM_RIGHT", disabled=False, tooltip="muovi la camera in basso a destra"),
                                ],
                            ]), title="Movimento Camera", pad=(3, 10), key="camera-remote"),
                        shrink=True)
                    ]
                ))  
            ]
        ]

        
        block_stato_tende = [
            [sg.Text('Stato Tende', font=FONT)],
            [
                sg.Canvas(size=(self.l, self.h), background_color='grey', key='canvas'),
                sg.Frame(layout=([[
                    sg.Column(layout=(
                        [sg.Text('Est', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (10, 0)))],
                        [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='apert_e', background_color="white", text_color="#2c2825", pad=(0, 0))],
                        [sg.Text('Ovest', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (50, 0)))],
                        [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='apert_w', background_color="white", text_color="#2c2825", pad=((0, 0), (0, 30)))]
                    ))
                ]]), title='Tende', relief=sg.RELIEF_GROOVE, pad=(2, 0)),
                sg.Frame(layout=([[
                    sg.Column(layout=(
                        [sg.Text('Alt', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (10, 0)))],
                        [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='alt', background_color="white", text_color="#2c2825", pad=(0, 0))],
                        [sg.Text('Az', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (50, 0)))],
                        [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='az', background_color="white", text_color="#2c2825", pad=((0, 0), (0, 30)))]
                    ))
                ]]), title='Telescopio', relief=sg.RELIEF_GROOVE, pad=((6, 0), (0, 0)))
            ]
        ]
        
        block_alimentatori = [
            [sg.Text('Alimentatori & Luci', font=FONT)],
            [
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_OFF), key=ButtonKey.KEY_TELE_SWITCH, metadata="TURN_ON", disabled=False, size=(8, 1), tooltip="accensione alimentarore telescopio", button_color=("white", "red")),
                ]]), title="Telescopio", pad=PAD_DOWN),
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_OFF), key=ButtonKey.KEY_CCD_SWITCH, metadata="TURN_ON", disabled=False, size=(8, 1), tooltip="accensione alimentatore CCD", button_color=("white", "red")),
                ]]), title="CCD", pad=PAD_DOWN),
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_OFF), key=ButtonKey.KEY_FLAT_LIGHT, metadata="TURN_ON", disabled=False, size=(8, 1), tooltip="accensione pannnello del flat e attiva il tracking se il telescopio è in posizione flat", button_color=("white", "red")),
                ]]), title="Luce Flat", pad=PAD_DOWN),
                sg.Frame(layout=([[
                    sg.Button(_name(ButtonLabel.LABEL_OFF), key=ButtonKey.KEY_DOME_LIGHT, metadata="TURN_ON", disabled=False, size=(8, 1), tooltip="accensioni luci cupola, controllare se il telescopio è in fase di ripresa", button_color=("white", "red")),
                    sg.Checkbox('Abilita Autolight', key="autolight", default=True, tooltip="le luci della cupola si accendono automaticamente quando il telescopio è in slewing")
                ]]), title="Luce Cupola", pad=PAD_DOWN)
            ]
        ]
        
        block_stato_crac = [
            [sg.Text('Stato di CRaC', font=FONT)],
            [
                sg.Frame(layout=(
                    [sg.Text('', size=(25, 1), justification='center', font=("Helvetica", 12))],
                    [
                        sg.Text(GuiLabel.TELESCOPE_DISCONNECTED.value, size=(10, 1), justification='center', font=("Helvetica", 12), key='status-tele', background_color="white", text_color="red"),
                        sg.Text(GuiLabel.TELESCOPE_TRACKING_OFF.value, size=(10, 1), justification='center', font=("Helvetica", 12), key='status-tracking', background_color="white", text_color="red"),
                        sg.Text(GuiLabel.TELESCOPE_SLEWING_OFF.value, size=(10, 1), justification='center', font=("Helvetica", 12), key='status-slewing', background_color="white", text_color="red"),
                    ]
                ), title='Telescopio', relief=sg.RELIEF_GROOVE),
                sg.Frame(layout=(
                    [sg.Text('Tenda Ovest', size=(11, 1), justification='center', font=("Helvetica", 12)), sg.Text('Tenda Est', size=(11, 1), justification='center', font=("Helvetica", 12))],
                    [
                        sg.Text(GuiLabel.CURTAIN_DISABLED.value, size=(11, 1), justification='center', font=("Helvetica", 12), key='status-curtain_west', background_color="red", text_color="white"),
                        sg.Text(GuiLabel.CURTAIN_DISABLED.value, size=(11, 1), justification='center', font=("Helvetica", 12), key='status-curtain_east', background_color="red", text_color="white")
                    ]
                ), title='Tende', relief=sg.RELIEF_GROOVE)
            ],
            [sg.Text(GuiLabel.NO_ALERT.value, size=(61, 1), justification='center', background_color="#B0C4DE", font=("Helvetica", 12), text_color="#FF0000", key="alert", relief=sg.RELIEF_RIDGE)]
        ]
        
  
        block_meteo =[
            [
                sg.Text('Dati Meteo', font=FONT), sg.Text(' ', size =(5, 1)), sg.Text('Tendenza Barometro (3 ore)', size=(23, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (10, 0))), 
                sg.Text('', size=(8, 1), justification='center', font=("Helvetica", 12), key='barometer-trend', background_color="white", text_color="#2c2825", pad=(0, 0)),
                sg.Text('       previsioni ', size=(11, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (10, 0))), 
                sg.Text('', size=(35, 1), justification='center', font=("Helvetica", 12), key="barometer-trend-forecast", background_color="white", text_color="#2c2825", pad=(0, 0))
            ],
            [
                sg.Frame(layout=([
                    [sg.In(key='weather-updated-at', visible=False)],
                    
                    [
                        sg.Image(key="wind-speed", expand_x=True, expand_y=True, size=SIZE_GAUGE),
                        sg.Image(key="wind-gust-speed", expand_x=True, expand_y=True, size=SIZE_GAUGE),
                        sg.Image(key="temperature", expand_x=True, expand_y=True, size=SIZE_GAUGE),
                    
                    
                        sg.Image(key="humidity", expand_x=True, expand_y=True, size=SIZE_GAUGE),
                        sg.Image(key="rain-rate", expand_x=True, expand_y=True, size=SIZE_GAUGE),
                        sg.Image(key="barometer", expand_x=True, expand_y=True, size=SIZE_GAUGE),
                    ],
                ]), title="Meteo", expand_x=True, expand_y=True)
            ],
            [sg.Text('Casella di allerta chiusura CRaC', size=(50, 1), justification='center', background_color="white", font=("Helvetica", 12), text_color="red", key='alert_meteo',  pad=((230, 0), (10, 0)))]
        ]

        block_alim = [
            [sg.Text('Stato Alimentazione - UPS', font=FONT)],
            [sg.T("Qui ci vanno i gauge dell'UPS, Volt e percent di carica")]
        ]
        
        block_logo_ara = [
            [sg.Text("        ", background_color='#000098'), sg.Image("images/logo_ara.png")]    
        ]

        layout = [
            [sg.Column(block_3T, size=(720, 90), pad=PAD), sg.Column(block_logo_ara, size=(190, 90), background_color='#000098')],

            [sg.Column(
                [
                    [sg.Column(block_alimentatori, size=(555, 90), pad=PAD_LEFT_INSIDE)],
                    [sg.Column(block_stato_tende, size=(555, 300), pad=PAD_LEFT_INSIDE)]
                ], background_color=BORDER_COLOR),
                sg.Column(block_video, size=(352, 394), pad=PAD_LEFT_INSIDE)
            ],
            [sg.Column(block_stato_crac, size=(574, 150), pad=PAD_LEFT_INSIDE), sg.Column(block_alim, size=(336, 150))],
            [sg.Column(block_meteo, size=(916, 200), pad=PAD_LEFT_INSIDE)]
        ]
        
        self.win = sg.Window('CRaC -- Control Roof and Curtains by ARA', layout, margins=(5, 5), background_color=BORDER_COLOR, grab_anywhere=True, finalize=True)
        self.base_draw()

    def create_background_image(self) -> None:

        """ Create the background image for the sky when the roof is open and hides immediately it """

        canvas = self.win['canvas']
        self.img_fondo = PhotoImage(file="cielo_stellato.gif")
        self.image = canvas.TKCanvas.create_image(0, 0, image=self.img_fondo, anchor=NW)
        self.hide_background_image()

    def hide_background_image(self) -> None:

        """ Hide the sky when the roof is closed """

        canvas = self.win['canvas']
        canvas.TKCanvas.itemconfigure(self.image, state='hidden')

    def show_background_image(self) -> None:

        """ Show the sky when the roof is open """

        canvas = self.win['canvas']
        canvas.TKCanvas.itemconfigure(self.image, state='normal')

    def is_autolight(self):

        """
            read the status of the checkbox that enable/disable the autolight
            when telescope is slewing
        """

        return self.win['autolight'].Get()

    def is_autodisplay(self):

        """
            read the status of the checkbox that enable/disable the
            camera autodisplay
        """
        return self.win['autodisplay'].Get()

    def set_autolight(self, checked: bool):
        logger.debug(f"Is inside set_autolight method with checked: {checked}")
        self.win['autolight'](checked)

    def set_autodisplay(self, checked: bool):
        logger.debug(f"Is inside set_autodisplay method with checked: {checked}")
        self.win['autodisplay'](checked)

    def base_draw(self) -> None:
        p1 = ((int((self.l / 2) - (self.delta_pt / 2))) - (0.9 * self.t), self.h)
        p2 = ((int((self.l / 2) - (self.delta_pt / 2))) - (0.9 * self.t), ((self.h / 12) * 10))
        p3 = self.l / 2, 1.2 * (self.h / 2)
        p4 = ((int((self.l / 2) + (self.delta_pt / 2))) + (0.9 * self.t), ((self.h / 12) * 10))
        p5 = ((int((self.l / 2) + (self.delta_pt / 2))) + (0.9 * self.t), self.h)
        p6 = 1, self.h
        p7 = self.l - 1, self.h
        p8 = self.l - 1, (self.h / 11) * 8
        p9 = self.l / 2, (self.h / 11) * 4.5
        p10 = 1, (self.h / 11) * 8
        canvas = self.win['canvas']
        self.create_background_image()
        canvas.TKCanvas.create_polygon((p6, p7, p8, p9, p10), width=1, outline='grey', fill='#D8D8D8')
        canvas.TKCanvas.create_polygon((p1, p5, p4, p3, p2), width=1, outline='grey', fill='#848484')

    def status_alert(self, mess_alert: str) -> None:

        """ Avvisa che le tende non possono essere aperte """

        self.win['alert'].Update(mess_alert)

    def __toggle_button__(self, *args, **kwargs):

        # args: list of elements keys
        # kwargs: dictionary of elements attributes

        # for every key in args:
        for key in args:

            # update the relative element with the kwargs attributes (actually
            # we use only update=False but we can also do something like):
            # update=False, tooltip="whatever"...
            self.win[key].Update(**kwargs)

    def update_status_tele(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Tele Status """

        self.win['status-tele'].Update(status, text_color=text_color, background_color=background_color)

    def update_tele_text(self, coords: Dict[str, str]) -> None:

        """ Update telescope altazimuth coordinates """

        altitude = int(coords["alt"])
        azimuth = int(coords["az"])

        self.win['alt'].Update(altitude)
        self.win['az'].Update(azimuth)

    def update_status_curtain(self, orientation, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Curtain East Status """

        self.win[f"status-{orientation}"].Update(status, text_color=text_color, background_color=background_color)

    def update_curtains_text(self, alpha_e: int, alpha_w: int) -> Tuple[int, int]:

        """ Update curtains angular values """

        self.win['apert_e'].Update(alpha_e)
        self.win['apert_w'].Update(alpha_w)

    def is_curtains_position_changed(self, east_steps: int, west_steps: int) -> bool:
        if east_steps == self.east_steps and west_steps == self.west_steps:
            return False

        self.east_steps = east_steps
        self.west_steps = west_steps
        return True

    def convert_steps_to_angular_values(self, east_steps: int, west_steps: int) -> Tuple[int, int]:

        """ Convert steps to curtains angular values """

        alpha_e = int(east_steps * float("{0:.3f}".format(self.increm_e)))  # from steps to degree for east
        alpha_w = int(west_steps * float("{0:.3f}".format(self.increm_w)))  # from steps to degree for west
        return alpha_e, alpha_w

    def update_status_tracking(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Tracking Status """

        self.win['status-tracking'].Update(status, text_color=text_color, background_color=background_color)

    def update_status_slewing(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Slewing Status """

        self.win['status-slewing'].Update(status, text_color=text_color, background_color=background_color)

    def update_curtains_graphic(self, alpha_e: int, alpha_w: int) -> None:

        """ Draw curtains position with canvas """

        self.__delete_polygons__(self.tenda_e, self.line2_e, self.line3_e, self.line4_e)
        self.__delete_polygons__(self.tenda_w, self.line2_w, self.line3_w, self.line4_w)

        self.tenda_e, self.line2_e, self.line3_e, self.line4_e = self.__create_curtain_polygon__(alpha_e, "E")
        self.tenda_w, self.line2_w, self.line3_w, self.line4_w = self.__create_curtain_polygon__(alpha_w, "W")

    def __delete_polygons__(self, *polygons_and_lines) -> None:
        canvas = self.win['canvas']
        for polygon in polygons_and_lines:
            canvas.TKCanvas.delete(polygon)

    def __create_curtain_polygon__(self, alpha: int, orientation: str) -> tuple:
        pt, pt1, pt2, pt3, pt4, pt5 = self.__create_polygon_coordinates__(alpha, orientation)

        canvas = self.win['canvas']

        return (
                canvas.TKCanvas.create_polygon((pt, pt1, pt2, pt3, pt4, pt5), width=1, outline='#E0F8F7', fill='#0B4C5F'),
                canvas.TKCanvas.create_line((pt, pt2), width=1, fill='#E0F8F7'),
                canvas.TKCanvas.create_line((pt, pt3), width=1, fill='#E0F8F7'),
                canvas.TKCanvas.create_line((pt, pt4), width=1, fill='#E0F8F7')
            )

    def __create_polygon_coordinates__(self, alpha: int, orientation: str) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        angolo_min = self.alpha_min_conf * self.conv  # valore dell'inclinazione della base della tenda in radianti
        angolo1 = ((alpha / 4) + self.alpha_min_conf) * self.conv
        angolo2 = ((alpha / 2) + self.alpha_min_conf) * self.conv
        angolo3 = (((alpha / 4) * 3) + self.alpha_min_conf) * self.conv
        angolo = (alpha + self.alpha_min_conf) * self.conv

        i = 1 if orientation == "E" else -1

        y = int(self.h / 3) * 2
        x = int((self.l / 2) + (i * self.delta_pt / 2))
        pt1 = (x + (i * (int(math.cos(angolo_min) * self.t))), y - (int(math.sin(angolo_min) * self.t)))
        pt2 = (x + (i * (int(math.cos(angolo1) * self.t))), y - (int(math.sin(angolo1) * self.t)))
        pt3 = (x + (i * (int(math.cos(angolo2) * self.t))), y - (int(math.sin(angolo2) * self.t)))
        pt4 = (x + (i * (int(math.cos(angolo3) * self.t))), y - (int(math.sin(angolo3) * self.t)))
        pt5 = (x + (i * (int(math.cos(angolo) * self.t))), y - (int(math.sin(angolo) * self.t)))

        pt = (x, y)

        return pt, pt1, pt2, pt3, pt4, pt5
