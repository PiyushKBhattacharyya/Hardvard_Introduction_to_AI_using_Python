import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having a gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},

    # Probability of trait given two copies of gene
    "trait": {2: {True: 0.65, False: 0.35},
              1: {True: 0.56, False: 0.44},
              0: {True: 0.01, False: 0.99}},

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")

    # Load data from CSV file
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {2: 0, 1: 0, 0: 0},
            "trait": {True: 0, False: 0}
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1

    for person in people:
        gene_number = 1 if person in one_gene else 2 if person in two_genes else 0
        trait = True if person in have_trait else False

        gene_numb_prop = PROBS['gene'][gene_number]
        trait_prop = PROBS['trait'][gene_number][trait]

        if people[person]['mother'] is None:
            # no parents, use probability distribution
            probability *= gene_numb_prop * trait_prop
        else:
            # info about parents is available
            mother = people[person]['mother']
            father = people[person]['father']
            percentages = {}

            for ppl in [mother, father]:
                number = 1 if ppl in one_gene else 2 if ppl in two_genes else 0
                perc = 0 + \
                    PROBS['mutation'] if number == 0 else 0.5 if number == 1 else 1 - PROBS['mutation']
                percentages[ppl] = perc

            if gene_number == 0:
                # 0, none of parents gave gene
                probability *= (1 - percentages[mother]) * (1 - percentages[father])
            elif gene_number == 1:
                # 1, one of parents gave gene
                probability *= (1 - percentages[mother]) * percentages[father] + \
                    percentages[mother] * (1 - percentages[father])
            else:
                # 2, both of parents gave gene
                probability *= percentages[mother] * percentages[father]

            probability *= trait_prop

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        gene_number = 1 if person in one_gene else 2 if person in two_genes else 0
        probabilities[person]["gene"][gene_number] += p
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    normalized = probabilities.copy()
    for person in probabilities:
        for typ in ['gene', 'trait']:
            summed = sum(probabilities[person][typ].values())
            for category in probabilities[person][typ]:
                val = probabilities[person][typ][category]
                normalized_val = val / summed
                normalized[person][typ][category] = normalized_val
    return normalized


def test_joint_probability_simple():
    # Define a simple family with no genes or traits
    simple_family_data = {
        "person1": {"name": "person1", "mother": None, "father": None, "trait": None},
        "person2": {"name": "person2", "mother": None, "father": None, "trait": None}
    }

    # Test case where no one has a gene or trait
    one_gene = set()
    two_genes = set()
    have_trait = set()
    probability = joint_probability(simple_family_data, one_gene, two_genes, have_trait)

    # The joint probability should be 1 since no gene or trait is present
    assert probability == 1, "Joint probability is incorrect for simple family with no genes or traits"

    print("Test passed: Joint probability is correct for simple family with no genes or traits")


def test_joint_probability_multiple_children():
    # Define a family with multiple children and no genes or traits
    family_data = {
        "mother": {"name": "mother", "mother": None, "father": None, "trait": None},
        "father": {"name": "father", "mother": None, "father": None, "trait": None},
        "child1": {"name": "child1", "mother": "mother", "father": "father", "trait": None},
        "child2": {"name": "child2", "mother": "mother", "father": "father", "trait": None},
        "child3": {"name": "child3", "mother": "mother", "father": "father", "trait": None}
    }

    # Test case where no one has a gene or trait
    one_gene = set()
    two_genes = set()
    have_trait = set()
    probability = joint_probability(family_data, one_gene, two_genes, have_trait)

    # The joint probability should be 1 since no gene or trait is present
    assert probability == 1, "Joint probability is incorrect for family with multiple children and no genes or traits"

    print("Test passed: Joint probability is correct for family with multiple children and no genes or traits")


def test_joint_probability_three_generation():
    # Define a three-generation family with no genes or traits
    three_generation_data = {
        "grandmother": {"name": "grandmother", "mother": None, "father": None, "trait": None},
        "grandfather": {"name": "grandfather", "mother": None, "father": None, "trait": None},
        "mother": {"name": "mother", "mother": "grandmother", "father": "grandfather", "trait": None},
        "father": {"name": "father", "mother": None, "father": None, "trait": None},
        "child": {"name": "child", "mother": "mother", "father": "father", "trait": None}
    }

    # Test case where no one has a gene or trait
    one_gene = set()
    two_genes = set()
    have_trait = set()
    probability = joint_probability(three_generation_data, one_gene, two_genes, have_trait)

    # The joint probability should be 1 since no gene or trait is present
    assert probability == 1, "Joint probability is incorrect for three-generation family with no genes or traits"

    print("Test passed: Joint probability is correct for three-generation family with no genes or traits")


if __name__ == "__main__":
    main()
    test_joint_probability_simple()
    test_joint_probability_multiple_children()
    test_joint_probability_three_generation()
