#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Union, List

class Triage:
    # Class-level attribute for configuration
    config = {
        'triage_home': Path(os.path.expanduser(os.environ.get('TRIAGE_HOME', '~/.triage/')))
    }
    name = 'base'

    @classmethod
    def _validate_target_within_home(cls, target: Path):
        """
        Validate that the target directory is within `triage_home`.
        """
        triage_home = cls.config['triage_home']
        if not target.resolve().as_posix().startswith(triage_home.resolve().as_posix()):
            raise ValueError("The target directory must be within `triage_home`.")
    
    
    @classmethod
    def configure(cls, **kwargs):
        """Configure triage settings."""
        cls.config.update(kwargs)
    
    def __init__(self):
        self.triage_path = self.config['triage_home'] / self.name
        self.init_local_storage()

    def init_local_storage(self):
        self.triage_path.mkdir(parents=True, exist_ok=True)
        
    def local_storage_ready(self):
        return self.triage_path.is_dir()

    @property
    def home(self) -> Path:
        return self.config['triage_home']
    
    @classmethod
    def copy(cls, source: Path, target: Path, overwrite: bool = False) -> str:
        cls._validate_target_within_home(target)
        
        # Check if the target is a directory
        if not target.is_dir():
            raise ValueError("The target must be a directory.")
        
        if (target / source.name).exists() and not overwrite:
            raise FileExistsError(f"File {source.name} already exists.")
        
        # Perform the copy operation, preserving metadata
        return shutil.copy2(source, target)

    @classmethod
    def move(cls, source: Path, target: Path, overwrite=False):
        """
        Move a file from the source to the target directory.
        """
        triage_home = cls.config['triage_home']

        # Check if the target directory is within `triage_home`
        cls._validate_target_within_home(target)

        # Check if the target is a directory
        if not target.is_dir():
            raise ValueError("The target must be a directory.")
        
        destination = target / source.name

        # Check if the file already exists in the target directory
        if destination.exists():
            if overwrite:
                destination.unlink()  # Remove the existing file
            else:
                raise FileExistsError(f"The file {source.name} already exists in the target directory.")

        # Perform the move operation
        return shutil.move(str(source), str(destination))

    def list_files(self, folder: Path = None) -> list:
        """
        List files in a specified folder within the triage directory.
        """
        if folder is None:
            folder = self.triage_path
        
        self._validate_target_within_home(folder)
        
        return list(folder.iterdir())
