"""Integration test for the complete graph"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from graph import run_graph
import matplotlib.pyplot as plt

prompt = "Generate 100 ensemble curves and show me a curve boxplot"
# prompt = "Generate a 2D scalar field ensemble and show probabilistic marching squares visualization"

result = run_graph(prompt)

print(result)

input("Press Enter to continue...")
