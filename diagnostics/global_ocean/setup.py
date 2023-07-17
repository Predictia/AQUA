
from global_ocean import global_ocean

# Create an instance of the Ocean_circulationDiagnostic class
diagnostic = global_ocean(model='FESOM', exp='tco2559-ng5-cycle3', source='lra-r100-monthly')

# Run the diagnostics
diagnostic.run()