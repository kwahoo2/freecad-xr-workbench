# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2023 Adrian Przekwas adrian.v.przekwas@gmail.com        *
# *                                                                         *
# *   Based on gl_example.py https://github.com/cmbruns/pyopenxr_examples   *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
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


import ctypes
import logging

from PySide2.QtWidgets import QOpenGLWidget, QDockWidget
from PySide2.QtGui import QOpenGLContext, QSurfaceFormat
from PySide2.QtCore import Qt, QTimer, QObject, SIGNAL

import shiboken2 as shiboken

import platform
try:
    from OpenGL import GL
    if platform.system() == "Windows":
        from OpenGL import WGL
    elif platform.system() == "Linux":
        from OpenGL import GLX
except ImportError:
    print ("PyOpenGL is required!")

try:
    import xr
except ImportError:
    print ("pyopenxr is required!")

from pivy.coin import SoSeparator
from pivy.coin import SoBaseColor
from pivy.coin import SbColor
from pivy.coin import SoSceneManager
from pivy.coin import SbViewportRegion
from pivy.coin import SoFrustumCamera
from pivy.coin import SoPerspectiveCamera
from pivy.coin import SbVec3f
from pivy.coin import SoCamera
from pivy.coin import SoDirectionalLight
from pivy.coin import SoScale
from pivy.coin import SoTranslation
from pivy.coin import SbRotation
from pivy.coin import SoGroup
from pivy.coin import SoRotationXYZ

import FreeCADGui as Gui

from math import tan, pi

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
        self.xr_widget = XRwidget(log_level=logging.WARNING) # set log_level=logging.DEBUG for more info
        self.setWidget(self.xr_widget)
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

