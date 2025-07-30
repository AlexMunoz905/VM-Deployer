# vCenter Template Deployer
# Alex Munoz <alex@napend.com>
# 07/29/2025
#
# Deploys vCenter template with user specifying which template, datastore, VM name, IP, and hostname.

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import time
import keyring

# Credentials for connecting to vCenter
vcenter_host = "vcenter.napend.com"
vcenter_user = "automation@napend.com"
vcenter_password = keyring.get_password(vcenter_host,vcenter_user)
vcenter_port = 443

# Disable SSL verification
context = ssl._create_unverified_context()

# Connect to vCenter
si = SmartConnect(
    host=vcenter_host,
    user=vcenter_user,
    pwd=vcenter_password,
    sslContext=context
)
content = si.RetrieveContent()

# Establishes all the objects in the vCenter datacenter
def get_all_objs(content, vimtype):
    obj_list = []
    container = content.viewManager.CreateContainerView(content.rootFolder, [vimtype], True)
    for obj in container.view:
        obj_list.append(obj)
    return obj_list

# Has the user pick which template they want to clone
def choose_from_list(title, objects, attr="name"):
    print(f"\n{title}")
    for i, obj in enumerate(objects):
        print(f"{i}: {getattr(obj, attr)}")
    choice = int(input("Select number: "))
    return objects[choice]

# List all templates
templates = [vm for vm in get_all_objs(content, vim.VirtualMachine) if vm.config and vm.config.template]
if not templates:
    print("No templates found.")
    exit()
template = choose_from_list("Available Templates:", templates)

# Step 2: List all datastores
datastores = get_all_objs(content, vim.Datastore)
if not datastores:
    print("No datastores found.")
    exit()
datastore = choose_from_list("Available Datastores:", datastores)

# Gets the folders, and sets it to the "VM" folder, which is the only folder I use on vCenter
def get_obj_by_moid(content, vimtype, moid):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vimtype], True)
    for obj in container.view:
        if obj._moId == moid:
            return obj
    return None
dest_folder = get_obj_by_moid(content, vim.Folder, "group-v4")

# Ask for amount of RAM in GB and converts it to MB, defaults to 2GB (2048mb)
new_vm_ram = input("Enter RAM in GB [Default: 2]: ").strip()
new_vm_ram = int(new_vm_ram) * 1024 if new_vm_ram else 2048

# Ask for new VM name
new_vm_name = input("Enter name for new VM: ").strip()

# Ask for VM hostname & IP.
# Does not ask for gateway, DNS, or search domain, those are pre-specefied by me in the custom_spec
new_vm_ip = input("IP for new VM: ").strip()
new_vm_hostname = input("Hostname for new VM: ").strip()

# Custom spec for vCenter. Allows you to customize the VM during it's cloning.
# In this case, it assigns IP, subnet, gateway, DNS, hostname, and search domain.
def create_custom_spec(ip, subnet, gateway, dns_servers, hostname, domain):
    adapter_mapping = vim.vm.customization.AdapterMapping()
    adapter_mapping.adapter = vim.vm.customization.IPSettings(
        ip=vim.vm.customization.FixedIp(ipAddress=ip),
        subnetMask=subnet,
        gateway=gateway,
        dnsDomain=domain
    )

    global_ip = vim.vm.customization.GlobalIPSettings()
    global_ip.dnsServerList = dns_servers

    ident = vim.vm.customization.LinuxPrep()
    ident.domain = domain
    ident.hostName = vim.vm.customization.FixedName(name=hostname)

    custom_spec = vim.vm.customization.Specification()
    custom_spec.nicSettingMap = [adapter_mapping]
    custom_spec.globalIPSettings = global_ip
    custom_spec.identity = ident

    return custom_spec

#Select cluster and resource pool (use the one from the template’s host)
host = template.runtime.host
cluster = host.parent
resource_pool = cluster.resourcePool
datacenter = cluster.parent

# Clone the template
relo_spec = vim.vm.RelocateSpec()
relo_spec.datastore = datastore
relo_spec.pool = resource_pool
config_spec = vim.vm.ConfigSpec()
config_spec.memoryMB = new_vm_ram

custom_spec = create_custom_spec(
    ip=new_vm_ip,
    subnet="255.255.255.0",
    gateway=["192.168.50.1"],
    dns_servers=["192.168.50.17", "192.168.50.25"],
    hostname=new_vm_hostname,
    domain="napend.com"
)

clone_spec = vim.vm.CloneSpec()
clone_spec.location = relo_spec
clone_spec.config = config_spec
clone_spec.powerOn = True
clone_spec.template = False
clone_spec.customization = custom_spec

print(f"\nCloning '{template.name}' to '{new_vm_name}' in datastore '{datastore.name}' with IP '{new_vm_ip}' with hostname '{new_vm_hostname}'...")

task = template.Clone(
    folder=dest_folder,
    name=new_vm_name,
    spec=clone_spec
)

# Wait for the task
while task.info.state == vim.TaskInfo.State.running:
    print("Cloning in progress...")
    time.sleep(5)

if task.info.state == vim.TaskInfo.State.success:
    print("✅ VM successfully cloned and powered on.")
    time.sleep(3)
else:
    print("❌ Clone failed.")
    if task.info.error:
        print(f"Reason: {task.info.error.msg}")
    else:
        print("No error details available. Task may have been cancelled or invalid.")

# Disconnect from vCenter
Disconnect(si)