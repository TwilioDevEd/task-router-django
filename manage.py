#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    test_settings = 'twilio_sample_project.settings.test'
    default_settings = 'twilio_sample_project.settings.local'
    settings = test_settings if 'test' in sys.argv else default_settings

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
