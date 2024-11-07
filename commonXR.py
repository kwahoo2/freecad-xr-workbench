# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2023 Adrian Przekwas adrian.v.przekwas@gmail.com        *
# *                                                                         *
# *   Based on gl_example.py https://github.com/cmbruns/pyopenxr_examples   *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 3 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************


import preferences as pref
import controllerXR as conXR
import movementXR as movXR
import menuCoin
from math import tan, pi
import FreeCADGui as Gui
from pivy.coin import SoTransform
from pivy.coin import SoRotationXYZ
from pivy.coin import SoGroup
from pivy.coin import SbRotation
from pivy.coin import SoScale
from pivy.coin import SoEnvironment
from pivy.coin import SoDirectionalLight
from pivy.coin import SoCamera
from pivy.coin import SbVec3f
from pivy.coin import SoFrustumCamera
from pivy.coin import SbViewportRegion
from pivy.coin import SoSceneManager
from pivy.coin import SbColor
from pivy.coin import SoSeparator
import ctypes
import logging

try:
    from PySide2.QtWidgets import QOpenGLWidget, QDockWidget
    from PySide2.QtGui import QOpenGLContext, QSurfaceFormat, QOpenGLDebugLogger
    from PySide2.QtCore import Qt, QTimer, QElapsedTimer, QObject, SIGNAL
    import shiboken2 as shiboken
except ImportError:
    try:
        from PySide6.QtWidgets import QDockWidget
        from PySide6.QtOpenGLWidgets import QOpenGLWidget
        from PySide6.QtOpenGL import QOpenGLDebugLogger
        from PySide6.QtGui import QOpenGLContext, QSurfaceFormat
        from PySide6.QtCore import Qt, QTimer, QElapsedTimer, QObject, SIGNAL
        import shiboken6 as shiboken
    except ImportError:
        raise ImportError("Neither PySide2 nor PySide6 found!")

import platform

windowing_interface = ""

try:
    from OpenGL import GL
    if platform.system() == "Windows":
        from OpenGL import WGL
        windowing_interface = "WGL"
    elif platform.system() == "Linux":
        try:
            from OpenGL import GLX
            windowing_interface = "GLX"
        except ImportError:
            try:
                from OpenGL import EGL
                windowing_interface = "EGL"
                print("EGL not yet implemented, please run on X11")
            except ImportError:
                print("No Windowing Interface found!")
except ImportError:
    raise ImportError("PyOpenGL is required!")

try:
    import xr
    if windowing_interface == 'EGL':
        from xr.platform.linux import wl_display
        LP_wl_display = ctypes.POINTER(wl_display)
except ImportError:
    raise ImportError("pyopenxr is required!")


ALL_SEVERITIES = (
    xr.DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT
    | xr.DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT
    | xr.DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT
    | xr.DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT
)

ALL_TYPES = (
    xr.DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT
    | xr.DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT
    | xr.DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT
    | xr.DEBUG_UTILS_MESSAGE_TYPE_CONFORMANCE_BIT_EXT
)


def py_log_level(severity_flags: int):
    if severity_flags & 0x0001:  # VERBOSE
        return logging.DEBUG
    if severity_flags & 0x0010:  # INFO
        return logging.INFO
    if severity_flags & 0x0100:  # WARNING
        return logging.WARNING
    if severity_flags & 0x1000:  # ERROR
        return logging.ERROR
    return logging.CRITICAL


stringForFormat = {
    GL.GL_COMPRESSED_R11_EAC: "COMPRESSED_R11_EAC",
    GL.GL_COMPRESSED_RED_RGTC1: "COMPRESSED_RED_RGTC1",
    GL.GL_COMPRESSED_RG_RGTC2: "COMPRESSED_RG_RGTC2",
    GL.GL_COMPRESSED_RG11_EAC: "COMPRESSED_RG11_EAC",
    GL.GL_COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT: "COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT",
    GL.GL_COMPRESSED_RGB8_ETC2: "COMPRESSED_RGB8_ETC2",
    GL.GL_COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2: "COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2",
    GL.GL_COMPRESSED_RGBA8_ETC2_EAC: "COMPRESSED_RGBA8_ETC2_EAC",
    GL.GL_COMPRESSED_SIGNED_R11_EAC: "COMPRESSED_SIGNED_R11_EAC",
    GL.GL_COMPRESSED_SIGNED_RG11_EAC: "COMPRESSED_SIGNED_RG11_EAC",
    GL.GL_COMPRESSED_SRGB_ALPHA_BPTC_UNORM: "COMPRESSED_SRGB_ALPHA_BPTC_UNORM",
    GL.GL_COMPRESSED_SRGB8_ALPHA8_ETC2_EAC: "COMPRESSED_SRGB8_ALPHA8_ETC2_EAC",
    GL.GL_COMPRESSED_SRGB8_ETC2: "COMPRESSED_SRGB8_ETC2",
    GL.GL_COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC2: "COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC2",
    GL.GL_DEPTH_COMPONENT16: "DEPTH_COMPONENT16",
    GL.GL_DEPTH_COMPONENT24: "DEPTH_COMPONENT24",
    GL.GL_DEPTH_COMPONENT32: "DEPTH_COMPONENT32",
    GL.GL_DEPTH_COMPONENT32F: "DEPTH_COMPONENT32F",
    GL.GL_DEPTH24_STENCIL8: "DEPTH24_STENCIL8",
    GL.GL_R11F_G11F_B10F: "R11F_G11F_B10F",
    GL.GL_R16_SNORM: "R16_SNORM",
    GL.GL_R16: "R16",
    GL.GL_R16F: "R16F",
    GL.GL_R16I: "R16I",
    GL.GL_R16UI: "R16UI",
    GL.GL_R32F: "R32F",
    GL.GL_R32I: "R32I",
    GL.GL_R32UI: "R32UI",
    GL.GL_R8_SNORM: "R8_SNORM",
    GL.GL_R8: "R8",
    GL.GL_R8I: "R8I",
    GL.GL_R8UI: "R8UI",
    GL.GL_RG16_SNORM: "RG16_SNORM",
    GL.GL_RG16: "RG16",
    GL.GL_RG16F: "RG16F",
    GL.GL_RG16I: "RG16I",
    GL.GL_RG16UI: "RG16UI",
    GL.GL_RG32F: "RG32F",
    GL.GL_RG32I: "RG32I",
    GL.GL_RG32UI: "RG32UI",
    GL.GL_RG8_SNORM: "RG8_SNORM",
    GL.GL_RG8: "RG8",
    GL.GL_RG8I: "RG8I",
    GL.GL_RG8UI: "RG8UI",
    GL.GL_RGB10_A2: "RGB10_A2",
    GL.GL_RGB8: "RGB8",
    GL.GL_RGB9_E5: "RGB9_E5",
    GL.GL_RGBA16_SNORM: "RGBA16_SNORM",
    GL.GL_RGBA16: "RGBA16",
    GL.GL_RGBA16F: "RGBA16F",
    GL.GL_RGBA16I: "RGBA16I",
    GL.GL_RGBA16UI: "RGBA16UI",
    GL.GL_RGBA2: "RGBA2",
    GL.GL_RGBA32F: "RGBA32F",
    GL.GL_RGBA32I: "RGBA32I",
    GL.GL_RGBA32UI: "RGBA32UI",
    GL.GL_RGBA8_SNORM: "RGBA8_SNORM",
    GL.GL_RGBA8: "RGBA8",
    GL.GL_RGBA8I: "RGBA8I",
    GL.GL_RGBA8UI: "RGBA8UI",
    GL.GL_SRGB8_ALPHA8: "SRGB8_ALPHA8",
    GL.GL_SRGB8: "SRGB8",
    GL.GL_RGB16F: "RGB16F",
    GL.GL_DEPTH32F_STENCIL8: "DEPTH32F_STENCIL8",
    GL.GL_BGR: "BGR (Out of spec)",
    GL.GL_BGRA: "BGRA (Out of spec)",
}


