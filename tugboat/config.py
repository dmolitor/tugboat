import json
import os
import prompt_toolkit as pt
import re
from tugboat.utils import string_to_none
from tugboat.validators import (
    add_remove_edit_validator,
    yes_no_validator,
    software_validator,
    software_version_validator
)
import yaml

class TugboatConfig:
    """Tugboat configuration settings
    
    This class provides methods for importing a configuration file or creating
    one in lieu of an existing file.
    
    Parameters
    ----------
    path : str, optional
        The filepath to a local configuration file (optional).
    
    Attributes
    ----------
    config : dict
        Tugboat configuration file in dictionary format.
    requirements : list
        A list of all required software.
    
    Methods
    -------
    generate_config()
        Generate a configuration file from user input.
    """
    def __init__(self):
        self.config = dict()
        self.requirements = list()
    
    def _import_config(self, path: str):
        with open(path, "r") as yaml_file:
            gangway_config = yaml.load(yaml_file, yaml.Loader)
        return gangway_config
    
    def _input_software(self, software=None):
        if software == None:
            sw = [
                "Julia", "Jupyter", "Pandoc", "Python", "Quarto", "RStudio", "R"
                #, "RMarkdown", "Shiny", "Cuda", "Stata"
            ]
        sw_completer = pt.completion.WordCompleter(
            words=sw,
            ignore_case=True,
            match_middle=True
        )
        text = pt.prompt(
            "Tell us what software you need! (press Esc + Enter/Return to submit):\n",
            completer=sw_completer,
            validator=software_validator,
            validate_while_typing=True,
            multiline=True
        )
        sw = text.split()
        sw = list(set(sw))
        return sw
    
    def _input_software_version(self, software: list, edit: bool = False):
        if not edit:
            pt.print_formatted_text(
                pt.HTML(
                    "ℹ️  For each software, please enter the version you'd like to use"
                    + ".\n   <u>(If you're unsure or it doesn't matter, keep this empty"
                    + " and hit Enter/Return)</u>"
                )
            )
        sw = dict()
        for s in software:
            sw_prompt = f"{s} version: "
            version = pt.prompt(
                sw_prompt,
                validator=software_version_validator,
                validate_while_typing=True
            )
            version = string_to_none(version)
            sw[s] = {"version": version}
        return sw
    
    def _update_config(self):
        sw = self.requirements
        sw_completer = pt.completion.WordCompleter(
            words=sw,
            ignore_case=True,
            match_middle=True
        )
        are_completer = pt.completion.WordCompleter(
            words=["Add", "Remove", "Edit"],
            ignore_case=True,
            match_middle=True
        )
        are = pt.prompt(
            "ℹ️  Would you like to add, remove, or edit the version of a software?\n(Add/Remove/Edit): ",
            completer=are_completer,
            validator=add_remove_edit_validator,
            validate_while_typing=True
        )
        if are.lower() == "remove":
            sw_to_remove = pt.prompt(
               "   What software would you like to remove: ",
                completer=sw_completer,
                validator=software_validator,
                validate_while_typing=True,
            )
            sw_to_remove = string_to_none(sw_to_remove)
            if sw_to_remove:
                self.config.pop(sw_to_remove)
                self.requirements.remove(sw_to_remove)
        elif are.lower() == "edit":
            sw_to_edit = pt.prompt(
               "   What software would you like to edit the version for: ",
                completer=sw_completer,
                validator=software_validator,
                validate_while_typing=True,
            )
            sw_to_edit = string_to_none(sw_to_edit)
            if sw_to_edit:
                sw_updated = self._input_software_version([sw_to_edit], edit=True)
                self.config[sw_to_edit] = sw_updated[sw_to_edit]
        else:
            requires = self._input_software()
            config = self._input_software_version(requires)
            [self.requirements.append(s) for s in requires]
            self.requirements = list(set(self.requirements))
            for k,v in config.items():
                self.config[k] = v
        yn = pt.prompt(
            "   Would you like to make further edits? [Y/n]: ",
            validator=yes_no_validator,
            validate_while_typing=True
        )
        if yn.lower() in ["y", "yes"]:
            self._update_config()
        return self
    
    def _write_config(self):
        with open("tugboat.yml", "w+") as config_fp:
            yaml.dump(self.config, config_fp, default_flow_style=False)
        print("✅ Configuration file written to ./tugboat.yml")
        return None
    
    def generate_config(self, path: str = "./tugboat.yml"):
        """Generate a Tugboat configuration
        
        This will either import an existing file or create one from user input.
        
        Parameters
        ----------
        path : str, default="./tugboat.yml"
            The path to an existing configuration file. The default value will
            look for a file at `./tugboat.yml` and, if it doesn't exist, the
            user will be prompted to create one.
        
        Returns
        -------
        TugboatConfig
            A configuration class containing software requirements.
        """
        if os.path.isfile(path):
            pt.print_formatted_text("Importing Tugboat configuration file ...")
            config = self._import_config(path=path)
            requires = list(set(config.keys()))
            self.config = config
            self.requirements = requires
            yn = pt.prompt(
                "Would you like to edit the existing configuration file? [Y/n]: ",
                validator=yes_no_validator,
                validate_while_typing=True
            )
            if yn.lower() in ["y", "yes"]:
                self._update_config()
                self._write_config()
        else:
            yn = pt.prompt(
                "❌ No Tugboat configuration file was found.\n   Would you like to create one? [Y/n]: ",
                validator=yes_no_validator,
                validate_while_typing=True
            )
            if yn.lower() in ["n", "no"]:
                print("   Please create a configuration file and put it at ./tugboat.yml")
                return self
            requires = self._input_software()
            config = self._input_software_version(requires)
            self.config = config
            self.requirements = requires
            pt.print_formatted_text(
                pt.HTML(
                    "Would you like to save your configuration file?\n❗<u>(This is "
                    + "highly recommended otherwise all changes will be lost)❗</u>"
                )
            )
            write_config = pt.prompt(
                "[Y/n]: ",
                validator=yes_no_validator,
                validate_while_typing=True
            )
            if write_config.lower() in ["y", "yes"]:
                self._write_config()
            else:
                print("Your configuration settings will not be saved")
        return self

if __name__ == "__main__":
    tst = TugboatConfig()
    tst.generate_config()
    print(f"Config: {tst.config}\nRequirements: {tst.requirements}")
