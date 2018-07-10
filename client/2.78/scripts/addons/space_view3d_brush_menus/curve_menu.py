# gpl author: Ryan Inch (Imaginer)

from bpy.types import (
        Operator,
        Menu,
        )
from . import utils_core


class BrushCurveMenu(Menu):
    bl_label = "Curve"
    bl_idname = "VIEW3D_MT_sv3_brush_curve_menu"

    @classmethod
    def poll(self, context):
        return utils_core.get_mode() in (
                        utils_core.sculpt, utils_core.vertex_paint,
                        utils_core.weight_paint, utils_core.texture_paint,
                        utils_core.particle_edit
                        )

    def draw(self, context):
        menu = utils_core.Menu(self)
        curves = [["Smooth", "SMOOTH", "SMOOTHCURVE"],
                  ["Sphere", "ROUND", "SPHERECURVE"],
                  ["Root", "ROOT", "ROOTCURVE"],
                  ["Sharp", "SHARP", "SHARPCURVE"],
                  ["Linear", "LINE", "LINCURVE"],
                  ["Constant", "MAX", "NOCURVE"]]

        # add the top slider
        menu.add_item().operator(CurvePopup.bl_idname, icon="RNDCURVE")
        menu.add_item().separator()

        # add the rest of the menu items
        for curve in curves:
            item = menu.add_item().operator("brush.curve_preset",
                                            text=curve[0], icon=curve[2])
            item.shape = curve[1]


class CurvePopup(Operator):
    bl_label = "Adjust Curve"
    bl_idname = "view3d.sv3_curve_popup"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        return utils_core.get_mode() in (
                        utils_core.sculpt, utils_core.vertex_paint,
                        utils_core.weight_paint, utils_core.texture_paint
                        )

    def draw(self, context):
        menu = utils_core.Menu(self)
        has_brush = utils_core.get_brush_link(context, types="brush")

        if utils_core.get_mode() == utils_core.sculpt or \
          utils_core.get_mode() == utils_core.vertex_paint or \
          utils_core.get_mode() == utils_core.weight_paint or \
          utils_core.get_mode() == utils_core.texture_paint:
            if has_brush:
                menu.add_item("column").template_curve_mapping(has_brush,
                                                               "curve", brush=True)
            else:
                menu.add_item().label("No brushes available", icon="INFO")
        else:
            menu.add_item().label("No brushes available", icon="INFO")

    def execute(self, context):
        return context.window_manager.invoke_popup(self, width=180)
