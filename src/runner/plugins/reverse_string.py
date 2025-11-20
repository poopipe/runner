from runner.plugin_libs.types import PluginResult

def plugin_main(s:str)->PluginResult:
    l = "".join( list(s)[::-1] )
    return PluginResult(__name__, {"_": l}) 

