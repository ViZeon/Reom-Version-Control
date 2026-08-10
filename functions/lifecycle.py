import sys
from .. import wrapper, data

def addon_register(classes):
    wrapper.register(classes)
    wrapper.register_keymap(data.OP_VERSION, data.KEY_SAVE, [data.MOD_CTRL], data.PROP_ACTION, data.ACT_SAVE)
    
    mod = sys.modules.get(__package__.split('.')[0]) # Get top-level package
    if mod and getattr(mod, data.AUTO_ENABLED, False):
        setattr(mod, data.AUTO_ENABLED, False)
    else:
        def _startup():
            win, area = wrapper.get_view3d()
            if win and area:
                with wrapper.override(win, area): wrapper.invoke(data.OP_STARTUP)
        wrapper.timer(_startup, data.STARTUP_DELAY)

def addon_unregister(classes): 
    wrapper.unregister_keymaps()
    wrapper.unregister(classes)