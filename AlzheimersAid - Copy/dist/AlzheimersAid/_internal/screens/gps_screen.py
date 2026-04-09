from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.utils import platform
from kivymd.toast import toast
import requests

try:
    from plyer import gps
except ImportError:
    gps = None

class GPSScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_gps_active = False

    def on_enter(self, *args):
        self.get_location()

    def on_leave(self, *args):
        """Stop GPS when navigating away to save battery."""
        if platform == 'android' and gps:
            try:
                gps.stop()
                self.is_gps_active = False
            except Exception as e:
                print(f"Error stopping GPS: {e}")

    def get_location(self):
        if platform == 'android':
            self.request_android_gps()
        else:
            self.get_ip_location()

    def request_android_gps(self):
        from android.permissions import request_permissions, Permission
        def callback(permissions, results):
            if all(results):
                self.start_gps_android()
            else:
                toast("Location permission required")
        request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], callback)

    def start_gps_android(self):
        if gps:
            try:
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                gps.start(minTime=1000, minDistance=1)
                self.is_gps_active = True
                toast("Starting GPS...")
            except Exception as e:
                toast(f"GPS Start Error: {e}")
                self.get_ip_location()

    def on_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        self.update_map(lat, lon)

    def on_status(self, stype, status):
        toast(f"GPS Status: {status}")

    def get_ip_location(self):
        """Fallback for desktop using IP-based geolocation."""
        try:
            r = requests.get("http://ip-api.com/json/", timeout=5)
            data = r.json()
            if data['status'] == 'success':
                lat = data['lat']
                lon = data['lon']
                self.update_map(lat, lon)
                toast(f"IP Location: {data.get('city', 'Unknown')}")
            else:
                toast("Failed to get location via IP")
        except Exception as e:
            toast(f"Location error: {e}")

    def update_map(self, lat, lon):
        if hasattr(self.ids, 'mapview'):
            self.ids.mapview.lat = lat
            self.ids.mapview.lon = lon
            self.ids.mapview.zoom = 15
            # In a real app we'd add a marker here
            app = MDApp.get_running_app()
            app.db.add_activity(f"Location updated: {lat}, {lon}")
