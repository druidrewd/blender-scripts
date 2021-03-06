import bpy


bl_info = {
    "name": "Text Move Toggle",
    "description": "Convenience operators for text editor",
    "author": "kaio",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Text Editor",
    "category": "Misc"
}


class TEXT_OT_move_toggle(bpy.types.Operator):
    """Makes Home key toggle between line begin and first indent"""
    bl_idname = "text.move_toggle"
    bl_label = "Move Toggle"

    @classmethod
    def poll(cls, context):
        return (context.area.type == 'TEXT_EDITOR' and
                context.space_data.text)

    def get_indent(self, text, tab):
        indent = 0
        body = text.select_end_line.body
        while body.find(" " * tab, indent * tab) != -1:
            indent += 1
        return indent

    def execute(self, context):
        st = context.space_data
        caret = st.text.select_end_character
        indent = self.get_indent(st.text, st.tab_width)

        if self.event.shift:
            move = bpy.ops.text.move_select
        else:
            move = bpy.ops.text.move

        if indent:
            if indent * st.tab_width < caret:
                move(type="LINE_BEGIN")
                return move(type="NEXT_WORD")
            elif not caret:
                return move(type="NEXT_WORD")
        return move(type="LINE_BEGIN")

    def invoke(self, context, event):
        self.event = event
        return self.execute(context)

    @classmethod
    def _setup(cls):
        cls._keymaps = []
        kc = bpy.context.window_manager.keyconfigs.addon.keymaps
        get, new = kc.get, kc.new
        km = get('Text', new(name='Text', space_type='TEXT_EDITOR'))

        new = km.keymap_items.new
        kmi = new(cls.bl_idname, 'HOME', 'PRESS')
        kmi = new(cls.bl_idname, 'HOME', 'PRESS', shift=1)
        cls._keymaps.append((km, kmi))

    @classmethod
    def _remove(cls):
        for km, kmi in cls._keymaps:
            km.keymap_items.remove(kmi)
        cls._keymaps.clear()


def classes():
    mod = globals().values()
    return [i for i in mod if hasattr(i, 'mro') and
            bpy.types.bpy_struct in i.mro() and
            i.__module__ == __name__]


def register():
    for cls in classes():
        bpy.utils.register_class(cls)
        if hasattr(cls, '_setup'):
            cls._setup()


def unregister():
    for cls in reversed(classes()):
        if hasattr(cls, '_remove'):
            cls._remove()
        bpy.utils.unregister_class(cls)
