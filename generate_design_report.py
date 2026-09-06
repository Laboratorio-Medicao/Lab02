from pathlib import Path

from experiment.config.design_report import export
from experiment.config.lab02_design import create_lab02_design

if __name__ == "__main__":
    design = create_lab02_design()
    export(design, Path("docs/experiment_design.md"))
