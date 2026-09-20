import csv
import os

class CSVDatabase:

    def __init__(self, folder="database"):
        self.folder = folder

    def _path(self, filename):
        return os.path.join(self.folder, filename)

    def append(self, filename, data: dict):

        path = self._path(filename)

        file_exists = os.path.exists(path)

        with open(path, "a", newline="", encoding="utf-8") as file:

            writer = csv.DictWriter(
                file,
                fieldnames=data.keys()
            )

            if not file_exists or os.path.getsize(path) == 0:
                writer.writeheader()

            writer.writerow(data)

    def read_last(self, filename):

        path = self._path(filename)

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as file:

            rows = list(csv.DictReader(file))

            if len(rows) == 0:
                return None

            return rows[-1]

    def read_all(self, filename):

        path = self._path(filename)

        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as file:

            return list(csv.DictReader(file))