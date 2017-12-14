
# Importing our utilities
from _utils import *
from _fuzzy import *
from _preprocessing import *

def main(args):
    """
    Main method.

    Collection of all steps to classify emails, some steps may be commented out
    because they are only usefull for creating feature lists, word lists.

    Parameters
    ----------
    args : List
        Input arguments could be used in the future.

    """
    # features_path = "res/features/*.csv"
    # Currently using categories folder instead of featuers folder
    features_path = "res/categories/*.csv"
    datadump_path = "res/validationdump.csv"

    # Clean, tokenize, and rate all emails
    feature_lists, email_ratings = prepare_ratings(features_path, datadump_path)

    # Create a fuzzy logic instance
    classifier = prepare_classifier(feature_lists)

    classes = [
        "Basisinformatie",
        "Openbare Ruimte",
        "Parkeren",
        "Belastingen, Werk en Inkomen",
    ]

    result_printer = ResultPrinter(classes)

    # Classify first email using the email rating
    for (dept, email, rating) in [next(email_ratings) for _ in range(10)]:
        classification = classifier.classify(dept, email, list(rating.values()))
        result_printer.print(classification)

def prepare_ratings(features_path, datadump_path):
    """
    Preprocessor.

    Cleans, tokenizes, categorizes, and rates emails.

    Parameters
    -------
    features_path
        String containing the path to the folder containing feature csv's
    datadump_path
        String containing the path of the datadump csv

    Returns
    -------
    generator
        Containing a set for each email, each set containing the feature and
		it's calculated rating.

    """
    dumpreader = Dumpreader(datadump_path)
    rows = dumpreader.get_rows()
    rater = Rater(features_path)
    return rater.feature_lists, ((row[0], row[1], rater.rate_email(row[1])) for row in rows)

def prepare_classifier(feature_lists):
    """
    Classifier.

    Instance of a Classifier object that is able to classify emails by
    using the email feature vector as inputs.

    Returns
    -------
    Classifier
        Instance of a Classifier object that is able to classify emails by
        using the email feature vector as inputs.

    """
    # Inputs all look the same, |\/\/|, ranging inclusively from 0 to 1 for
    # each feature list.
    inputs = [

        Input(feature[0], (0, 1), [
            TrapezoidalMF("low", 0, 0, 0, 0.5),
            TriangularMF("med", 0, 0.5, 1),
            TrapezoidalMF("high", 0.5, 1, 1, 1)
        ]) for feature in feature_lists

    ]

    # The outputs are the department and priority of the email.
    outputs = [

        Output("department", (0, 3), [
            TrapezoidalMF("basisinformatie", 0, 0, 0, 1),
            TriangularMF("openbare ruimte", 0, 1, 2),
            TriangularMF("parkeren", 1, 2, 3),
            TrapezoidalMF("belasting, werk en inkomen", 2, 3, 3, 3),
        ])

    ]

    # Rules order: action agitation financial personal space tax traffic
	# note: action en agitation zijn alleen voor output "priority"
    rules = [

        Rule(1, ["high", "low", "low", "low"],
            "and", ["basisinformatie"]),
        Rule(2, ["low", "low", "high", "low"],
            "and", ["openbare ruimte"]),
        Rule(3, ["low", "low", "low", "high"],
            "and", ["parkeren"]),
        Rule(4, ["low", "high", "low", "low"],
            "and", ["belasting, werk en inkomen"])

    ]

    # Creating classifier
    classifier = Classifier(inputs, outputs, rules)
    classifier.reason()
    return classifier

class ResultPrinter:
    """
    Result Printer.

    Prints a classification object.
    """
    def __init__(self, classes):
        self.classes = classes
        self.format = "%27s / %27s / %1s"
        print(self.format % ("LABEL", "CLASS", "FEATURES"))
    def print(self, classification):
        print(
            self.format %
            (classification['label'],
            self.classes[classification['class']['department']],
            classification['ratings'])
        )


# Calls main method and passes first argument
if __name__ =='__main__': main(sys.argv)
