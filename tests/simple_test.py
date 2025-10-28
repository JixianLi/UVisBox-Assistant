"""Integration test for the complete graph"""

from chatuvisbox.graph import run_graph
import matplotlib.pyplot as plt

# prompt = "generate 30 vectors over a 10 by 10 grid; plot uncertainty lobe"
# prompt = "Generate 100 ensemble curves and show me a curve boxplot"
# prompt = "Generate 30 instances of 100x100 scalar field ensemble and show probabilistic marching squares visualization, at isovalue 0.75, using plasma colormap"
# prompt = "Generate 30 instances of 100x100 scalar field ensemble and show contour boxplot visualization, at isovalue 0.75"
prompt = "generate 30 instances of 10x10 vector field ensemble, with initial direction 0.0 and magnitude 1.0, direction variation factor 0.2 and magnitude variation factor 0.2; plot uncertainty lobes with percentiles 40 and 80, scale 0.3"

result = run_graph(prompt)

print(result)

input("Press Enter to continue...")
