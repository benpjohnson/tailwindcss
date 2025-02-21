import os
import os.path as path
import shutil
import subprocess

from pelican import signals

from .utils import commands, installs, utils

BASE_DIR = os.path.dirname(__file__)


def initialize(po):
    SETTINGS = po.settings
    TAILWIND_SETTINGS = SETTINGS.get("TAILWIND", None)
    THEME_PATH = path.abspath(path.join(po.path, ".."))

    node_modules_path = os.path.join(BASE_DIR, "node_modules/")

    # Copy the tailwind.config.js file in order
    # to be able to use Tailwind plugins
    twconfig_file_path = os.path.join(THEME_PATH, "tailwind.config.js")
    shutil.copyfile(twconfig_file_path, os.path.join(BASE_DIR, "tailwind.config.js"))

    if os.path.isdir(node_modules_path):
        j_version = subprocess.check_output(
            "npm -j ls tailwindcss",
            cwd=BASE_DIR,
            shell=True,
        ).decode("utf-8")

        installed_tailwind_version = utils.get_npm_package_version(j_version=j_version)

        print(
            f"{utils.LOG_PREFIX} The version is right (v{installed_tailwind_version})"
        )

        if TAILWIND_SETTINGS:
            print(f"{utils.LOG_PREFIX} Settings were found")

            installs.another_tailwind(
                settings=TAILWIND_SETTINGS,
                installed_tailwind_version=installed_tailwind_version,
            )

            installs.plugins(settings=TAILWIND_SETTINGS)

        else:
            print(f"{utils.LOG_PREFIX} No settings were found")
    else:
        print("{utils.LOG_PREFIX} Initialization required, first start")
        commands.run_in_plugin("npm install")
        if TAILWIND_SETTINGS:
            print(f"{utils.LOG_PREFIX} Settings were found")
            installs.tailwind(settings=TAILWIND_SETTINGS)
            installs.plugins(settings=TAILWIND_SETTINGS)


def generate_css(po):
    SETTINGS = po.settings
    TAILWIND_OUTPUT = SETTINGS.get("OUTPUT_PATH", None)
    TAILWIND_CONFIG_PATH = SETTINGS.get("TAILWIND_CONFIG_PATH", os.path.join(BASE_DIR, "tailwind.config.js"))

    THEME_PATH = path.abspath(path.join(po.path, ".."))

    input_file_path = os.path.join(THEME_PATH, "input.css")
    output_file_path = os.path.join(THEME_PATH, f"{TAILWIND_OUTPUT}/output.css")

    input_output = f"-i {input_file_path} -o {output_file_path}"
    print(f"{utils.LOG_PREFIX} Build css ({output_file_path})")

    subprocess.run(
        f"npx tailwindcss@3 -c {TAILWIND_CONFIG_PATH} {input_output}",
    )


def register():
    signals.initialized.connect(initialize)
    signals.finalized.connect(generate_css)
