# 🖥️ VM-Deployer

A simple Python utility for deploying virtual machines from templates in a VMware vCenter environment using PyVmomi.

---

## 🚀 Features

- Interactive CLI for deploying a VM
- Choose template, datastore, VM name, IP address, and hostname
- Automates VM creation through vCenter API
- Stores vCenter credentials securely using the system keyring
- Perfect for homelab automation or small-scale virtualization tasks

---

## 🛠️ Requirements

- Python 3.6+
- A vCenter environment with accessible VM templates
- Python packages:
  - `pyvmomi`
  - `keyring`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🔑 Storing vCenter Credentials

Before running the script, store your vCenter credentials securely using `keyring`, either in bash or Python:

Bash
```bash
keyring set {vCenter IP} {vCenter username} {vCenter password}
```

Python
```python
import keyring

# Replace with your actual values
keyring.set_password("{vCenter IP}", "{vCenter username}", "{vCenter password}")
```

This stores the credentials in your OS’s native keyring (e.g., macOS Keychain, Windows Credential Manager, etc.).

---

## 🧑‍💻 Usage

Run the deployer script:

```bash
python3 deployer.py
```

You will be prompted to:

1. **Select a VM template**
2. **Choose a datastore**
3. **Enter a new VM name**
4. **Specify an IP address**
5. **Set a hostname**

Once complete, the VM will be cloned and powered on using the parameters provided.

---

## ⚠️ Notes

- Make sure your VM templates support customization (e.g., VMware Tools installed).
- Ensure your user account in vCenter has permissions to deploy VMs and access datastores.

---

## 👤 Author

**Alex Munoz**  
GitHub: [@AlexMunoz905](https://github.com/AlexMunoz905)

---
