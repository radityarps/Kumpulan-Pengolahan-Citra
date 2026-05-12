"""
Optional system controls for GfG-style advanced gestures.

This module is intentionally defensive: if optional dependencies are unavailable,
methods become no-ops and the main app keeps running.
"""


class SystemController:
    """Control system brightness and volume if optional deps are available."""

    def __init__(self):
        self._brightness_available = False
        self._volume_available = False
        self._sbc = None
        self._volume_interface = None

        # Brightness backend
        try:
            import screen_brightness_control as sbc

            self._sbc = sbc
            self._brightness_available = True
        except Exception:
            self._brightness_available = False

        # Volume backend (Windows via pycaw)
        try:
            from ctypes import POINTER, cast
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            self._volume_available = True
        except Exception:
            self._volume_available = False

    @property
    def brightness_available(self):
        return self._brightness_available

    @property
    def volume_available(self):
        return self._volume_available

    def adjust_brightness(self, delta):
        """Adjust brightness by integer delta and clamp to [0, 100]."""
        if not self._brightness_available:
            return

        try:
            current = self._sbc.get_brightness()
            current_val = int(current[0] if isinstance(current, list) else current)
            target = max(0, min(100, current_val + int(delta)))
            self._sbc.set_brightness(target)
        except Exception:
            pass

    def adjust_volume(self, delta):
        """Adjust endpoint volume by scalar step and clamp to [0.0, 1.0]."""
        if not self._volume_available or self._volume_interface is None:
            return

        try:
            current = self._volume_interface.GetMasterVolumeLevelScalar()
            step = float(delta) / 100.0
            target = max(0.0, min(1.0, current + step))
            self._volume_interface.SetMasterVolumeLevelScalar(target, None)
        except Exception:
            pass
