import opendssdirect as dss


dss_file = r"C:\Users\hani049\OneDrive - PNNL\Documents\OpenDSS\scripts\13Bus\IEEE13Nodeckt.dss"

# using redirect command
dss.run_command(f"Redirect [{dss_file}]")
# using solve command
dss.run_command(f"Solve")
dss.run_command("Show voltages LN nodes")
