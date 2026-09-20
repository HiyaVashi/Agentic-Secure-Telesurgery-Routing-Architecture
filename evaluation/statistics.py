import pandas as pd
import numpy as np

from scipy.stats import ttest_rel
from scipy.stats import t


class Statistics:

    def __init__(self, filename="results/experiment_results.csv"):
        self.filename = filename
        self.df = pd.read_csv(filename)

    def get_model_results(self, model_name):

        return self.df[self.df["Model"] == model_name]

    def mean(self, data):

        return np.mean(data)

    def std(self, data):

        return np.std(data, ddof=1)

    def confidence_interval(self, data, confidence=0.95):

        n = len(data)

        mean = np.mean(data)

        std = np.std(data, ddof=1)

        margin = t.ppf(
            (1 + confidence) / 2,
            n - 1
        ) * (std / np.sqrt(n))

        return (
            mean - margin,
            mean + margin
        )

    def cohens_d(self, group1, group2):

        difference = np.array(group1) - np.array(group2)

        return np.mean(difference) / np.std(
            difference,
            ddof=1
        )

    def paired_ttest(self, group1, group2):

        statistic, pvalue = ttest_rel(
            group1,
            group2
        )

        return statistic, pvalue

    def compare_models(self):

        groq = self.get_model_results("Groq")

        ollama = self.get_model_results("Ollama")

        groq_scores = groq["Weighted_Distance"]

        ollama_scores = ollama["Weighted_Distance"]

        t_statistic, p_value = self.paired_ttest(
            groq_scores,
            ollama_scores
        )

        effect = self.cohens_d(
            groq_scores,
            ollama_scores
        )

        groq_ci = self.confidence_interval(
            groq_scores
        )

        ollama_ci = self.confidence_interval(
            ollama_scores
        )

        return {

            "Groq": {

                "Mean": self.mean(groq_scores),

                "Std": self.std(groq_scores),

                "Confidence Interval": groq_ci

            },

            "Ollama": {

                "Mean": self.mean(ollama_scores),

                "Std": self.std(ollama_scores),

                "Confidence Interval": ollama_ci

            },

            "Paired t-test": {

                "t statistic": t_statistic,

                "p value": p_value

            },

            "Cohen's d": effect

        }


if __name__ == "__main__":

    stats = Statistics()

    results = stats.compare_models()

    print("\n========== EXPERIMENT SUMMARY ==========\n")

    for key, value in results.items():

        print(key)

        print(value)

        print()