"""Gera docs/experiment_design.md a partir de experiment/config/lab02_design.py.

Os trechos manuais do documento ficam entre marcadores
`<!-- manual:start <nome> -->` e `<!-- manual:end <nome> -->` e são preservados.
Se a regeneração fosse remover qualquer outra linha do arquivo atual, o script
para sem gravar nada; use `--force` apenas se essa perda for intencional.
"""

import argparse
import sys
from pathlib import Path

from experiment.config.design_report import ManualContentLossError, export
from experiment.config.lab02_design import create_lab02_design

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force",
        action="store_true",
        help="grava mesmo que linhas do arquivo atual sejam removidas",
    )
    args = parser.parse_args()
    try:
        export(create_lab02_design(), Path("docs/experiment_design.md"), force=args.force)
    except ManualContentLossError as error:
        sys.exit(str(error))
