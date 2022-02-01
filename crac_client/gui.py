import PySimpleGUI as sg  # type: ignore
import math
import config
from logger import LoggerClient as Logger
from tkinter import PhotoImage, NW, DISABLED
from typing import Tuple
#from status import Orientation
from typing import Dict
from gui_constants import GuiLabel, GuiKey


class Gui:

    def __init__(self):
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
#        sg.theme('DarkBlue')
        layout = [
                    [sg.Menu([], tearoff=True)],
                    [sg.Text('Monitor Tende e Tetto ', size=(50, 1), justification='center', font=("Helvetica", 15))],
                    [
                        sg.Frame(layout=([[
                            sg.Button('Apri', key=GuiKey.OPEN_ROOF, disabled=False, size=(6, 1), tooltip="apre il tetto"),
                            sg.Button('Chiudi', key=GuiKey.CLOSE_ROOF, disabled=True, size=(6, 1), tooltip="chiude il tetto")
                        ]]), title="Tetto", pad=(3, 0)),
                        sg.Frame(layout=([[
                            sg.Button('Sync', key=GuiKey.SYNC_TELE, disabled=False, size=(5, 1), tooltip='sincronizza il telescopio'),
                            sg.Button('Park', key=GuiKey.PARK_TELE, disabled=False, size=(5, 1), tooltip='porta il telescopio in posizione di park'),
                            sg.Button('Flat', key=GuiKey.FLAT_TELE, disabled=False, size=(5, 1) , tooltip='porta il telescopio in posizione di flat')
                        ]]), title="Telescopio", pad=(3, 0)),
                        sg.Frame(layout=([[
                            sg.Button('Attiva', key=GuiKey.ENABLED_CURTAINS, disabled=True, size=(6, 1), tooltip='clicca per attivare'),
                            sg.Button('Disattiva', key=GuiKey.DISABLED_CURTAINS, disabled=True,  size=(6, 1), tooltip='clicca per attivare'),
                            sg.Button('Calibra', key=GuiKey.CALIBRATE_CURTAINS, disabled=True,  size=(6, 1), tooltip='clicca per attivare')
                        ]]), title="Tende", pad=(3, 0))
                    ],
                    [
                        sg.Frame(layout=([[
                            sg.Button(GuiLabel.ON, key=GuiKey.POWER_ON_TELE, disabled=False, size=(4, 1), tooltip="accensione alimentarore telescopio"),
                            sg.Button(GuiLabel.OFF, key=GuiKey.POWER_OFF_TELE, disabled=True, size=(4, 1), button_color=('black', 'red'), tooltip="spegnimento alimentatore telescopio"),
                        ]]), title="Power Switch Tele", pad=(3, 10)),
                        sg.Frame(layout=([[
                            sg.Button(GuiLabel.ON, key=GuiKey.POWER_ON_CCD, disabled=False, size=(4, 1), tooltip="accensione alimentatore CCD"),
                            sg.Button(GuiLabel.OFF, key=GuiKey.POWER_OFF_CCD, disabled=True, size=(4, 1), button_color=('black', 'red'), tooltip="spegnimento alimentatore CCD"),
                        ]]), title="Power Switch CCD", pad=(3, 10)),
                        sg.Frame(layout=([[
                            sg.Button(GuiLabel.ON, key=GuiKey.PANEL_ON, disabled=False, size=(4, 1), tooltip="accensione pannnello del flat"),
                            sg.Button(GuiLabel.OFF, key=GuiKey.PANEL_OFF, disabled=True, size=(4, 1), button_color=('black', 'red'), tooltip="spegnimento pannello flat")
                        ]]), title="Panel Flat", pad=(3, 10)),
                        sg.Frame(layout=([[
                            sg.Button(GuiLabel.ON, key=GuiKey.LIGHT_ON, disabled=False, size=(4, 1), tooltip="accensioni luci cupola, controllare se i telescopio è in fase di ripresa"),
                            sg.Button(GuiLabel.OFF, key=GuiKey.LIGHT_OFF, disabled=True, size=(4, 1), button_color=('black', 'red'), tooltip="spegnimento luci cupola"),
                            sg.Checkbox('Enable Autolight', key="autolight", default=True)
                        ]]), title="Light Dome", pad=(3, 10))
                    ],
                    [
                        sg.Canvas(size=(self.l, self.h), background_color='grey', key='canvas'),
                        sg.Frame(layout=([[
                                sg.Column(layout=(
                                    [sg.Text('Est', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (10, 0)))],
                                    [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='apert_e', background_color="white", text_color="#2c2825", pad=(0, 0))],
                                    [sg.Text('Ovest', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (50, 0)))],
                                    [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='apert_w', background_color="white", text_color="#2c2825", pad=((0, 0), (0, 30)))]
                                ))
                            ]]), title='Tende', relief=sg.RELIEF_GROOVE, pad=(2, 0)
                        ),
                        sg.Frame(layout=([[
                                sg.Column(layout=(
                                    [sg.Text('Alt', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (10, 0)))],
                                    [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='alt', background_color="white", text_color="#2c2825", pad=(0, 0))],
                                    [sg.Text('Az', size=(5, 1), justification='left', font=("Helvetica", 12), pad=((0, 0), (50, 0)))],
                                    [sg.Text('0', size=(5, 1), justification='right', font=("Helvetica", 12), key='az', background_color="white", text_color="#2c2825", pad=((0, 0), (0, 30)))]
                                ))
                            ]]), title='Telescopio', relief=sg.RELIEF_GROOVE, pad=((6, 0), (0, 0))
                        )
                    ],
                    [sg.Frame(layout=([
                            [
                                sg.Column(layout=(
                                    [sg.Text('Tetto', size=(11, 1), justification='center', font=("Helvetica", 12))],
                                    [sg.Text(GuiLabel.ROOF_CLOSED, size=(11, 1), justification='center', font=("Helvetica", 12), key='status-roof', background_color="red", text_color="white")]
                                )),
                                sg.Column(layout=(
                                    [sg.Text('Telescopio', size=(25, 1), justification='center', font=("Helvetica", 12))],
                                    [
                                        sg.Text(GuiLabel.TELESCOPE_PARKED, size=(8, 1), justification='center', font=("Helvetica", 12), key='status-tele', background_color="white", text_color="red"),
                                        sg.Text(GuiLabel.TELESCOPE_TRACKING_OFF, size=(8, 1), justification='center', font=("Helvetica", 12), key='status-tracking', background_color="white", text_color="red"),
                                        sg.Text(GuiLabel.TELESCOPE_SLEWING_OFF, size=(8, 1), justification='center', font=("Helvetica", 12), key='status-slewing', background_color="white", text_color="red"),
                                        sg.Text(GuiLabel.TELESCOPE_SYNC_OFF, size=(8, 1), justification='center', font=("Helvetica", 12), key='status-sync', background_color="white", text_color="red")
                                    ]
                                )),
                                sg.Column(layout=(
                                    [sg.Text('Tenda Ovest', size=(11, 1), justification='center', font=("Helvetica", 12)), sg.Text('Tenda Est', size=(11, 1), justification='center', font=("Helvetica", 12))],
                                    [
                                        sg.Text(GuiLabel.CURTAINS_DISABLED, size=(11, 1), justification='center', font=("Helvetica", 12), key='status-curtain-west', background_color="red", text_color="white"),
                                        sg.Text(GuiLabel.CURTAINS_DISABLED, size=(11, 1), justification='center', font=("Helvetica", 12), key='status-curtain-east', background_color="red", text_color="white")
                                    ]
                                ))

                            ],
                            [sg.Text(GuiLabel.NO_ALERT, size=(58, 1), justification='center', background_color="#B0C4DE", font=("Helvetica", 12), text_color="#FF0000", key="alert", relief=sg.RELIEF_RIDGE)]
                        ]), title='Status CRaC', relief=sg.RELIEF_GROOVE
                    )]
                 ]

        self.win = sg.Window('CRaC -- Control Roof and Curtains by ARA', layout, grab_anywhere=False, finalize=True)
        self.base_draw()

    def create_background_image(self) -> None:

        """ Create the background image for the sky when the roof is open and hides immediately it """

        canvas = self.win.FindElement('canvas')
        self.img_fondo = PhotoImage(file="cielo_stellato.gif")
        self.image = canvas.TKCanvas.create_image(0, 0, image=self.img_fondo, anchor=NW)
        self.hide_background_image()

    def hide_background_image(self) -> None:

        """ Hide the sky when the roof is closed """

        canvas = self.win.FindElement('canvas')
        canvas.TKCanvas.itemconfigure(self.image, state='hidden')

    def show_background_image(self) -> None:

        """ Show the sky when the roof is open """

        canvas = self.win.FindElement('canvas')
        canvas.TKCanvas.itemconfigure(self.image, state='normal')

    def is_autolight(self):

        """
            read the status of the checkbox that enable/disable the autolight
            when telescope is slewing
        """

        autolight = self.win.FindElement('autolight').Get()
        Logger.getLogger().debug('autolight status is %s', autolight)
        return autolight

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
        canvas = self.win.FindElement('canvas')
        self.create_background_image()
        canvas.TKCanvas.create_polygon((p6, p7, p8, p9, p10), width=1, outline='grey', fill='#D8D8D8')
        canvas.TKCanvas.create_polygon((p1, p5, p4, p3, p2), width=1, outline='grey', fill='#848484')

    def status_alert(self, mess_alert: str) -> None:

        """ Avvisa che le tende non possono essere aperte """

        self.win.FindElement('alert').Update(mess_alert)

    def update_status_roof(self, status: str, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Roof Status """

        Logger.getLogger().info('update_status_roof in gui')
        self.win.FindElement('status-roof').Update(status, text_color=text_color, background_color=background_color)

    def __toggle_button__(self, *args, **kwargs):

        # args: list of elements keys
        # kwargs: dictionary of elements attributes

        # for every key in args:
        for key in args:

            # update the relative element with the kwargs attributes (actually
            # we use only update=False but we can also do something like):
            # update=False, tooltip="whatever"...
            self.win.FindElement(key).Update(**kwargs)

    def update_enable_disable_button(self):

        """ Update enable-disable button """

        Logger.getLogger().info('update_enable_disable_button in gui')
        self.__toggle_button__(GuiKey.OPEN_ROOF, disabled=True)
        self.__toggle_button__(GuiKey.CLOSE_ROOF, GuiKey.ENABLED_CURTAINS, GuiKey.DISABLED_CURTAINS, GuiKey.CALIBRATE_CURTAINS, disabled=False)

    def update_disable_button_close_roof(self):

        """ Update disable button close roof """

        Logger.getLogger().info('disable close roof button in gui')
        self.__toggle_button__(GuiKey.CLOSE_ROOF, disabled=True)

    def update_enable_button_open_roof(self):

        """ Update enable button open roof """

        Logger.getLogger().info('enable close roof button in gui and the other components')
        self.__toggle_button__(GuiKey.OPEN_ROOF, disabled=False)
        self.__toggle_button__(GuiKey.CLOSE_ROOF, GuiKey.ENABLED_CURTAINS, GuiKey.DISABLED_CURTAINS, GuiKey.CALIBRATE_CURTAINS, disabled=True)

    def update_status_tele(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Tele Status """

        Logger.getLogger().info('update_status_tele in gui')
        self.win.FindElement('status-tele').Update(status, text_color=text_color, background_color=background_color)

    def update_tele_text(self, coords: Dict[str, str]) -> None:

        """ Update telescope altazimuth coordinates """

        altitude = int(coords["alt"])
        azimuth = int(coords["az"])

        self.win.FindElement('alt').Update(altitude)
        self.win.FindElement('az').Update(azimuth)

    def update_status_curtain_east(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Curtain East Status """

        Logger.getLogger().info('update_status_curtain_east in gui')
        self.win.FindElement('status-curtain-east').Update(status, text_color=text_color, background_color=background_color)

    def update_status_curtain_west(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Curtain West Status """

        Logger.getLogger().info('update_status_curtain_west in gui %s', status)
        self.win.FindElement('status-curtain-west').Update(status, text_color=text_color, background_color=background_color)

    def update_curtains_text(self, e_e: int, e_w: int) -> Tuple[int, int]:

        """ Update curtains angular values """

        alpha_e = int(e_e * float("{0:.3f}".format(self.increm_e)))  # from steps to degree for east
        alpha_w = int(e_w * float("{0:.3f}".format(self.increm_w)))  # from steps to degree for west

        self.win.FindElement('apert_e').Update(alpha_e)
        self.win.FindElement('apert_w').Update(alpha_w)
        return alpha_e, alpha_w

    def update_disable_button_disabled_curtains(self):

        """ Update enable button curtains """

        Logger.getLogger().info('update_enable_disable_button_curtains in gui')
        self.__toggle_button__(GuiKey.DISABLED_CURTAINS, disabled=True)

    def update_disable_button_enabled_curtains(self):

        """ Update enable button curtains """

        Logger.getLogger().info('update_enable_disable_button_curtains in gui')
        self.__toggle_button__(GuiKey.ENABLED_CURTAINS, disabled=True)

    def update_disable_panel_all(self):

        """ Update enable button on panel flat """

        Logger.getLogger().info('update_disable_button_panel_flat_all')
        self.__toggle_button__(GuiKey.PANEL_ON, GuiKey.PANEL_OFF, disabled=True, button_color=('black', 'red'))

    def update_disable_panel_on(self):

        """ Update enable button on panel flat """

        Logger.getLogger().info('update_disable_button_panel_flat_on')
        self.__toggle_button__(GuiKey.PANEL_ON, disabled=True, button_color=('white', 'green'))
        self.__toggle_button__(GuiKey.PANEL_OFF, disabled=False, button_color=('black', 'white'))

    def update_disable_panel_off(self):

        """ Update disable button off panel flat """

        Logger.getLogger().info('update_disable_button_panel_flat_off')
        self.__toggle_button__(GuiKey.PANEL_ON, disabled=False, button_color=('black', 'white'))
        self.__toggle_button__(GuiKey.PANEL_OFF, disabled=True, button_color=('black', 'red'))

    def update_disable_button_power_switch_on(self):

        """ Update enable button on power switch """

        Logger.getLogger().info('update_disable_button_power_switch_on')
        self.__toggle_button__(GuiKey.POWER_ON_TELE, disabled=True, button_color=('white', 'green'))
        self.__toggle_button__(GuiKey.POWER_OFF_TELE, disabled=False, button_color=('black', 'white'))

    def update_disable_button_power_switch_off(self):

        """ Update disable button off power switch """

        Logger.getLogger().info('update_disable_button_power_switch_off')
        self.__toggle_button__(GuiKey.POWER_ON_TELE, disabled=False, button_color=('black', 'white'))
        self.__toggle_button__(GuiKey.POWER_OFF_TELE, disabled=True, button_color=('black', 'red'))

    def update_disable_button_light_on(self):

        """ Update enable button on light dome """

        Logger.getLogger().info('update_disable_button_light_dome_on')
        self.__toggle_button__(GuiKey.LIGHT_ON, disabled=True, button_color=('white', 'green'))
        self.__toggle_button__(GuiKey.LIGHT_OFF, disabled=False, button_color=('black', 'white'))

    def update_disable_button_light_off(self):

        """ Update enable button off light dome """

        Logger.getLogger().info('update_disable_button_light_dome_off')
        self.__toggle_button__(GuiKey.LIGHT_ON, disabled=False, button_color=('black', 'white'))
        self.__toggle_button__(GuiKey.LIGHT_OFF, disabled=True, button_color=('black', 'red'))

    def update_disable_button_power_on_ccd(self):

        """ Update enable button on auxiliary """

        Logger.getLogger().info('update_disable_button_auxiliary_on')
        self.__toggle_button__(GuiKey.POWER_ON_CCD, disabled=True, button_color=('white', 'green'))
        self.__toggle_button__(GuiKey.POWER_OFF_CCD, disabled=False, button_color=('black', 'white'))

    def update_disable_button_power_off_ccd(self):

        """ Update enable button off auxiliary """

        Logger.getLogger().info('update_disable_button_auxiliary_off')
        self.__toggle_button__(GuiKey.POWER_ON_CCD, disabled=False, button_color=('black', 'white'))
        self.__toggle_button__(GuiKey.POWER_OFF_CCD, disabled=True, button_color=('black', 'red'))

    def update_status_tracking(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Tracking Status """

        Logger.getLogger().info('update_status_tracking in gui')
        self.win.FindElement('status-tracking').Update(status, text_color=text_color, background_color=background_color)

    def update_status_slewing(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Slewing Status """

        Logger.getLogger().info('update_status_slewing in gui')
        self.win.FindElement('status-slewing').Update(status, text_color=text_color, background_color=background_color)

    def update_status_sync(self, status, text_color: str = 'white', background_color: str = 'red') -> None:

        """ Update Sync Status """

        Logger.getLogger().info('update_status_sync in gui')
        self.win.FindElement('status-sync').Update(status, text_color=text_color, background_color=background_color)

    def update_button_sync(self, disabled):

        """ Disable Button Sync """

        Logger.getLogger().info('update_disable_button_sync on gui')
        self.__toggle_button__(GuiKey.SYNC_TELE, disabled=disabled)

    def update_curtains_graphic(self, alpha_e: int, alpha_w: int) -> None:

        """ Draw curtains position with canvas """

        self.__delete_polygons__(self.tenda_e, self.line2_e, self.line3_e, self.line4_e)
        self.__delete_polygons__(self.tenda_w, self.line2_w, self.line3_w, self.line4_w)

        self.tenda_e, self.line2_e, self.line3_e, self.line4_e = self.__create_curtain_polygon__(alpha_e, "E")
        self.tenda_w, self.line2_w, self.line3_w, self.line4_w = self.__create_curtain_polygon__(alpha_w, "W")

    def __delete_polygons__(self, *polygons_and_lines) -> None:
        canvas = self.win.FindElement('canvas')
        for polygon in polygons_and_lines:
            canvas.TKCanvas.delete(polygon)

    def __create_curtain_polygon__(self, alpha: int, orientation: str) -> tuple:
        pt, pt1, pt2, pt3, pt4, pt5 = self.__create_polygon_coordinates__(alpha, orientation)

        canvas = self.win.FindElement('canvas')

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
