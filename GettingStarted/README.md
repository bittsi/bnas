# Getting Started
## Setup
The lab topology is built with physical Cisco Switches (IOS, IOS-XE, NX-OS):

| Hostname			| HW-Type 				| OS-Type	| SW-Version  | 
| ----------------- | --------------------- | --------- | ----------- |   
| Lab_Access-23		| WS-C3560CG-8PC-S     	| IOS       | 12.2(55)EX2 |    
| Lab_Access-25     | WS-C3650-24PD        	| IOS-XE    | 03.03.03SE  |    
| Lab_Core-1        | WS-C4500X-16         	| IOS-XE    | 03.08.02.E  |    
| Pod_N5k-1         | Nexus5548 Chassis    	| NX-OS     | 7.3(1)N1(1) |    
| Pod_N5k-2         | Nexus5548 Chassis    	| NX-OS     | 7.3(1)N1(1) |
| Stag_Access-1     | WS-C2960X-24PD-L     	| IOS       | 15.2(2)E5   |

The equipment is from our staging environment. There are 3 different areas:
- Pod: Small DC infrastructure with 2 Nexus switches connected to the staging environment 
- Staging: Switches which are staged before shipping to the customer (currently just one, this will change frequently)
- Lab: Infrastructure to connect the staging devices

These areas are grouped within the hosts.ini file. Each group uses different credentials. The credentials and other group specific variables are stored in a vault.yml file inside the corresponding group_var directory.

## Playbook execution
### Executing raw commands
ansible all -i hosts.ini -m raw -a "show version" --ask-vault-pass
