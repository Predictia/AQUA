diagnostic_config = {
    'tropical_rainfall': [
        {
            'config_file': 'config-tropical-rainfall.yml',
            'source_path': 'diagnostics/tropical_rainfall/tropical_rainfall',
            'target_path': 'diagnostics/tropical_rainfall/config'
        },
        {
            'config_file': 'cli_config_trop_rainfall.yml',
            'source_path': 'diagnostics/tropical_rainfall/cli',
            'target_path': 'diagnostics/tropical_rainfall/cli'
        }
    ],
    'atmglobalmean': [
        {
            'config_file': 'atm_mean_bias_config.yaml',
            'source_path': 'diagnostics/atmglobalmean/cli/config',
            'target_path': 'diagnostics/atmglobalmean/cli'
        }
    ],
    'ecmean': [
        {
            'config_file': 'ecmean_config_destine-v1-levante.yml',
            'source_path': 'diagnostics/ecmean/config',
            'target_path': 'diagnostics/ecmean/config'
        },
        {
            'config_file': 'ecmean_config_destine-v1.yml',
            'source_path': 'diagnostics/ecmean/config',
            'target_path': 'diagnostics/ecmean/config'
        },
        {
            'config_file': 'interface_AQUA_destine-v1.yml',
            'source_path': 'diagnostics/ecmean/config',
            'target_path': 'diagnostics/ecmean/config'
        },
        {
            'config_file': 'config_ecmean_cli.yaml',
            'source_path': 'diagnostics/ecmean/cli',
            'target_path': 'diagnostics/ecmean/cli'
        }
    ],
    # Add other diagnostic configurations here
}