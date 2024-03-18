"""Local Ansible filters."""


class FilterModule(object):
    """Class to hold the filters."""

    def filters(self):
        """Method to expose the filters."""
        return {'get_environment_value': self.get_environment_value}

    def get_environment_value(self, input_data):
        """Get an environment specific value."""
        (environment_data, environment_name) = input_data
        if isinstance(environment_data, dict):
            if environment_name in environment_data:
                return environment_data[environment_name]
            if 'default' in environment_data:
                return environment_data['default']
        return environment_data
