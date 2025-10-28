"""Integration test for the complete graph"""

from chatuvisbox.graph import run_graph
import matplotlib.pyplot as plt

prompt = "generate 30 vectors over a 10 by 10 grid; plot uncertainty lobe"
# prompt = "Generate 100 ensemble curves and show me a curve boxplot"
# prompt = "Generate a 2D scalar field ensemble and show probabilistic marching squares visualization"

result = run_graph(prompt)

print(result)

input("Press Enter to continue...")
