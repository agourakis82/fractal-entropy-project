import itertools, pathlib, datetime, subprocess, sys

alphas = [0.1,0.2,0.3,0.4,0.5,0.6,0.8,1.0,1.5,2.0]
betas  = [0.005,0.01,0.015,0.02,0.025,0.03,0.04,0.05,0.06,0.08]

today = datetime.date.today().strftime("%Y%m%d")
csvfile = pathlib.Path("../paper_data") / f"run_{today}.csv"
csvfile.parent.mkdir(exist_ok=True)

for a,b in itertools.product(alphas, betas):
    cmd = [
        sys.executable, "mc_sim.py",
        "--N", "10000", "--steps", "10000",
        "--alpha", str(a), "--beta", str(b),
        "--seed", "0", "--outcsv", str(csvfile)
    ]
    subprocess.run(cmd, cwd=pathlib.Path(__file__).parent, check=True)
print("Grid complete:", csvfile)