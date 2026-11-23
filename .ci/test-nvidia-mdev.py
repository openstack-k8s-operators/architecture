#!/usr/bin/env python3
"""Check NVIDIA configuration rendering and installation decisions.

Requires PyYAML, kustomize and ansible-playbook. The Ansible tests execute only
set_fact/assert tasks with synthetic data, never installer or system tasks.
"""

import copy
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parent.parent
NODESET = Path("examples/va/nvidia-mdev/edpm/nodeset")
POST = Path("examples/va/nvidia-mdev/edpm-post-driver/deployment")


def build(path):
    output = subprocess.run(
        ["kustomize", "build", str(path)], check=True, capture_output=True, text=True
    ).stdout
    return list(yaml.safe_load_all(output))


def resource(documents, name):
    return next(item for item in documents if item["metadata"]["name"] == name)


class NvidiaMdevTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = build(ROOT / NODESET)
        cls.install = yaml.safe_load(
            resource(cls.documents, "install-nvidia")["spec"]["playbookContents"]
        )[0]

    def test_rpm_is_default(self):
        data = resource(self.documents, "nvidia-url")["data"]
        self.assertEqual("rpm", data["nvidia_mdev_driver_install_method"])
        self.assertEqual("false", data["nvidia_mdev_driver_accept_license"])
        self.assertTrue(all(isinstance(value, str) for value in data.values()))

    def test_embedded_playbooks_pass_syntax_check(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("install-nvidia", "validate-nvidia"):
                with self.subTest(service=name):
                    path = Path(directory) / (name + ".yml")
                    path.write_text(resource(self.documents, name)["spec"]["playbookContents"])
                    result = subprocess.run(
                        ["ansible-playbook", "--syntax-check", "-i", "localhost,", str(path)],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_run_configuration_is_rendered(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "architecture"
            shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = checkout / NODESET / "values.yaml"
            values = yaml.safe_load(path.read_text())
            requested = {
                "nvidia_mdev_driver_install_method": "run",
                "nvidia_mdev_driver_url": "https://example.com/host-driver.run",
                "nvidia_mdev_driver_checksum": "sha256:" + "a" * 64,
                "nvidia_mdev_driver_accept_license": "true",
                "nvidia_mdev_expected_types": '["nvidia-228", "nvidia-229"]',
            }
            values["data"]["nova"]["mdev"].update(requested)
            path.write_text(yaml.safe_dump(values))
            self.assertEqual(requested, resource(build(checkout / NODESET), "nvidia-url")["data"])

    def test_validation_follows_reboot(self):
        deployment = resource(build(ROOT / POST), "edpm-deployment-post-driver")
        self.assertEqual(
            ["reboot-os", "validate-nvidia", "compute-provider"],
            deployment["spec"]["servicesOverride"],
        )
        resource(self.documents, "validate-nvidia")

    def run_playbook(self, plays, expect_success=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.yml"
            path.write_text(yaml.safe_dump(plays))
            result = subprocess.run(
                ["ansible-playbook", "-i", "localhost,", "-c", "local", str(path)],
                capture_output=True, text=True,
            )
            if expect_success:
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            else:
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            return result

    def test_rebuild_decisions(self):
        run_block = next(task for task in self.install["tasks"]
                         if task["name"] == "Build and install the driver for the running kernel")
        decision = next(task for task in run_block["block"]
                        if task["name"] == "Decide whether the driver needs rebuilding")
        base = {
            "_nvidia_run_state": {"kernel": "kernel-a", "installer_sha256": "digest-a",
                                  "driver_version": "580.178.05"},
            "_nvidia_kernel": {"stdout": "kernel-a"},
            "_nvidia_run_file": {"stat": {"checksum": "digest-a"}},
            "_nvidia_run_modules": {"results": [
                {"rc": 0, "stdout": "580.178.05"},
                {"rc": 0, "stdout": "580.178.05"},
            ]},
        }
        cases = [("unchanged", copy.deepcopy(base), False)]
        for name in ("new kernel", "new installer", "missing module", "different module", "fresh host"):
            values = copy.deepcopy(base)
            if name == "new kernel":
                values["_nvidia_kernel"]["stdout"] = "kernel-b"
            elif name == "new installer":
                values["_nvidia_run_file"]["stat"]["checksum"] = "digest-b"
            elif name == "missing module":
                values["_nvidia_run_modules"]["results"][1] = {"rc": 1, "stdout": ""}
            elif name == "different module":
                values["_nvidia_run_modules"]["results"][1]["stdout"] = "580.126.08"
            else:
                values["_nvidia_run_state"] = {}
            cases.append((name, values, True))
        plays = []
        for name, values, expected in cases:
            plays.append({"name": name, "hosts": "localhost", "gather_facts": False,
                          "vars": values, "tasks": [decision, {
                              "ansible.builtin.assert": {"that": [
                                  "_nvidia_run_required == " + str(expected).lower()
                              ]}
                          }]})
        self.run_playbook(plays)

    def test_run_requires_license_acknowledgement(self):
        validation = next(task for task in self.install["tasks"]
                          if task["name"] == "Validate the installation method")
        result = self.run_playbook([{
            "hosts": "localhost", "gather_facts": False,
            "vars": {"nvidia_install_method": "run", "nvidia_accept_license": False},
            "tasks": [validation],
        }], expect_success=False)
        self.assertIn("explicitly acknowledge", result.stdout)

    def test_mixed_installations_are_rejected(self):
        guard = next(task for task in self.install["tasks"]
                     if task["name"] == "Prevent mixing installation methods")
        for method, packages, marker in (
            ("run", {"NVIDIA-vGPU-rhel": []}, False),
            ("rpm", {}, True),
        ):
            with self.subTest(method=method):
                result = self.run_playbook([{
                    "hosts": "localhost", "gather_facts": False,
                    "vars": {"nvidia_install_method": method,
                             "ansible_facts": {"packages": packages},
                             "_nvidia_run_marker": {"stat": {"exists": marker}}},
                    "tasks": [guard],
                }], expect_success=False)
                self.assertIn("uninstall the previous", result.stdout)

    def test_mdev_validation_follows_sysfs_links(self):
        validation = yaml.safe_load(
            resource(self.documents, "validate-nvidia")["spec"]["playbookContents"]
        )[0]
        discovery = copy.deepcopy(next(task for task in validation["tasks"]
                                       if task["name"] == "Discover the supported NVIDIA mediated device types"))
        assertion = next(task for task in validation["tasks"]
                         if task["name"] == "Require NVIDIA mediated device support")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bus = root / "mdev_bus"
            bus.mkdir()
            for name in ("nvidia-228", "nvidia-229"):
                (root / "device/mdev_supported_types" / name).mkdir(parents=True)
            (bus / "0000:04:00.0").symlink_to(root / "device", target_is_directory=True)
            discovery["ansible.builtin.find"]["paths"] = str(bus)
            self.run_playbook([{
                "hosts": "localhost", "gather_facts": False,
                "vars": {"nvidia_expected_types": ["nvidia-228", "nvidia-229"]},
                "tasks": [discovery, assertion],
            }])

    def test_mdev_validation_rejects_missing_profiles(self):
        validation = yaml.safe_load(
            resource(self.documents, "validate-nvidia")["spec"]["playbookContents"]
        )[0]
        assertion = next(task for task in validation["tasks"]
                         if task["name"] == "Require NVIDIA mediated device support")
        for expected, discovered in (([], []), (["nvidia-229"], ["nvidia-228"])):
            with self.subTest(expected=expected):
                result = self.run_playbook([{
                    "hosts": "localhost", "gather_facts": False,
                    "vars": {"nvidia_expected_types": expected,
                             "_nvidia_mdev_types": {"matched": len(discovered), "files": [
                                 {"path": "/mdev_supported_types/" + name} for name in discovered
                             ]}},
                    "tasks": [assertion],
                }], expect_success=False)
                self.assertIn("profiles are missing", result.stdout)


if __name__ == "__main__":
    unittest.main()
