import os
import pytest

def check_directory_for_forbidden_import(directory_path: str, forbidden_string: str):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert f"import {forbidden_string}" not in content, \
                        f"Architecture violation: '{forbidden_string}' found in {file_path}"
                    assert f"from {forbidden_string}" not in content, \
                        f"Architecture violation: '{forbidden_string}' found in {file_path}"

def test_domain_is_pure_from_sqlalchemy():
    check_directory_for_forbidden_import("domain", "sqlalchemy")

def test_application_is_pure_from_sqlalchemy():
    check_directory_for_forbidden_import("application", "sqlalchemy")