class DockWidget(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        mw = Gui.getMainWindow()
        # set log_level=logging.DEBUG for more info
        self.xr_widget = XRwidget(log_level=logging.WARNING)
        self.setWidget(self.xr_widget)
        # widget without close button
        self.setFeatures(QDockWidget.DockWidgetMovable |
                         QDockWidget.DockWidgetFloatable)
        mw.addDockWidget(Qt.RightDockWidgetArea, self)

    def closeEvent(self, event):
        self.xr_widget.terminate()
        event.accept()

    def hide_mirror(self):
        self.xr_widget.disable_mirror()
        self.hide()

    def unhide_mirror(self):
        self.xr_widget.enable_mirror()
        self.show()

    def reload_scenegraph(self):
        self.xr_widget.read_preferences()
        self.xr_widget.reload_scenegraph()


class XRwidget(QOpenGLWidget):
    def __init__(self, parent=None, log_level=logging.WARNING):
        QOpenGLWidget.__init__(self, parent)
        self.log_level = log_level
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.render_target_size = None
        self.window = None
        self.session = None
        self.projection_layer_views = (xr.CompositionLayerProjectionView * 2)(
            *([xr.CompositionLayerProjectionView()] * 2))
        self.projection_layer = xr.CompositionLayerProjection(
            views=self.projection_layer_views)
        self.swapchain_create_info = xr.SwapchainCreateInfo()
        self.swapchain = None
        self.swapchain_images = None
        self.fbo_id = None
        self.fbo_msaa_id = None
        self.fbo_depth_buffer = None
        self.quit = False
        self.session_state = xr.SessionState.IDLE
        self.frame_state = xr.FrameState()
        self.eye_view_states = None
        self.window_size = None
        self.enable_debug = True
        self.linux_steamvr_broken_destroy_instance = False
        self.instance = None
        self.system_id = None
        self.pxrCreateDebugUtilsMessengerEXT = None
        self.pxrDestroyDebugUtilsMessengerEXT = None
        self.pxrGetOpenGLGraphicsRequirementsKHR = None
        self.graphics_requirements = xr.GraphicsRequirementsOpenGLKHR()
        if windowing_interface == 'WGL':
            self.graphics_binding = xr.GraphicsBindingOpenGLWin32KHR()
        elif windowing_interface == 'GLX':
            self.graphics_binding = xr.GraphicsBindingOpenGLXlibKHR()
        elif windowing_interface == 'EGL':
            self.graphics_binding = xr.GraphicsBindingOpenGLWaylandKHR()
        else:
            raise NotImplementedError('Unsupported platform')
        logging.basicConfig()
        self.logger = logging.getLogger("xr_viewer")
        self.logger.setLevel(log_level)
        self.debug_callback = xr.PFN_xrDebugUtilsMessengerCallbackEXT(
            self.debug_callback_py)

        self.context = QOpenGLContext.currentContext()
        # Attempt to disable vsync on the desktop window or
        # it will interfere with the OpenXR frame loop timing
        frmt = self.context.format()
        frmt.setSwapInterval(0)
        frmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        frmt.setMajorVersion(4)
        frmt.setMinorVersion(5)
        frmt.setRedBufferSize(8)
        frmt.setGreenBufferSize(8)
        frmt.setBlueBufferSize(8)
        frmt.setDepthBufferSize(24)
        frmt.setStencilBufferSize(8)
        frmt.setAlphaBufferSize(8)
        frmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        # multiple samples not required as MSAA is done in another buffer
        frmt.setSamples(1)
        frmt.setOption(QSurfaceFormat.DebugContext)
        ctx = QOpenGLContext()
        ctx.setFormat(frmt)
        ctx.create()
        if ctx.hasExtension(b"GL_KHR_debug"):
            print("GL_KHR_debug extension available")
        else:
            print("GL_KHR_debug extension NOT available")
        self.context = ctx

        self.logger.debug("OpenGL Context: %s", self.context)
        # drawing QOpenGLWidget mirror window may degrade frame timing
        self.mirror_window = True

        self.hand_count = 2
        self.old_time = 0
        # set which controller should be used for primary functionality (eg.
        # movement)
        self.primary_con = 0
        # 0 is the left one - defined in hand_paths
        self.secondary_con = 1
        self.frame_duration = 0
        self.render_duration = 0

        self.prepare_xr_instance()
        self.prepare_xr_system()
        self.prepare_window()
        self.prepare_xr_session()
        self.prepare_xr_swapchain()
        self.prepare_xr_composition_layers()
        self.prepare_xr_controls()
        self.setup_cameras()
        self.setup_controllers()
        self.setup_menus()
        self.setup_scene()  # have to be last, after cameras and controllers setup
        self.read_preferences()
        self.reload_scenegraph()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.update_render)
        self.timer.start(0)

        self.timer_gui = QTimer()  # timer used to update non-vr things like widget title bar
        QObject.connect(self.timer_gui, SIGNAL("timeout()"), self.update_gui)
        self.timer_gui.start(100)

    def debug_callback_py(
            self,
            severity: xr.DebugUtilsMessageSeverityFlagsEXT,
            _type: xr.DebugUtilsMessageTypeFlagsEXT,
            data: ctypes.POINTER(xr.DebugUtilsMessengerCallbackDataEXT),
            _user_data: ctypes.c_void_p,
    ) -> bool:
        d = data.contents
        # TODO structure properties to return unicode strings
        self.logger.log(py_log_level(severity),
                        f"{d.function_name.decode()}: {d.message.decode()}")
        return True

    def setup_cameras(self):
        self.near_plane = 0.01
        self.far_plane = 10000.0
        self.camera = [SoFrustumCamera(), SoFrustumCamera()]
        self.hmdrot = SbRotation()
        self.hmdpos = SbVec3f()
        # 0 - left eye, 1 - right eye
        for eye_index in range(2):
            self.camera[eye_index].viewportMapping.setValue(
                SoCamera.LEAVE_ALONE)

    def setup_scene(self):
        # coin3d setup
        self.vp_reg = SbViewportRegion(
            self.render_target_size[0],
            self.render_target_size[1])
        # scene manager overhead over render manager seems to be pretty small
        self.m_sceneManager = SoSceneManager()
        self.environ = SoEnvironment()
        # done in read_preferences
        # self.environ.ambientIntensity.setValue(self.ambient_light_intensity)
        # without ambient lighting some places would be completely dark
        self.m_sceneManager.setViewportRegion(self.vp_reg)
        self.m_sceneManager.setBackgroundColor(SbColor(0.6, 0.6, 0.8))
        self.light = SoDirectionalLight()
        self.light.direction.setValue(-1, -1, -1)
        # done in read_preferences
        # self.light.intensity.setValue(self.directional_light_intensity)
        self.light.color.setValue(1, 1, 1)
        scale = SoScale()
        # OpenXR uses meters not millimeters
        scale.scaleFactor.setValue(0.001, 0.001, 0.001)
        rot = SoRotationXYZ()  # rotate scene to set Z as vertical
        rot.axis.setValue(SoRotationXYZ.X)
        rot.angle.setValue(-pi / 2)
        self.sg = SoSeparator()  # placeholder for scenegraph
        # store complete transformation of world, including artificial movement
        self.world_transform = SoTransform()
        self.world_separator = SoSeparator()
        # this rotation is only to make FC scene Z-Up
        self.world_separator.addChild(rot)
        self.world_separator.addChild(scale)
        self.world_separator.addChild(self.sg)  # add FreeCAD active scenegraph
        self.cgrp = [SoGroup(), SoGroup()]  # group for camera
        self.sgrp = [SoGroup(), SoGroup()]  # group for scenegraph
        self.root_scene = [SoSeparator(), SoSeparator()]
        for eye_index in range(2):
            self.root_scene[eye_index].ref()
            self.root_scene[eye_index].addChild(self.cgrp[eye_index])
            self.cgrp[eye_index].addChild(self.camera[eye_index])
            self.root_scene[eye_index].addChild(self.sgrp[eye_index])
            self.sgrp[eye_index].addChild(self.environ)
            self.sgrp[eye_index].addChild(self.light)
            for hand in range(len(self.xr_con)):
                self.sgrp[eye_index].addChild(
                    self.xr_con[hand].get_controller_scenegraph())
                if self.xr_con[hand].get_ray_scenegraph():
                    self.sgrp[eye_index].addChild(
                        self.xr_con[hand].get_ray_scenegraph())  # ray for controller
            # add menu
            self.sgrp[eye_index].addChild(
                self.con_menu.get_menu_scenegraph())
            # add world (scene without controllers and gui elements)
            self.sgrp[eye_index].addChild(self.world_separator)

    def setup_controllers(self):
        # initialise scenegraphs for controllers
        self.xr_con = [
            conXR.xrController(
                self.primary_con,
                ray=True,
                log_level=self.log_level),
            conXR.xrController(
                self.secondary_con,
                ray=True,
                log_level=self.log_level)]
        # create movement object for world transformation based on controller
        # input
        self.mov_xr = movXR.xrMovement()

    def setup_menus(self):
        # initialize menus floating in the 3D view
        self.con_menu = menuCoin.coinMenu()
        self.hide_menu_timer = QTimer()
        self.hide_menu_timer.setSingleShot(True)
        QObject.connect(self.hide_menu_timer, SIGNAL("timeout()"), self.con_menu.hide_menu)

    def read_preferences(self):
        # read from user preferences
        self.user_mov_speed = pref.preferences().GetInt("LinearSpeed", 50) / 100
        self.user_rot_speed = pref.preferences().GetInt("RotationalSpeed", 50) / 100
        self.ambient_light_intensity = pref.preferences().GetInt(
            "AmbientLightIntesity", 40) / 100
        self.directional_light_intensity = pref.preferences().GetInt(
            "DirectionalLightIntesity", 60) / 100
        self.environ.ambientIntensity.setValue(self.ambient_light_intensity)
        self.light.intensity.setValue(self.directional_light_intensity)
        self.sample_count = pref.preferences().GetInt(
            "MSAA", 4)  # MSAA number of samples, requires restart
        movement_type = pref.preferences().GetString(
            "Movement", "ARCH")
        self.mov_xr.set_movement_type(movement_type)
        # preselecting button in the VR menu
        if (movement_type == "FREE"):
            self.con_menu.select_widget_by_name("free_mov_button")
        elif (movement_type == "ARCH"):
            self.con_menu.select_widget_by_name("arch_mov_button")
        self.con_menu.select_widget_by_name(
            "lin_speed_slider", self.user_mov_speed)
        self.con_menu.select_widget_by_name(
            "rot_speed_slider", self.user_rot_speed)

    def reload_scenegraph(self):
        sg = Gui.ActiveDocument.ActiveView.getSceneGraph()  # get active scenegraph
        self.world_separator.replaceChild(self.sg, sg)
        self.sg = sg

    def prepare_xr_instance(self):
        discovered_extensions = xr.enumerate_instance_extension_properties()
        if xr.EXT_DEBUG_UTILS_EXTENSION_NAME not in discovered_extensions:
            self.enable_debug = False
        requested_extensions = [xr.KHR_OPENGL_ENABLE_EXTENSION_NAME]
        if self.enable_debug:
            requested_extensions.append(xr.EXT_DEBUG_UTILS_EXTENSION_NAME)
        for extension in requested_extensions:
            assert extension in discovered_extensions
        app_info = xr.ApplicationInfo(
            application_name="xr_viewer",
            application_version=0,
            engine_name="pyopenxr",
            engine_version=xr.PYOPENXR_CURRENT_API_VERSION,
            api_version=xr.Version(1, 0, xr.XR_VERSION_PATCH),
        )
        ici = xr.InstanceCreateInfo(
            application_info=app_info,
            enabled_extension_names=requested_extensions,
        )
        dumci = xr.DebugUtilsMessengerCreateInfoEXT()
        if self.enable_debug:
            dumci.message_severities = ALL_SEVERITIES
            dumci.message_types = ALL_TYPES
            dumci.user_data = None  # TODO
            dumci.user_callback = self.debug_callback
            ici.next = ctypes.cast(
                ctypes.pointer(dumci),
                ctypes.c_void_p)  # TODO: yuck
        self.instance = xr.create_instance(ici)
        # TODO: pythonic wrapper
        self.pxrGetOpenGLGraphicsRequirementsKHR = ctypes.cast(
            xr.get_instance_proc_addr(
                self.instance,
                "xrGetOpenGLGraphicsRequirementsKHR",
            ),
            xr.PFN_xrGetOpenGLGraphicsRequirementsKHR
        )
        instance_props = xr.get_instance_properties(self.instance)
        self.logger.debug("Instance properties: %s", instance_props)
        if platform.system() == 'Linux' and instance_props.runtime_name == b"SteamVR/OpenXR" and instance_props.runtime_version != 4294967296:  # 4294967296 is linux_v1.14 1.14.16
            print("SteamVR/OpenXR on Linux detected, enabling workarounds")
            # Enabling workaround for https://github.com/ValveSoftware/SteamVR-for-Linux/issues/422,
            # and https://github.com/ValveSoftware/SteamVR-for-Linux/issues/479
            # destroy_instance() causes SteamVR to hang and never recover
            self.linux_steamvr_broken_destroy_instance = True

    def prepare_xr_system(self):
        get_info = xr.SystemGetInfo(xr.FormFactor.HEAD_MOUNTED_DISPLAY)
        self.system_id = xr.get_system(
            self.instance, get_info)  # TODO: not a pointer
        view_configs = xr.enumerate_view_configurations(
            self.instance, self.system_id)
        # TODO: equality...
        assert view_configs[0] == xr.ViewConfigurationType.PRIMARY_STEREO.value
        view_config_views = xr.enumerate_view_configuration_views(
            self.instance, self.system_id, xr.ViewConfigurationType.PRIMARY_STEREO)
        assert len(view_config_views) == 2
        assert view_config_views[0].recommended_image_rect_height == view_config_views[1].recommended_image_rect_height
        self.max_ss_count = view_config_views[0].max_swapchain_sample_count
        self.render_target_size = (
            view_config_views[0].recommended_image_rect_width * 2,
            view_config_views[0].recommended_image_rect_height)
        result = self.pxrGetOpenGLGraphicsRequirementsKHR(
            self.instance, self.system_id, ctypes.byref(
                self.graphics_requirements))  # TODO: pythonic wrapper
        result = xr.exception.check_result(xr.Result(result))
        if result.is_exception():
            raise result

    def initializeGL(self):
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        self.gl_logger = QOpenGLDebugLogger(self)
        self.gl_logger.initialize()
        self.gl_logger.messageLogged.connect(self.log_message)
        self.gl_logger.startLogging()

        w, h = self.render_target_size
        # configure MSAA
        GL.glEnable(GL.GL_MULTISAMPLE)
        self.fbo_msaa_id = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo_msaa_id)
        # create a multisampled color attachment texture
        msaa_color_buf = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, msaa_color_buf)
        GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE,
                                   self.sample_count,
                                   GL.GL_RGBA8,
                                   w,
                                   h,
                                   GL.GL_TRUE)
        GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, 0)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER,
                                  GL.GL_COLOR_ATTACHMENT0,
                                  GL.GL_TEXTURE_2D_MULTISAMPLE,
                                  msaa_color_buf,
                                  0)
        # create a multisampled renderbuffer object
        self.fbo_depth_buffer = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.fbo_depth_buffer)
        GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER,
                                            self.sample_count,
                                            GL.GL_DEPTH24_STENCIL8,
                                            w,
                                            h)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)
        GL.glFramebufferRenderbuffer(
            GL.GL_DRAW_FRAMEBUFFER,
            GL.GL_DEPTH_STENCIL_ATTACHMENT,
            GL.GL_RENDERBUFFER,
            self.fbo_depth_buffer,
        )

        # target framebuffer
        self.fbo_id = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo_id)

        tex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex)
        GL.glTexImage2D(GL.GL_TEXTURE_2D,
                        0,
                        GL.GL_RGBA8,
                        w,
                        h,
                        0,
                        GL.GL_RGBA,
                        GL.GL_UNSIGNED_BYTE,
                        None)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D,
            GL.GL_TEXTURE_MIN_FILTER,
            GL.GL_LINEAR)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D,
            GL.GL_TEXTURE_MAG_FILTER,
            GL.GL_LINEAR)
        # only color buffer is needed
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER,
            GL.GL_COLOR_ATTACHMENT0,
            GL.GL_TEXTURE_2D,
            tex,
            0)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def prepare_window(self):
        self.resize(
            self.render_target_size[0] // 4,
            self.render_target_size[1] // 4)

    def prepare_xr_session(self):
        if windowing_interface == 'WGL':
            self.graphics_binding.h_dc = WGL.wglGetCurrentDC()
            self.graphics_binding.h_glrc = WGL.wglGetCurrentContext()
        elif windowing_interface == 'GLX':
            self.graphics_binding.x_display = GLX.glXGetCurrentDisplay()
            self.graphics_binding.glx_context = GLX.glXGetCurrentContext()
            self.graphics_binding.glx_drawable = GLX.glXGetCurrentDrawable()
        elif windowing_interface == 'EGL':
            display_instance = LP_wl_display(EGL.wl_display())
            self.graphics_binding.display = display_instance
        else:
            print("Cannot create XR Session")
            return
        pp = ctypes.cast(
            ctypes.pointer(
                self.graphics_binding),
            ctypes.c_void_p)
        sci = xr.SessionCreateInfo(0, self.system_id, next=pp)
        self.session = xr.create_session(self.instance, sci)
        reference_spaces = xr.enumerate_reference_spaces(self.session)
        for rs in reference_spaces:
            self.logger.debug(
                f"Session supports reference space {xr.ReferenceSpaceType(rs)}")
        # TODO: default constructors for Quaternion, Vector3f, Posef,
        # ReferenceSpaceCreateInfo
        rsci = xr.ReferenceSpaceCreateInfo(
            xr.ReferenceSpaceType.STAGE,
            xr.Posef(xr.Quaternionf(0, 0, 0, 1), xr.Vector3f(0, 0, 0))
        )
        self.projection_layer.space = xr.create_reference_space(
            self.session, rsci)
        swapchain_formats = xr.enumerate_swapchain_formats(self.session)
        for scf in swapchain_formats:
            self.logger.debug(
                f"Session supports swapchain format {stringForFormat[scf]}")

    def prepare_xr_swapchain(self):
        self.swapchain_create_info.usage_flags = xr.SWAPCHAIN_USAGE_TRANSFER_DST_BIT
        self.swapchain_create_info.format = GL.GL_SRGB8_ALPHA8
        self.swapchain_create_info.sample_count = 1
        self.swapchain_create_info.array_size = 1
        self.swapchain_create_info.face_count = 1
        self.swapchain_create_info.mip_count = 1
        self.swapchain_create_info.width = self.render_target_size[0]
        self.swapchain_create_info.height = self.render_target_size[1]
        self.swapchain = xr.create_swapchain(
            self.session, self.swapchain_create_info)
        self.swapchain_images = xr.enumerate_swapchain_images(
            self.swapchain, xr.SwapchainImageOpenGLKHR)
        for i, si in enumerate(self.swapchain_images):
            self.logger.debug(
                f"Swapchain image {i} type = {xr.StructureType(si.type)}")

    def prepare_xr_composition_layers(self):
        self.projection_layer.view_count = 2
        self.projection_layer.views = self.projection_layer_views
        for eye_index in range(2):
            layer_view = self.projection_layer_views[eye_index]
            layer_view.sub_image.swapchain = self.swapchain
            layer_view.sub_image.image_rect.extent = xr.Extent2Di(
                self.render_target_size[0] // 2,
                self.render_target_size[1],
            )
            if eye_index == 1:
                layer_view.sub_image.image_rect.offset.x = layer_view.sub_image.image_rect.extent.width

    def prepare_xr_controls(self):
        hand_count = self.hand_count
        self.action_set = xr.create_action_set(
            instance=self.instance,
            create_info=xr.ActionSetCreateInfo(
                action_set_name="baseactionset",
                localized_action_set_name="Base Action Set",
                priority=0,
            ),
        )

        self.hand_paths = (xr.Path * hand_count)(
            xr.string_to_path(self.instance, "/user/hand/left"),
            xr.string_to_path(self.instance, "/user/hand/right"),
        )

        self.pose_action = xr.create_action(
            action_set=self.action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.POSE_INPUT,  # XR_ACTION_TYPE_POSE_INPUT
                action_name="hand_pose",
                localized_action_name="Hand pose",
                count_subaction_paths=len(self.hand_paths),
                subaction_paths=self.hand_paths,
            ),
        )

        self.x_lever_action = xr.create_action(
            action_set=self.action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.FLOAT_INPUT,  # XR_ACTION_TYPE_FLOAT_INPUT
                action_name="x_lever",
                localized_action_name="Move a lever left or right",
                count_subaction_paths=len(self.hand_paths),
                subaction_paths=self.hand_paths,
            ),
        )

        self.y_lever_action = xr.create_action(
            action_set=self.action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.FLOAT_INPUT,
                action_name="y_lever",
                localized_action_name="Move a lever forward or backward",
                count_subaction_paths=len(self.hand_paths),
                subaction_paths=self.hand_paths,
            ),
        )

        self.grab_action = xr.create_action(
            action_set=self.action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.FLOAT_INPUT,
                action_name="triggergrab",
                localized_action_name="Grab Object with Trigger Button",
                count_subaction_paths=len(self.hand_paths),
                subaction_paths=self.hand_paths,
            ),
        )

        pose_path = (
            xr.Path *
            hand_count)(
            xr.string_to_path(
                self.instance,
                "/user/hand/left/input/aim/pose"),
            xr.string_to_path(
                self.instance,
                "/user/hand/right/input/aim/pose"),
        )

        trigger_value_path = (
            xr.Path *
            hand_count)(
            xr.string_to_path(
                self.instance,
                "/user/hand/left/input/trigger/value"),
            xr.string_to_path(
                self.instance,
                "/user/hand/right/input/trigger/value"),
        )

        thumbstick_x_path = (
            xr.Path *
            hand_count)(
            xr.string_to_path(
                self.instance,
                "/user/hand/left/input/thumbstick/x"),
            xr.string_to_path(
                self.instance,
                "/user/hand/right/input/thumbstick/x"),
        )

        thumbstick_y_path = (
            xr.Path *
            hand_count)(
            xr.string_to_path(
                self.instance,
                "/user/hand/left/input/thumbstick/y"),
            xr.string_to_path(
                self.instance,
                "/user/hand/right/input/thumbstick/y"),
        )

        trackpad_x_path = (
            xr.Path *
            hand_count)(
            xr.string_to_path(
                self.instance,
                "/user/hand/left/input/trackpad/x"),
            xr.string_to_path(
                self.instance,
                "/user/hand/right/input/trackpad/x"),
        )

        trackpad_y_path = (
            xr.Path *
            hand_count)(
            xr.string_to_path(
                self.instance,
                "/user/hand/left/input/trackpad/y"),
            xr.string_to_path(
                self.instance,
                "/user/hand/right/input/trackpad/y"),
        )

        # Suggest bindings for the Valve Index Controller.
        valve_index_bindings = [
            xr.ActionSuggestedBinding(self.pose_action, pose_path[0]),
            xr.ActionSuggestedBinding(self.pose_action, pose_path[1]),
            xr.ActionSuggestedBinding(self.x_lever_action, thumbstick_x_path[0]),
            xr.ActionSuggestedBinding(self.x_lever_action, thumbstick_x_path[1]),
            xr.ActionSuggestedBinding(self.y_lever_action, thumbstick_y_path[0]),
            xr.ActionSuggestedBinding(self.y_lever_action, thumbstick_y_path[1]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[0]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[1]),

        ]
        xr.suggest_interaction_profile_bindings(
            instance=self.instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    self.instance,
                    "/interaction_profiles/valve/index_controller",
                ),
                count_suggested_bindings=len(valve_index_bindings),
                suggested_bindings=(
                    xr.ActionSuggestedBinding *
                    len(valve_index_bindings))(
                    *
                    valve_index_bindings),
            ),
        )

        # Suggest bindings for the Vive Controller.
        vive_bindings = [
            xr.ActionSuggestedBinding(self.pose_action, pose_path[0]),
            xr.ActionSuggestedBinding(self.pose_action, pose_path[1]),
            xr.ActionSuggestedBinding(self.x_lever_action, trackpad_x_path[0]),
            xr.ActionSuggestedBinding(self.x_lever_action, trackpad_x_path[1]),
            xr.ActionSuggestedBinding(self.y_lever_action, trackpad_y_path[0]),
            xr.ActionSuggestedBinding(self.y_lever_action, trackpad_y_path[1]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[0]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[1]),

        ]
        xr.suggest_interaction_profile_bindings(
            instance=self.instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    self.instance,
                    "/interaction_profiles/htc/vive_controller",
                ),
                count_suggested_bindings=len(vive_bindings),
                suggested_bindings=(
                    xr.ActionSuggestedBinding *
                    len(vive_bindings))(
                    *
                    vive_bindings),
            ),
        )

        # Suggest bindings for the Oculus Touch Controller.
        oculus_touch_bindings = [
            xr.ActionSuggestedBinding(self.pose_action, pose_path[0]),
            xr.ActionSuggestedBinding(self.pose_action, pose_path[1]),
            xr.ActionSuggestedBinding(self.x_lever_action, thumbstick_x_path[0]),
            xr.ActionSuggestedBinding(self.x_lever_action, thumbstick_x_path[1]),
            xr.ActionSuggestedBinding(self.y_lever_action, thumbstick_y_path[0]),
            xr.ActionSuggestedBinding(self.y_lever_action, thumbstick_y_path[1]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[0]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[1]),

        ]
        xr.suggest_interaction_profile_bindings(
            instance=self.instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    self.instance,
                    "/interaction_profiles/oculus/touch_controller",
                ),
                count_suggested_bindings=len(oculus_touch_bindings),
                suggested_bindings=(
                    xr.ActionSuggestedBinding *
                    len(oculus_touch_bindings))(
                    *
                    oculus_touch_bindings),
            ),
        )

        # Suggest bindings for the Microsoft Motion Controller.
        microsoft_motion_bindings = [
            xr.ActionSuggestedBinding(self.pose_action, pose_path[0]),
            xr.ActionSuggestedBinding(self.pose_action, pose_path[1]),
            xr.ActionSuggestedBinding(self.x_lever_action, thumbstick_x_path[0]),
            xr.ActionSuggestedBinding(self.x_lever_action, thumbstick_x_path[1]),
            xr.ActionSuggestedBinding(self.y_lever_action, thumbstick_y_path[0]),
            xr.ActionSuggestedBinding(self.y_lever_action, thumbstick_y_path[1]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[0]),
            xr.ActionSuggestedBinding(self.grab_action, trigger_value_path[1]),

        ]
        xr.suggest_interaction_profile_bindings(
            instance=self.instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    self.instance,
                    "/interaction_profiles/microsoft/motion_controller",
                ),
                count_suggested_bindings=len(microsoft_motion_bindings),
                suggested_bindings=(
                    xr.ActionSuggestedBinding *
                    len(microsoft_motion_bindings))(
                    *
                    microsoft_motion_bindings),
            ),
        )

        action_space_info = xr.ActionSpaceCreateInfo(
            action=self.pose_action,
            # pose_in_action_space # w already defaults to 1 in python...
            subaction_path=self.hand_paths[0],
        )

        self.hand_space = (xr.Space * hand_count)(*([xr.Space()] * hand_count))

        assert action_space_info.pose_in_action_space.orientation.w == 1
        self.hand_space[0] = xr.create_action_space(
            session=self.session,
            create_info=action_space_info,
        )

        action_space_info = xr.ActionSpaceCreateInfo(
            action=self.pose_action,
            subaction_path=self.hand_paths[1],
        )
        assert action_space_info.pose_in_action_space.orientation.w == 1
        self.hand_space[1] = xr.create_action_space(
            session=self.session,
            create_info=action_space_info,
        )

        xr.attach_session_action_sets(
            session=self.session,
            attach_info=xr.SessionActionSetsAttachInfo(
                count_action_sets=1,
                action_sets=ctypes.pointer(self.action_set),
            ),
        )

    def update_xr_controls(self):
        hand_count = self.hand_count
        # Sync actions
        active_action_set = xr.ActiveActionSet(self.action_set, xr.NULL_PATH)
        try:
            xr.sync_actions(
                self.session,
                xr.ActionsSyncInfo(
                    count_active_action_sets=1,
                    active_action_sets=ctypes.pointer(active_action_set)
                ),
            )
        except xr.exception.SessionNotFocused:
            self.logger.debug("session  not focused")
            return
        # # Get pose and actions for each hand
        for hand in range(hand_count):
            # session.getActionStatePose(getInfo, poseState);
            pose_state = xr.get_action_state_pose(
                session=self.session,
                get_info=xr.ActionStateGetInfo(
                    action=self.pose_action,
                    subaction_path=self.hand_paths[hand],
                ),
            )
            # xrSpaceLocation contains "pose" field with position and
            # orientation
            space_location = xr.locate_space(
                space=self.hand_space[hand],
                base_space=self.projection_layer.space,
                time=self.frame_state.predicted_display_time,
            )
            if (space_location.location_flags &
                    xr.SPACE_LOCATION_POSITION_VALID_BIT):
                self.xr_con[hand].show_controller()
                self.xr_con[hand].update_pose(
                    space_location, self.world_transform)  # definition in controllerXR.py
                # Update actions
                x_lever_value = xr.get_action_state_float(
                    self.session,
                    xr.ActionStateGetInfo(
                        action=self.x_lever_action,
                        subaction_path=self.hand_paths[hand],
                    ),
                )
                y_lever_value = xr.get_action_state_float(
                    self.session,
                    xr.ActionStateGetInfo(
                        action=self.y_lever_action,
                        subaction_path=self.hand_paths[hand],
                    ),
                )
                grab_value = xr.get_action_state_float(
                    self.session,
                    xr.ActionStateGetInfo(
                        action=self.grab_action,
                        subaction_path=self.hand_paths[hand],
                    ),
                )
                self.xr_con[hand].update_lever(x_lever_value, y_lever_value)
                self.xr_con[hand].update_grab(grab_value)
            else:
                self.xr_con[hand].hide_controller()

    def poll_xr_events(self):
        while True:
            try:
                event_buffer = xr.poll_event(self.instance)
                event_type = xr.StructureType(event_buffer.type)
                if event_type == xr.StructureType.EVENT_DATA_SESSION_STATE_CHANGED:
                    self.on_session_state_changed(event_buffer)
            except xr.EventUnavailable:
                break

    def on_session_state_changed(self, session_state_changed_event):
        # TODO: it would be nice to avoid this horrible cast...
        event = ctypes.cast(
            ctypes.byref(session_state_changed_event),
            ctypes.POINTER(xr.EventDataSessionStateChanged)).contents
        # TODO: enum property
        self.session_state = xr.SessionState(event.state)
        if self.session_state == xr.SessionState.READY:
            if not self.quit:
                sbi = xr.SessionBeginInfo(
                    xr.ViewConfigurationType.PRIMARY_STEREO)
                xr.begin_session(self.session, sbi)
        elif self.session_state == xr.SessionState.STOPPING:
            xr.end_session(self.session)
            self.session = None
            self.quit = True

    def start_xr_frame(self) -> bool:
        if self.session_state in [
            xr.SessionState.READY,
            xr.SessionState.FOCUSED,
            xr.SessionState.SYNCHRONIZED,
            xr.SessionState.VISIBLE,
        ]:
            frame_wait_info = xr.FrameWaitInfo(None)
            try:
                self.frame_state = xr.wait_frame(self.session, frame_wait_info)
                xr.begin_frame(self.session, None)
                return True
            except xr.ResultException:
                return False
        return False

    def end_xr_frame(self):
        frame_end_info = xr.FrameEndInfo(
            self.frame_state.predicted_display_time,
            xr.EnvironmentBlendMode.OPAQUE
        )
        if self.frame_state.should_render:
            for eye_index in range(2):
                layer_view = self.projection_layer_views[eye_index]
                eye_view = self.eye_view_states[eye_index]
                layer_view.fov = eye_view.fov
                layer_view.pose = eye_view.pose
            frame_end_info.layers = [ctypes.byref(self.projection_layer), ]
        xr.end_frame(self.session, frame_end_info)

    def check_teleport_jump(self):
        # teleport implementation
        hand = self.secondary_con
        if self.xr_con[hand].get_ray_scenegraph():
            if (self.xr_con[hand].get_buttons_states().grab >= 0.5
                    and self.xr_con[hand].get_hist_buttons_states().grab < 0.5):
                # just pressed
                self.xr_con[hand].show_ray()
            elif (self.xr_con[hand].get_buttons_states().grab > 0.5):
                # traverse just to update the ray view
                self.xr_con[hand].find_picked_coin_object(
                    self.world_separator, self.vp_reg, self.near_plane, self.far_plane)
            elif (self.xr_con[hand].get_buttons_states().grab < 0.5
                  and self.xr_con[hand].get_hist_buttons_states().grab >= 0.5):
                # just released
                # do traversal only if trigger is pressed or just released,
                # because it is expensive
                # traverse only the world, avoid picking controller
                # gizmos or other non-world objects
                coin_picked_point, coin_picked_p_coords = self.xr_con[hand].find_picked_coin_object(
                    self.world_separator, self.vp_reg, self.near_plane, self.far_plane)
                if (coin_picked_point):
                    teleport_transform = SoTransform()
                    teleport_transform.translation.setValue(
                        SbVec3f(coin_picked_p_coords) -
                        self.camera[0].position.getValue() +
                        SbVec3f(
                            0.0,
                            self.hmdpos[1],
                            0.0))
                    self.world_transform.combineRight(teleport_transform)
                self.xr_con[hand].hide_ray()

    def check_menu_selection(self):
        # menu implementation, hidden by default, shows if trigger pressed
        hand = self.primary_con
        if self.xr_con[hand].get_ray_scenegraph():
            # if just pressed
            if (self.xr_con[hand].get_buttons_states().grab >= 0.5
                    and self.xr_con[hand].get_hist_buttons_states().grab < 0.5):
                self.hide_menu_timer.stop()
                # menus are independent from controller gizmos
                # location stays after showing the menu
                pos = self.xr_con[hand].get_global_transf().translation
                rot = self.xr_con[hand].get_global_transf().rotation
                if not self.hide_menu_timer.isActive(): # menu still visible
                    self.con_menu.update_location(pos, rot)
                self.con_menu.show_menu()
                self.xr_con[hand].show_ray()
            # if pressed
            elif (self.xr_con[hand].get_buttons_states().grab > 0.5):
                # show the ray
                self.xr_con[hand].find_picked_coin_object(
                    self.con_menu.get_menu_scenegraph(),
                    self.vp_reg,
                    self.near_plane,
                    self.far_plane)
            # if just released
            elif (self.xr_con[hand].get_buttons_states().grab < 0.5
                  and self.xr_con[hand].get_hist_buttons_states().grab >= 0.5):
                # traverse menu scenegraph
                menu_picked_point, menu_picked_p_coords = self.xr_con[hand].find_picked_coin_object(
                    self.con_menu.get_menu_scenegraph(), self.vp_reg, self.near_plane, self.far_plane)
                if (menu_picked_point):
                    tail = self.xr_con[hand].get_picked_tail()
                    coords = self.xr_con[hand].get_picked_tex_coords()
                    widget = self.con_menu.find_picked_widget(tail, coords)
                    self.process_menu_selection(widget)
                self.xr_con[hand].hide_ray()
                # hide delay allows user to see what he has chosen
                self.hide_menu_timer.start(1000)

    def process_menu_selection(self, widget):
        name = widget.name
        if (name == "free_mov_button"):
            pref.preferences().SetString(
                "Movement", "FREE")
            self.mov_xr.set_movement_type("FREE")
        elif (name == "arch_mov_button"):
            pref.preferences().SetString(
                "Movement", "ARCH")
            self.mov_xr.set_movement_type("ARCH")
        elif (name == "lin_speed_slider"):
            self.user_mov_speed = widget.value
            pref.preferences().SetInt("LinearSpeed",
                                      round(self.user_mov_speed * 100))
        elif (name == "rot_speed_slider"):
            self.user_rot_speed = widget.value
            pref.preferences().SetInt("RotationalSpeed",
                                      round(self.user_rot_speed * 100))

    def update_xr_movement(self):
        curr_time = self.frame_state.predicted_display_time / \
            1e9  # XrTime is measured in nanoseconds (int64)
        self.frame_duration = curr_time - self.old_time
        self.old_time = curr_time

        self.check_teleport_jump()

        if pref.pref_updated:
            self.read_preferences()
            pref.reset_upd_flag()
        self.check_menu_selection()

        # additional multiplier if 0 - 1 range is too small
        aux_mul = 2
        # translation (movement) speed
        final_mov_speed = self.frame_duration * \
            self.user_mov_speed * aux_mul
        final_rot_speed = self.frame_duration * \
            self.user_rot_speed * aux_mul
        # transformation with movement at this particular moment
        # combine it with existing world transformation
        self.world_transform.combineLeft(self.mov_xr.calculate_transformation(
            self.hmdpos, self.hmdrot,
            self.xr_con[self.primary_con],
            self.xr_con[self.secondary_con],
            final_mov_speed, final_rot_speed))

    def update_xr_views(self):
        near_plane = self.near_plane
        far_plane = self.far_plane
        vi = xr.ViewLocateInfo(
            xr.ViewConfigurationType.PRIMARY_STEREO,
            self.frame_state.predicted_display_time,
            self.projection_layer.space,
        )
        vs, self.eye_view_states = xr.locate_views(self.session, vi)
        for eye_index, view_state in enumerate(self.eye_view_states):
            self.hmdrot = SbRotation(
                view_state.pose.orientation.x,
                view_state.pose.orientation.y,
                view_state.pose.orientation.z,
                view_state.pose.orientation.w)
            self.hmdpos = SbVec3f(
                view_state.pose.position.x,
                view_state.pose.position.y,
                view_state.pose.position.z)  # get global position and orientation for both cameras
            cam_transform = SoTransform()
            cam_transform.translation.setValue(
                self.world_transform.translation.getValue())  # transfer values only
            cam_transform.rotation.setValue(
                self.world_transform.rotation.getValue())
            cam_transform.center.setValue(
                self.world_transform.center.getValue())
            hmd_transform = SoTransform()
            hmd_transform.translation.setValue(self.hmdpos)
            hmd_transform.rotation.setValue(self.hmdrot)
            # combine real hmd and arificial (stick-driven) camera movement
            cam_transform.combineLeft(hmd_transform)
            pfLeft = tan(view_state.fov.angle_left)
            pfRight = tan(view_state.fov.angle_right)
            pfTop = tan(view_state.fov.angle_up)
            pfBottom = tan(view_state.fov.angle_down)
            self.camera[eye_index].orientation.setValue(
                cam_transform.rotation.getValue())
            self.camera[eye_index].position.setValue(
                cam_transform.translation.getValue())
            self.camera[eye_index].aspectRatio.setValue(
                (pfTop - pfBottom) / (pfRight - pfLeft))
            self.camera[eye_index].nearDistance.setValue(near_plane)
            self.camera[eye_index].farDistance.setValue(far_plane)
            self.camera[eye_index].left.setValue(near_plane * pfLeft)
            self.camera[eye_index].right.setValue(near_plane * pfRight)
            self.camera[eye_index].top.setValue(near_plane * pfTop)
            self.camera[eye_index].bottom.setValue(near_plane * pfBottom)

    def update_gui(self):
        if self.mirror_window:
            self.parentWidget().setWindowTitle(
                "Render time: " +
                "{:.2f}".format(
                    self.render_duration /
                    1e6) +
                " ms Predicted frame time: " +
                "{:.2f}".format(
                    self.frame_duration *
                    1000) +
                " ms")

    def update_render(self):
        if self.mirror_window:
            self.update()
        else:
            self.makeCurrent()
            self.paintGL()
            self.doneCurrent()

    def paintGL(self):
        if self.fbo_id is not None:  # make sure that initializeGL happened
            self.poll_xr_events()
            if self.quit:
                return
            if self.start_xr_frame():
                if self.frame_state.should_render:
                    self.update_xr_controls()
                    self.update_xr_movement()
                    self.update_xr_views()
                    ren_timer = QElapsedTimer()
                    ren_timer.start()
                    self.oldfb = self.defaultFramebufferObject()  # widget's (not context) DFO
                    ai = xr.SwapchainImageAcquireInfo(None)
                    swapchain_index = xr.acquire_swapchain_image(
                        self.swapchain, ai)
                    wi = xr.SwapchainImageWaitInfo(xr.INFINITE_DURATION)
                    xr.wait_swapchain_image(self.swapchain, wi)
                    GL.glUseProgram(0)
                    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo_msaa_id)
                    w, h = self.render_target_size
                    # "render" to the swapchain image
                    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
                    GL.glEnable(GL.GL_BLEND)
                    GL.glEnable(GL.GL_SCISSOR_TEST)
                    GL.glScissor(0, 0, w // 2, h)

                    self.vp_reg.setViewportPixels(0, 0, w // 2, h)
                    self.m_sceneManager.setViewportRegion(self.vp_reg)
                    self.m_sceneManager.setSceneGraph(self.root_scene[0])
                    GL.glEnable(GL.GL_CULL_FACE)
                    GL.glEnable(GL.GL_DEPTH_TEST)
                    self.m_sceneManager.render()
                    GL.glDisable(GL.GL_CULL_FACE)
                    GL.glDisable(GL.GL_DEPTH_TEST)

                    GL.glScissor(w // 2, 0, w // 2, h)
                    self.vp_reg.setViewportPixels(w // 2, 0, w // 2, h)
                    self.m_sceneManager.setViewportRegion(self.vp_reg)
                    self.m_sceneManager.setSceneGraph(self.root_scene[1])
                    GL.glEnable(GL.GL_CULL_FACE)
                    GL.glEnable(GL.GL_DEPTH_TEST)
                    self.m_sceneManager.render()
                    GL.glDisable(GL.GL_CULL_FACE)
                    GL.glDisable(GL.GL_DEPTH_TEST)

                    GL.glDisable(GL.GL_SCISSOR_TEST)

                    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo_id)
                    sw_image = self.swapchain_images[swapchain_index]
                    GL.glFramebufferTexture(
                        GL.GL_FRAMEBUFFER,
                        GL.GL_COLOR_ATTACHMENT0,
                        sw_image.image,
                        0,
                    )

                    GL.glBindFramebuffer(
                        GL.GL_READ_FRAMEBUFFER, self.fbo_msaa_id)
                    GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.fbo_id)
                    GL.glBlitFramebuffer(
                        0, 0, w, h, 0, 0,
                        w, h,
                        GL.GL_COLOR_BUFFER_BIT,
                        GL.GL_NEAREST
                    )
                    self.render_duration = ren_timer.nsecsElapsed()

                    ri = xr.SwapchainImageReleaseInfo()
                    xr.release_swapchain_image(self.swapchain, ri)
                    if self.mirror_window:
                        # fast blit from the fbo to the window surface
                        GL.glBindFramebuffer(
                            GL.GL_READ_FRAMEBUFFER, self.fbo_id)
                        GL.glBindFramebuffer(
                            GL.GL_DRAW_FRAMEBUFFER, self.oldfb)
                        GL.glBlitFramebuffer(
                            0, 0, w, h, 0, 0,
                            self.size().width(), self.size().height(),
                            GL.GL_COLOR_BUFFER_BIT,
                            GL.GL_NEAREST
                        )
                    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.oldfb)

                self.end_xr_frame()

    def terminate(self):
        self.timer.stop()
        self.quit = True
        self.makeCurrent()
        self.gl_logger.stopLogging()
        if self.fbo_id is not None:
            GL.glDeleteFramebuffers(1, [self.fbo_id])
            self.fbo_id = None
        if self.fbo_depth_buffer is not None:
            GL.glDeleteRenderbuffers(1, [self.fbo_depth_buffer])
            self.fbo_depth_buffer = None
        if self.action_set is not None:
            for hand in range(self.hand_count):
                if self.hand_space[hand] is not None:
                    xr.destroy_space(self.hand_space[hand])
                    self.hand_space[hand] = None
            xr.destroy_action_set(self.action_set)
            self.action_set = None
        if self.swapchain is not None:
            xr.destroy_swapchain(self.swapchain)
            self.swapchain = None
        if self.session is not None:
            xr.destroy_session(self.session)
            self.session = None
        self.system_id = None
        if self.instance is not None:
            # Workaround for https://github.com/ValveSoftware/SteamVR-for-Linux/issues/422
            # and https://github.com/ValveSoftware/SteamVR-for-Linux/issues/479
            if not self.linux_steamvr_broken_destroy_instance:
                xr.destroy_instance(self.instance)
            self.instance = None
        for i, rs in enumerate(self.root_scene):
            self.root_scene[i].unref()
        self.doneCurrent()
        self.deleteLater()
        print("XR terminated")

    def disable_mirror(self):
        self.mirror_window = False

    def enable_mirror(self):
        self.mirror_window = True

    def log_message(self, message):
        print(f"OpenGL Debug: {message.message()}")


xr_dock_w = None


def open_xr_viewer():
    if Gui.ActiveDocument is None:
        print("No active view!")
        return
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w is not None:
        print("XR already started, please close it before reopening")
    else:
        xr_dock_w = DockWidget()


def close_xr_viewer():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w is not None:
        xr_dock_w.close()


def open_xr_mirror():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w is not None:
        xr_dock_w.unhide_mirror()


def close_xr_mirror():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w is not None:
        xr_dock_w.hide_mirror()


def reload_scenegraph():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w is not None:
        xr_dock_w.reload_scenegraph()
