from .plugin import SamplePlugin

def on_load():
    plugin = SamplePlugin()
    plugin.on_load()

def on_enable():
    plugin = SamplePlugin()
    plugin.on_enable()

def on_disable():
    plugin = SamplePlugin()
    plugin.on_disable()

def on_unload():
    plugin = SamplePlugin()
    plugin.on_unload()
