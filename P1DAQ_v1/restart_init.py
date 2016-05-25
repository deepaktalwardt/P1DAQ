# Sets the restart_count to 0 at every reboot

# file_name = "C:/Users/Deepak/Desktop/New folder/restart_counts.txt"
restart_file_name = "/mnt/Clarity/restart_counts.txt"
restart_counter = 0

def reset_counter():
	with open(file_name, "w") as file_to_write:
		file_to_write.write(str(restart_counter))

reset_counter()