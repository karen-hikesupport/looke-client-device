import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect('remote_host', username='user', password='pass')
scp = ssh.open_sftp()
scp.put('local_file', 'remote_file')

# Close the SCP client
scp.close()

# Close the SSH client
ssh.close()