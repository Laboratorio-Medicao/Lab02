import argparse
import logging
from pathlib import Path

from shared.client import GitHubGraphQLClient
from shared.config import get_github_token
from kanban.exporter import CsvExporter
from kanban.fetcher import KanbanFetcher

logger = logging.getLogger(__name__)

DEFAULT_ORG = "Laboratorio-Medicao"
DEFAULT_PROJECT_NUMBER = 1
DEFAULT_LABEL_FILTER = "lab02"
SNAPSHOTS_DIR = Path(__file__).resolve().parent.parent / "data" / "kanban-snapshots"


def _parse_args():
    parser = argparse.ArgumentParser(description="Gera snapshot do Kanban GitHub Projects v2")
    parser.add_argument("--org", default=DEFAULT_ORG, help="organização GitHub")
    parser.add_argument("--project", type=int, default=DEFAULT_PROJECT_NUMBER, help="número do projeto")
    parser.add_argument("--label", default=DEFAULT_LABEL_FILTER, help="filtrar por label (padrão: lab02)")
    return parser.parse_args()


def run(org, project_number, label_filter=DEFAULT_LABEL_FILTER, output_dir=SNAPSHOTS_DIR):
    token = get_github_token()
    client = GitHubGraphQLClient(token=token)

    fetcher = KanbanFetcher(client, org=org, project_number=project_number, label_filter=label_filter)
    items = fetcher.fetch_all()

    exporter = CsvExporter(output_dir)
    output_path = exporter.export(items)

    logger.info("snapshot salvo: %s (%s itens)", output_path, len(items))
    return output_path


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = _parse_args()
    run(org=args.org, project_number=args.project, label_filter=args.label)


if __name__ == "__main__":
    main()
