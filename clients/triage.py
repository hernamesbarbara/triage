#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Union, List
from functools import wraps
from collections import Counter, defaultdict

class SkipError(Exception):
    pass

def _reset_data_before_action(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.data_ = []
        return func(self, *args, **kwargs)
    return wrapper

def _update_data_after_action(func):
    @wraps(func)
    def wrapper(self, source, target, *args, **kwargs):
        try:
            result = func(self, source, target, *args, **kwargs)
            self._update_data(source, target, 'success')
            return result
        except SkipError:
            self._update_data(source, target, 'skipped')
        except Exception as e:
            self._update_data(source, target, 'error', str(e))
            raise e
    return wrapper

class Triage:
    config = {
        'triage_home': Path(os.path.expanduser(os.environ.get('TRIAGE_HOME', '~/.triage/')))
    }
    name = 'base'
    
    def __init__(self):
        self.triage_path = self.config['triage_home'] / self.name
        self.init_local_storage()
        self.data_ = []

    def _validate_target_within_home(self, target: Path):
        """
        Validate that the target directory is within `triage_home`.
        """
        triage_home = self.config['triage_home']
        if not target.resolve().as_posix().startswith(triage_home.resolve().as_posix()):
            raise ValueError("The target directory must be within `triage_home`.")
    
    @classmethod
    def configure(cls, **kwargs):
        """Configure triage settings."""
        cls.config.update(kwargs)
    
    def init_local_storage(self):
        self.triage_path.mkdir(parents=True, exist_ok=True)

    @_reset_data_before_action
    def triage_base(self, *args, **kwargs):
        pass

    def _update_data(self, source, target, status, error=None):
        new_data = {
            'source': source,
            'target': target,
            'status': status,
            'error': error
        }
        self.data_.append(new_data)
        return new_data

    @property
    def home(self) -> Path:
        return self.config['triage_home']
    
    @_update_data_after_action
    def copy(self, source: Path, target: Path, overwrites: str='raise'):
        self._validate_target_within_home(target)
        
        # Check if the target is a directory
        if not target.is_dir():
            raise ValueError("The target must be a directory.")
        
        if (target / source.name).exists():
            if overwrites == 'skip':
                raise SkipError(f"File {source.name} skipped.")
            else:
                raise FileExistsError(f"File {source.name} already exists.")
        
        # Perform the copy operation, preserving metadata
        return shutil.copy2(source, target)

    @_update_data_after_action
    def move(self, source: Path, target: Path, overwrites: str='raise'):
        """
        Move a file from the source to the target directory.
        """
        self._validate_target_within_home(target)

        # Check if the target is a directory
        if not target.is_dir():
            raise ValueError("The target must be a directory.")
        
        destination = target / source.name

        # Check if the file already exists in the target directory
        if destination.exists():
            if overwrites == 'overwrite':
                destination.unlink()  # Remove the existing file
            elif overwrites == 'skip':
                raise SkipError(f"File {source.name} skipped.")
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
    
    def summary(self):
        if not self.data_:
            return "No triage actions have been performed yet."
        
        num_files = len(self.data_)
        num_unique_files = len(set(entry['source'] for entry in self.data_))
        status_counter = Counter(entry['status'] for entry in self.data_)
        
        num_errors = status_counter.get('error', 0)
        num_skips = status_counter.get('skipped', 0)
        num_success = status_counter.get('success', 0)
        
        # Grouping by target and status
        target_status_group = defaultdict(lambda: defaultdict(int))
        for entry in self.data_:
            target_status_group[entry['target']][entry['status']] += 1
        
        # Formatting the grouped data
        grouped_data_str = "\n".join(
            f"- Target: {target}, Status Counts: {dict(counts)}"
            for target, counts in target_status_group.items()
        )
        
        summary_str = (
            f"Summary of triage actions:\n"
            f"- Number of files processed: {num_files}\n"
            f"- Number of unique files processed: {num_unique_files}\n"
            f"- Number of errors: {num_errors}\n"
            f"- Number of skips: {num_skips}\n"
            f"- Number of successful actions: {num_success}\n"
            f"\nGrouped by target and status:\n{grouped_data_str}\n"
        )
        
        return summary_str