class XRwidget(QOpenGLWidget):
    def __init__(self, parent=None, log_level=logging.WARNING):
        QOpenGLWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
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
        frmt.setSamples(8) # MSAA
        ctx = QOpenGLContext()
        ctx.setFormat(frmt)
        ctx.create()
        self.context = ctx
        print (self.context)

        logging.basicConfig()
        self.logger = logging.getLogger("xr_viewer")
        self.logger.setLevel(log_level)
        self.debug_callback = xr.PFN_xrDebugUtilsMessengerCallbackEXT(self.debug_callback_py)
        # drawing QOpenGLWidget mirror window may degrade frame timing
        self.mirror_window = True
        self.instance = None
        self.system_id = None
        self.pxrCreateDebugUtilsMessengerEXT = None
        self.pxrDestroyDebugUtilsMessengerEXT = None
        self.pxrGetOpenGLGraphicsRequirementsKHR = None
        self.graphics_requirements = xr.GraphicsRequirementsOpenGLKHR()
        if platform.system() == 'Windows':
            self.graphics_binding = xr.GraphicsBindingOpenGLWin32KHR()

        elif platform.system() == 'Linux':
            self.graphics_binding = xr.GraphicsBindingOpenGLXlibKHR()

        else:
            raise NotImplementedError('Unsupported platform')

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
        self.fbo_depth_buffer = None
        self.quit = False
        self.session_state = xr.SessionState.IDLE
        self.frame_state = xr.FrameState()
        self.eye_view_states = None
        self.window_size = None
        self.enable_debug = True
        self.linux_steamvr_broken_destroy_instance = False

        self.prepare_xr_instance()
        self.prepare_xr_system()
        self.prepare_window()
        self.prepare_xr_session()
        self.prepare_xr_swapchain()
        self.prepare_xr_composition_layers()
        self.setup_cameras()
        self.setup_scene()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.frame)
        self.timer.start(0)

    def debug_callback_py(
            self,
            severity: xr.DebugUtilsMessageSeverityFlagsEXT,
            _type: xr.DebugUtilsMessageTypeFlagsEXT,
            data: ctypes.POINTER(xr.DebugUtilsMessengerCallbackDataEXT),
            _user_data: ctypes.c_void_p,
    ) -> bool:
        d = data.contents
        # TODO structure properties to return unicode strings
        self.logger.log(py_log_level(severity), f"{d.function_name.decode()}: {d.message.decode()}")
        return True


    def setup_cameras(self):
        self.nearPlane = 0.01
        self.farPlane = 10000.0
        self.camera = [SoFrustumCamera(), SoFrustumCamera()]
        # 0 - left eye, 1 - right eye
        for eye_index in range (2):
            self.camera[eye_index].viewportMapping.setValue(SoCamera.LEAVE_ALONE)

    def  setup_scene(self):
        # coin3d setup
        self.vpReg = SbViewportRegion(self.render_target_size[0], self.render_target_size[1])
        self.m_sceneManager = SoSceneManager() #scene manager overhead over render manager seems to be pretty #small
        self.m_sceneManager.setViewportRegion(self.vpReg)
        self.m_sceneManager.setBackgroundColor(SbColor(0.0, 0.0, 0.8))
        light = SoDirectionalLight()
        light2 = SoDirectionalLight()
        light2.direction.setValue(-1,-1,-1)
        light2.intensity.setValue(0.6)
        light2.color.setValue(0.8,0.8,1)
        scale = SoScale()
        scale.scaleFactor.setValue(0.001, 0.001, 0.001) #OpenXR uses meters not milimeters
        sg = Gui.ActiveDocument.ActiveView.getSceneGraph()#get active scenegraph
        rot = SoRotationXYZ() # rotate scene to set Z as vertical
        rot.axis.setValue(SoRotationXYZ.X)
        rot.angle.setValue(-pi/2)
        self.camtrans = [SoTranslation(), SoTranslation()]
        self.cgrp = [SoGroup(), SoGroup()] # group for camera
        self.sgrp = [SoGroup(), SoGroup()] # group for scenegraph
        self.rootScene = [SoSeparator(), SoSeparator()]
        for eye_index in range (2):
            self.rootScene[eye_index].ref()
            self.rootScene[eye_index].addChild(self.cgrp[eye_index])
            self.cgrp[eye_index].addChild(self.camtrans[eye_index])
            self.cgrp[eye_index].addChild(self.camera[eye_index])
            self.rootScene[eye_index].addChild(self.sgrp[eye_index])
            self.sgrp[eye_index].addChild(light)
            self.sgrp[eye_index].addChild(light2)
            self.sgrp[eye_index].addChild(scale)
            self.sgrp[eye_index].addChild(rot)
            self.sgrp[eye_index].addChild(sg) # add scenegraph

    def prepare_xr_instance(self):
        discovered_extensions = xr.enumerate_instance_extension_properties()
        if xr.EXT_DEBUG_UTILS_EXTENSION_NAME not in discovered_extensions:
            self.enable_debug = False
        requested_extensions = [xr.KHR_OPENGL_ENABLE_EXTENSION_NAME]
        if self.enable_debug:
            requested_extensions.append(xr.EXT_DEBUG_UTILS_EXTENSION_NAME)
        for extension in requested_extensions:
            assert extension in discovered_extensions
        app_info = xr.ApplicationInfo("xr_viewer", 0, "pyopenxr", 0, xr.XR_CURRENT_API_VERSION)
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
            ici.next = ctypes.cast(ctypes.pointer(dumci), ctypes.c_void_p)  # TODO: yuck
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
        print(instance_props)
        if platform.system() == 'Linux' and instance_props.runtime_name == b"SteamVR/OpenXR" and instance_props.runtime_version != 4294967296: # 4294967296 is linux_v1.14 1.14.16
            print("SteamVR/OpenXR on Linux detected, enabling workarounds")
            # Enabling workaround for https://github.com/ValveSoftware/SteamVR-for-Linux/issues/422,
            # and https://github.com/ValveSoftware/SteamVR-for-Linux/issues/479
            # destroy_instance() causes SteamVR to hang and never recover
            self.linux_steamvr_broken_destroy_instance = True

    def prepare_xr_system(self):
        get_info = xr.SystemGetInfo(xr.FormFactor.HEAD_MOUNTED_DISPLAY)
        self.system_id = xr.get_system(self.instance, get_info)  # TODO: not a pointer
        view_configs = xr.enumerate_view_configurations(self.instance, self.system_id)
        assert view_configs[0] == xr.ViewConfigurationType.PRIMARY_STEREO.value  # TODO: equality...
        view_config_views = xr.enumerate_view_configuration_views(
            self.instance, self.system_id, xr.ViewConfigurationType.PRIMARY_STEREO)
        assert len(view_config_views) == 2
        assert view_config_views[0].recommended_image_rect_height == view_config_views[1].recommended_image_rect_height
        self.render_target_size = (
            view_config_views[0].recommended_image_rect_width * 2,
            view_config_views[0].recommended_image_rect_height)
        result = self.pxrGetOpenGLGraphicsRequirementsKHR(
            self.instance, self.system_id, ctypes.byref(self.graphics_requirements))  # TODO: pythonic wrapper
        result = xr.exception.check_result(xr.Result(result))
        if result.is_exception():
            raise result

    def initializeGL(self):
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        GL.glEnable(GL.GL_MULTISAMPLE)
        self.fbo_depth_buffer = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.fbo_depth_buffer)
        if self.swapchain_create_info.sample_count == 1:
            GL.glRenderbufferStorage(
                GL.GL_RENDERBUFFER,
                GL.GL_DEPTH24_STENCIL8,
                self.swapchain_create_info.width,
                self.swapchain_create_info.height,
            )
        else:
            GL.glRenderbufferStorageMultisample(
                GL.GL_RENDERBUFFER,
                self.swapchain_create_info.sample_count,
                GL.GL_DEPTH24_STENCIL8,
                self.swapchain_create_info.width,
                self.swapchain_create_info.height,
            )
        self.fbo_id = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.fbo_id)
        GL.glFramebufferRenderbuffer(
            GL.GL_DRAW_FRAMEBUFFER,
            GL.GL_DEPTH_STENCIL_ATTACHMENT,
            GL.GL_RENDERBUFFER,
            self.fbo_depth_buffer,
        )
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)

    def prepare_window(self):
        self.resize(self.render_target_size[0] // 4, self.render_target_size[1] // 4)

    def prepare_xr_session(self):
        if platform.system() == 'Windows':
            self.graphics_binding.h_dc = WGL.wglGetCurrentDC()
            self.graphics_binding.h_glrc = WGL.wglGetCurrentContext()
        else:
            self.graphics_binding.x_display = GLX.glXGetCurrentDisplay()
            self.graphics_binding.glx_context = GLX.glXGetCurrentContext()
            self.graphics_binding.glx_drawable = GLX.glXGetCurrentDrawable()
        pp = ctypes.cast(ctypes.pointer(self.graphics_binding), ctypes.c_void_p)
        sci = xr.SessionCreateInfo(0, self.system_id, next=pp)
        self.session = xr.create_session(self.instance, sci)
        reference_spaces = xr.enumerate_reference_spaces(self.session)
        for rs in reference_spaces:
            self.logger.debug(f"Session supports reference space {xr.ReferenceSpaceType(rs)}")
        # TODO: default constructors for Quaternion, Vector3f, Posef, ReferenceSpaceCreateInfo
        rsci = xr.ReferenceSpaceCreateInfo(
            xr.ReferenceSpaceType.STAGE,
            xr.Posef(xr.Quaternionf(0, 0, 0, 1), xr.Vector3f(0, 0, 0))
        )
        self.projection_layer.space = xr.create_reference_space(self.session, rsci)
        swapchain_formats = xr.enumerate_swapchain_formats(self.session)
        for scf in swapchain_formats:
            self.logger.debug(f"Session supports swapchain format {stringForFormat[scf]}")

    def prepare_xr_swapchain(self):
        self.swapchain_create_info.usage_flags = xr.SWAPCHAIN_USAGE_TRANSFER_DST_BIT
        self.swapchain_create_info.format = GL.GL_SRGB8_ALPHA8
        self.swapchain_create_info.sample_count = 1
        self.swapchain_create_info.array_size = 1
        self.swapchain_create_info.face_count = 1
        self.swapchain_create_info.mip_count = 1
        self.swapchain_create_info.width = self.render_target_size[0]
        self.swapchain_create_info.height = self.render_target_size[1]
        self.swapchain = xr.create_swapchain(self.session, self.swapchain_create_info)
        self.swapchain_images = xr.enumerate_swapchain_images(self.swapchain, xr.SwapchainImageOpenGLKHR)
        for i, si in enumerate(self.swapchain_images):
            self.logger.debug(f"Swapchain image {i} type = {xr.StructureType(si.type)}")

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

    def frame(self):
        self.poll_xr_events()
        if self.quit:
            return
        if self.start_xr_frame():
            self.update_xr_views()
            if self.frame_state.should_render:
                # paintGL have to be called explicitly, otherwise VR goggles frame timing will be off
                # update() is still necessary in another place to execute mirror window redraw
                self.paintGL()
            self.end_xr_frame()

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
                sbi = xr.SessionBeginInfo(xr.ViewConfigurationType.PRIMARY_STEREO)
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

    def update_xr_views(self):
        nearPlane = self.nearPlane
        farPlane = self.farPlane
        vi = xr.ViewLocateInfo(
            xr.ViewConfigurationType.PRIMARY_STEREO,
            self.frame_state.predicted_display_time,
            self.projection_layer.space,
        )
        vs, self.eye_view_states = xr.locate_views(self.session, vi)
        for eye_index, view_state in enumerate(self.eye_view_states):
            hmdrot = SbRotation(view_state.pose.orientation.x, view_state.pose.orientation.y, view_state.pose.orientation.z, view_state.pose.orientation.w)
            hmdpos = SbVec3f(view_state.pose.position.x, view_state.pose.position.y, view_state.pose.position.z) #get global position and orientation for both cameras
            pfLeft = tan(view_state.fov.angle_left)
            pfRight = tan(view_state.fov.angle_right)
            pfTop = tan(view_state.fov.angle_up)
            pfBottom = tan(view_state.fov.angle_down)
            self.camera[eye_index].orientation.setValue(hmdrot)
            self.camera[eye_index].position.setValue(hmdpos)
            self.camera[eye_index].aspectRatio.setValue((pfTop - pfBottom)/(pfRight - pfLeft))
            self.camera[eye_index].nearDistance.setValue(nearPlane)
            self.camera[eye_index].farDistance.setValue(farPlane)
            self.camera[eye_index].left.setValue(nearPlane * pfLeft)
            self.camera[eye_index].right.setValue(nearPlane * pfRight)
            self.camera[eye_index].top.setValue(nearPlane * pfTop)
            self.camera[eye_index].bottom.setValue(nearPlane * pfBottom)

    def paintGL(self):
        self.oldfb = self.defaultFramebufferObject() # widget's (not context) DFO

        ai = xr.SwapchainImageAcquireInfo(None)
        swapchain_index = xr.acquire_swapchain_image(self.swapchain, ai)
        wi = xr.SwapchainImageWaitInfo(xr.INFINITE_DURATION)
        xr.wait_swapchain_image(self.swapchain, wi)
        if self.fbo_id != None: # make sure that initializeGL happened
            GL.glUseProgram(0)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo_id)
            sw_image = self.swapchain_images[swapchain_index]
            GL.glFramebufferTexture(
                GL.GL_FRAMEBUFFER,
                GL.GL_COLOR_ATTACHMENT0,
                sw_image.image,
                0,
            )
            w, h = self.render_target_size
            # "render" to the swapchain image
            GL.glEnable(GL.GL_SCISSOR_TEST)
            GL.glScissor(0, 0, w // 2, h)
            self.vpReg.setViewportPixels(0, 0, w // 2, h)
            self.m_sceneManager.setViewportRegion(self.vpReg)
            self.m_sceneManager.setSceneGraph(self.rootScene[0])
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_DEPTH_TEST)
            self.m_sceneManager.render()
            GL.glDisable(GL.GL_CULL_FACE)
            GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glScissor(w // 2, 0, w // 2, h)
            self.vpReg.setViewportPixels(w // 2, 0, w // 2, h)
            self.m_sceneManager.setViewportRegion(self.vpReg)
            self.m_sceneManager.setSceneGraph(self.rootScene[1])
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_DEPTH_TEST)
            self.m_sceneManager.render()
            GL.glDisable(GL.GL_CULL_FACE)
            GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glDisable(GL.GL_SCISSOR_TEST)
            if self.mirror_window:
                # fast blit from the fbo to the window surface
                GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.oldfb)
                GL.glBlitFramebuffer(
                    0, 0, w, h, 0, 0,
                    self.size().width(), self.size().height(),
                    GL.GL_COLOR_BUFFER_BIT,
                    GL.GL_NEAREST
                )
                self.update() # necessary just for mirror window, not VR goggles
                            # (their rendering is triggered by paintGL placed in frame()

            GL.glFramebufferTexture(GL.GL_READ_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, 0, 0)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        ri = xr.SwapchainImageReleaseInfo()
        xr.release_swapchain_image(self.swapchain, ri)

    def terminate(self):
        self.timer.stop()
        self.quit = True
        print (self.context.surface())
        #self.context.makeCurrent(self.context.surface())
        if self.fbo_id is not None:
            GL.glDeleteFramebuffers(1, [self.fbo_id])
            self.fbo_id = None
        if self.fbo_depth_buffer is not None:
            GL.glDeleteRenderbuffers(1, [self.fbo_depth_buffer])
            self.fbo_depth_buffer = None
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
        for i, rs in enumerate(self.rootScene):
            self.rootScene[i].unref()
        self.context.doneCurrent()
        self.deleteLater()
        print ("XR terminated")

    def disable_mirror(self):
        self.mirror_window = False

    def enable_mirror(self):
        self.mirror_window = True



xr_dock_w = None

def open_xr_viewer():
    if Gui.ActiveDocument == None:
        print ("No active view!")
        return
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w != None:
        print ("XR already started, please close it before reopening")
    else:
        xr_dock_w = DockWidget()

def close_xr_viewer():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w != None:
        xr_dock_w.close()


def open_xr_mirror():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w != None:
        xr_dock_w.unhide_mirror()

def close_xr_mirror():
    global xr_dock_w
    if shiboken.isValid(xr_dock_w) and xr_dock_w != None:
        xr_dock_w.hide_mirror()

