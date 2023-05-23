import intake  # Import this first to avoid circular imports during discovery.
# from intake.container import register_container

# Test if FDB5 binary library is available
try:
    from .intake_gsv import GSVSource
except RuntimeError:
    print("FDB5 binary library not present on system, disabling FDB support.")
    pass

try:
    intake.registry.drivers.register_driver('gsv', GSVSource)
except ValueError:
    pass

#register_container('gsv', GSVSource)