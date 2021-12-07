import opendssdirect as dss


dss_file = r"C:\Users\kini136\OneDrive - PNNL\Desktop\Enhanced_Controls_Dashboard\ckts\opendss-ckts\IEEE13\MasterIEEE13.dss"

# using redirect command
dss.run_command(f"Redirect [{dss_file}]")
# using solve command
dss.run_command(f"Solve")
dss.run_command("Show voltages LN nodes")
