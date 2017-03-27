# Summary Reports

## About
Read data to create a simple HW/SW-Report for NX-OS, IOS and IOS-XE devices

By default the data is directly gathered from each device and the report is written into a textfile. Reports are always genrated with templates.

To determine if it's a NX-OS, an IOS or an IOS-XE device group_vars are being used. The variable is named os.

Extra variables can be used to overwrite the default settings:
   input   - from where the data is read (from device directly or from vars)
   format  - template format (e.g. html)


The current date and time is determined with a task and is written into facts. This fact is later used in the template which generates the html report.


## Playbook execution
### Read from devices and generate report as text-file:
ansible-playbook hw_sw.yml --ask-vault-pass

### Read from devices and generated report as html-file:
ansible-playbook hw_sw.yml  --extra-vars="format=html" --ask-vault-pass

### Read from var-files (which previously created with read from devices) and generate report as text-file:
ansible-playbook hw_sw.yml --ask-vault-pass --extra-vars="input=vars"

### Read from var-files (which previously created with read from devices) and generate report as html-file :
ansible-playbook hw_sw.yml --ask-vault-pass --extra-vars="format=html input=vars"